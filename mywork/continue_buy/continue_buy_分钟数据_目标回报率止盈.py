from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math
import backtrader as bt


class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 22),
        ('buy_money_already',0),
        ('buy_amount_once',5000),
        ('least_buy_days',66),
        ('target_returns',0.2),
        ('continue_sell_day',10),

    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datetime.datetime()
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datalow = self.datas[0].low
        self.datahigh = self.datas[0].high

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.flag_continue_buy =  True
        self.flag_continue_sell =  False
        self.buy_money_already = self.params.buy_money_already
        self.buy_amount_once = self.params.buy_amount_once
        self.least_buy_money = self.buy_amount_once * self.params.least_buy_days
        self.target_returns = self.params.target_returns
        self.size_continue_sell = 0


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            # print(order)
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f,Size:%.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm,
                     order.executed.size))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.buy_money_already += order.executed.value + order.executed.comm
            else:  # Sell
                # self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f,Size:%.2f' %
                #          (order.executed.price,
                #           order.executed.value,
                #           order.executed.comm,
                #           order.executed.size))
                posValue = self.broker.getvalue() - self.broker.get_cash()
                if posValue == 0:
                    self.flag_continue_sell = False
                    self.flag_continue_buy = True
                    self.buy_money_already = 0

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        if self.order:
            return

        posValue = self.broker.getvalue() - self.broker.get_cash()
        currentReturns = 0
        if self.buy_money_already > 0:
            currentReturns = (posValue - self.buy_money_already) / self.buy_money_already

        buy_flag = True
        if currentReturns > self.target_returns \
                and self.buy_money_already > self.least_buy_money\
                and self.flag_continue_buy == True:
            buy_flag = False
            self.flag_continue_buy = False
            self.flag_continue_sell = True
            self.log('stop continue buy,now buy_money_already = %.2f' %
                     (self.buy_money_already))

        if buy_flag == True and self.flag_continue_buy ==  True:
            buy_size = math.floor(self.buy_amount_once / self.dataclose[0]*(1+0.05))
            self.getsizer().setsizing(buy_size)
            self.order = self.buy()


        if self.flag_continue_sell == True:
            new_size  = math.floor(self.broker.getposition(self.data0).size / self.params.continue_sell_day)
            self.size_continue_sell = max(new_size, self.size_continue_sell)
            if self.size_continue_sell > self.broker.getposition(self.data0).size:
                self.size_continue_sell = self.broker.getposition(self.data0).size
            self.getsizer().setsizing(self.size_continue_sell)
            self.order = self.sell()


if __name__ == '__main__':

    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/orcl-1995-2014.txt')
    # datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/BTC-USD-1D-coinbase-converted-date.txt')
    # datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/COINBASE-BTCUSD-5M.txt')

    data =   bt.feeds.BacktraderCSVData(
        dataname=datapath,
        # timeframe=bt.TimeFrame.Days,
        timeframe=bt.TimeFrame.Minutes,
        compression=5,
        # fromdate=datetime.datetime(2015, 7, 20),
        # todate=datetime.datetime(2015, 10, 21, 21, 25, 0),
        reverse=False)
    cerebro.adddata(data)

    # 合并为日线
    # cerebro.resampledata(data,
    #                              timeframe=bt.TimeFrame.Minutes,
    #                              compression=1440)
    init_value = 10000000
    cerebro.broker.setcash(init_value)

    # Add a FixedSize sizer according to the stake
    # cerebro.addsizer(bt.sizers.FixedSize, stake=5)

    mycommission = 0.001
    cerebro.broker.setcommission(commission=mycommission)
    strats = cerebro.run(tradehistory=True)
    final_value = cerebro.broker.getvalue()
    returns = (final_value - init_value) / init_value
    print("初始市值：{}，期末市值：{}，回报率：{}".format(init_value,final_value,returns))
    cerebro.plot()
    # cerebro.plot(start=datetime.date(2015, 7, 20), end=datetime.date(2015, 8, 1))
    # cerebro.plot(start=1, end=2400)
    # cerebro.plot(start=1201, end=2400)