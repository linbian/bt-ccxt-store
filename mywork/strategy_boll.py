from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])

# Import the backtrader platform
import backtrader as bt
from tabulate import tabulate


# Create a Stratey
from mywork import myAnalyzer


class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 22),
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

        # Add a MovingAverageSimple indicator
        self.sma_min = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=60)

        # self.sma_max = bt.indicators.SimpleMovingAverage(
        #     self.datas[1], period=5)

        # Indicators for the plotting show
        self.boll = bt.indicators.BollingerBands(self.datas[0], period=self.params.maperiod)
        # bt.indicators.ExponentialMovingAverage(self.datas[0], period=self.params.maperiod)
        # bt.indicators.MACDHisto(self.datas[0])
        # rsi = bt.indicators.RSI(self.datas[0])
        # bt.indicators.ATR(self.datas[0], plot=False)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

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
        # Simply log the closing price of the series from the reference
        # self.log('Open, High, Low, Close => %.2f, %.2f, %.2f, %.2f' % (self.dataopen[0],self.datahigh[0],self.datalow[0],self.dataclose[0]))
        # self.log('DrawDown: %.2f' % self.stats.drawdown.drawdown[-1])
        # self.log('MaxDrawDown: %.2f' % self.stats.drawdown.maxdrawdown[-1])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        # print("(broker.value,position.cash,position.shares) ==> ",self.broker.getvalue(),self.broker.get_cash(),self.broker.getposition(self.data0).size*self.broker.getposition(self.data0).price)
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            # if self.dataclose[0] > self.sma[0]:
            if self.dataclose[0] > self.boll.top[0] and self.dataclose[-1] < self.boll.top[-1]:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.getsizer().setsizing(10)
                self.order = self.buy()

        else:
            if self.dataclose[0] < self.boll.bot[0] and self.dataclose[-1] > self.boll.bot[-1]:
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose[0])

                # Keep track of the created order to avoid a 2nd order
                self.getsizer().setsizing(10)
                self.order = self.sell()


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, '../datas/orcl-1995-2014.txt')
    # datapath = os.path.join(modpath, '../datas/BTC-USD-1D-coinbase-converted-date.txt')
    datapath = os.path.join(modpath, '../datas/COINBASE-BTCUSD-5M.txt')

    # Create a Data Feed
    # data = bt.feeds.YahooFinanceCSVData(
    data =   bt.feeds.BacktraderCSVData(
        dataname=datapath,
        timeframe=bt.TimeFrame.Minutes,
        compression=5,
        fromdate=datetime.datetime(2015, 7, 20),
        todate=datetime.datetime(2015, 10, 21, 21, 25, 0),
        reverse=False)

    # data =   bt.feeds.BacktraderCSVData(
    #     dataname=datapath,
    #     timeframe=bt.TimeFrame.Days,
    #     compression=1,
    #     reverse=False)

    cerebro.adddata(data)

    # Set our desired cash start
    cerebro.broker.setcash(10000.0)

    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake=5)

    # Set the commission
    mycommission = 0.001
    cerebro.broker.setcommission(commission=mycommission)


    # 添加性能分析器
    # cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio',timeframe=bt.TimeFrame.Minutes, compression=5)
    cerebro.addanalyzer(bt.analyzers.trade_list, _name='trade_list')

    # 添加观察者
    # cerebro.addobserver(bt.observers.DrawDown)

    # Run over everything
    strats = cerebro.run(tradehistory=True)

    # Plot the result
    cerebro.plot()