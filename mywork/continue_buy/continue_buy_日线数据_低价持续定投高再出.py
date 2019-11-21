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
        ('continue_sell_day',20),
        ('rsi_low',45),
        ('rsi_high',60),
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
        self.buy_lastdays_already = 0
        self.buy_money_already = self.params.buy_money_already
        self.buy_amount_once = self.params.buy_amount_once
        self.least_buy_money = self.buy_amount_once * self.params.least_buy_days
        self.target_returns = self.params.target_returns
        self.size_continue_sell = 0
        self.max_continue_buy_amount = 0
        self.max_continue_buy_days = 0
        self.sma_year = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=126)
        self.sma_month = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=30)
        self.rsi_quarter = bt.talib.RSI(self.datas[0], timeperiod=63)


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
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f,Size:%.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm,
                          order.executed.size))
                posValue = self.broker.getvalue() - self.broker.get_cash()
                if posValue == 0:
                    self.buy_money_already = 0
                else:
                    self.buy_money_already = self.buy_money_already - order.executed.value + order.executed.comm

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
        #1、买：上根bar收盘价 < 年均线 且 rsi值 < rsi_low
        #2、卖：上跟bar收盘价 > 月均线 且 rsi值 > rsi_high
        #3、其他时候观望
        if self.order:
            return

        posValue = self.broker.getvalue() - self.broker.get_cash()
        currentReturns = 0
        if self.buy_money_already > 0:
            currentReturns = (posValue - self.buy_money_already) / self.buy_money_already

        if self.dataclose[0] < self.sma_year[0] and self.rsi_quarter[0] < self.params.rsi_low:
            buy_size = math.floor(self.buy_amount_once / self.dataclose[0]*(1+0.05))
            self.getsizer().setsizing(buy_size)
            self.order = self.buy()

        if self.dataclose[0] > self.sma_month[0] \
                and self.rsi_quarter[0] > self.params.rsi_high \
                and self.broker.getposition(self.data0).size > 0 \
                and currentReturns > self.target_returns \
                and self.buy_lastdays_already > self.params.least_buy_days:
            self.max_continue_buy_amount = max(self.max_continue_buy_amount, self.buy_money_already)
            self.max_continue_buy_days = max(self.buy_lastdays_already, self.max_continue_buy_days)
            self.buy_lastdays_already = -1
            new_size  = math.floor(self.broker.getposition(self.data0).size / self.params.continue_sell_day)
            self.size_continue_sell = max(new_size, self.size_continue_sell)
            if self.size_continue_sell > self.broker.getposition(self.data0).size:
                self.size_continue_sell = self.broker.getposition(self.data0).size
            self.getsizer().setsizing(self.size_continue_sell)
            self.order = self.sell()
            self.buy_lastdays_already = -1
            self.log('today can sell, now buy_money_already = %.2f' %
                     (self.buy_money_already))

        self.buy_lastdays_already += 1

    def stop(self):
        print("最大连续投入金额为：{}".format(self.max_continue_buy_amount))
        print("最大连续买入天数为：{}".format(self.max_continue_buy_days))
        final_value = cerebro.broker.getvalue()
        returns = (final_value - self.max_continue_buy_amount) / self.max_continue_buy_amount
        print("最大连续投入金额：{}，期末市值：{}，回报率：{}".format(self.max_continue_buy_amount,final_value,returns))


if __name__ == '__main__':

    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/orcl-1995-2014.txt')
    datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/yhoo-1996-2014.txt')
    # datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/BTC-USD-1D-coinbase-converted-date.txt')
    # datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/COINBASE-BTCUSD-5M.txt')

    data =   bt.feeds.BacktraderCSVData(
        dataname=datapath,
        timeframe=bt.TimeFrame.Days,
        # fromdate=datetime.datetime(2015, 7, 20),
        # todate=datetime.datetime(2015, 10, 21, 21, 25, 0),
        reverse=False)
    cerebro.adddata(data)

    init_value = 10000000
    cerebro.broker.setcash(init_value)

    # Add a FixedSize sizer according to the stake
    # cerebro.addsizer(bt.sizers.FixedSize, stake=5)

    mycommission = 0.001
    cerebro.broker.setcommission(commission=mycommission)
    strats = cerebro.run(tradehistory=True)

    cerebro.plot()
    # cerebro.plot(start=datetime.date(2015, 7, 20), end=datetime.date(2015, 8, 1))
    # cerebro.plot(start=1, end=2400)
    # cerebro.plot(start=1201, end=2400)