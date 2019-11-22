from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import math
import backtrader as bt
import time
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns

class TestStrategy(bt.Strategy):
    params = (
        ("rsi_period_1",10),
        ("rsi_period_2",20),
        ("rsi_period_3",40),
        ("rsi_period_4",60),
        ("rsi_period_5",80),
        ("rsi_period_6",100),
        ("rsi_period_7",120),
        ("rsi_period_8",150),
        ("rsi_period_9",180),
        ("rsi_period_10",210),
        ("rsi_period_11",250),
        ("rsi_period_12",300),
        ("rsi_period_13",350),
        ("rsi_period_14",400),
        ("rsi_period_15",500),
    )

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datalow = self.datas[0].low
        self.datahigh = self.datas[0].high

        self.rsi_1 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_1)
        self.rsi_2 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_2)
        self.rsi_3 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_3)
        self.rsi_4 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_4)
        self.rsi_5 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_5)
        self.rsi_6 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_6)
        self.rsi_7 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_7)
        self.rsi_8 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_8)
        self.rsi_9 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_9)
        self.rsi_10 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_10)
        self.rsi_11 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_11)
        self.rsi_12 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_12)
        self.rsi_13 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_13)
        self.rsi_14 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_14)
        self.rsi_15 = bt.talib.RSI(self.datas[0], timeperiod=self.params.rsi_period_15)
        self.array_rsi_1 = []
        self.array_rsi_2 = []
        self.array_rsi_3 = []
        self.array_rsi_4 = []
        self.array_rsi_5 = []
        self.array_rsi_6 = []
        self.array_rsi_7 = []
        self.array_rsi_8 = []
        self.array_rsi_9 = []
        self.array_rsi_10 = []
        self.array_rsi_11 = []
        self.array_rsi_12 = []
        self.array_rsi_13 = []
        self.array_rsi_14 = []
        self.array_rsi_15 = []


    def next(self):
        self.array_rsi_1.append(self.rsi_1[0])
        self.array_rsi_2.append(self.rsi_2[0])
        self.array_rsi_3.append(self.rsi_3[0])
        self.array_rsi_4.append(self.rsi_4[0])
        self.array_rsi_5.append(self.rsi_5[0])
        self.array_rsi_6.append(self.rsi_6[0])
        self.array_rsi_7.append(self.rsi_7[0])
        self.array_rsi_8.append(self.rsi_8[0])
        self.array_rsi_9.append(self.rsi_9[0])
        self.array_rsi_10.append(self.rsi_10[0])
        self.array_rsi_11.append(self.rsi_11[0])
        self.array_rsi_12.append(self.rsi_12[0])
        self.array_rsi_13.append(self.rsi_13[0])
        self.array_rsi_14.append(self.rsi_14[0])
        self.array_rsi_15.append(self.rsi_15[0])

    def stop(self):
        # print(self.array_rsi_1)
        figsize=(30, 25)
        figure, ax = plt.subplots(figsize=figsize)
        plt.subplot(15,2, 1)
        plt.boxplot(self.array_rsi_1,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_1(period="+str(self.params.rsi_period_1)+")")
        plt.subplot(15,2, 2)
        sns.distplot(self.array_rsi_1)
        plt.title("rsi_1(period="+str(self.params.rsi_period_1)+")")

        plt.subplot(15,2, 3)
        plt.boxplot(self.array_rsi_2,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_2(period="+str(self.params.rsi_period_2)+")")
        plt.subplot(15,2, 4)
        sns.distplot(self.array_rsi_2)
        plt.title("rsi_2(period="+str(self.params.rsi_period_2)+")")

        plt.subplot(15,2, 5)
        plt.boxplot(self.array_rsi_3,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_3(period="+str(self.params.rsi_period_3)+")")
        plt.subplot(15,2, 6)
        sns.distplot(self.array_rsi_3)
        plt.title("rsi_3(period="+str(self.params.rsi_period_3)+")")

        plt.subplot(15,2, 7)
        plt.boxplot(self.array_rsi_4,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_4(period="+str(self.params.rsi_period_4)+")")
        plt.subplot(15,2, 8)
        sns.distplot(self.array_rsi_4)
        plt.title("rsi_4(period="+str(self.params.rsi_period_4)+")")

        plt.subplot(15,2, 9)
        plt.boxplot(self.array_rsi_5,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_5(period="+str(self.params.rsi_period_5)+")")
        plt.subplot(15,2, 10)
        sns.distplot(self.array_rsi_5)
        plt.title("rsi_5(period="+str(self.params.rsi_period_5)+")")

        plt.subplot(15,2, 11)
        plt.boxplot(self.array_rsi_6,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_6(period="+str(self.params.rsi_period_6)+")")
        plt.subplot(15,2, 12)
        sns.distplot(self.array_rsi_6)
        plt.title("rsi_6(period="+str(self.params.rsi_period_6)+")")

        plt.subplot(15,2, 13)
        plt.boxplot(self.array_rsi_7,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_7(period="+str(self.params.rsi_period_7)+")")
        plt.subplot(15,2, 14)
        sns.distplot(self.array_rsi_7)
        plt.title("rsi_7(period="+str(self.params.rsi_period_7)+")")

        plt.subplot(15,2, 15)
        plt.boxplot(self.array_rsi_8,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_8(period="+str(self.params.rsi_period_8)+")")
        plt.subplot(15,2, 16)
        sns.distplot(self.array_rsi_8)
        plt.title("rsi_8(period="+str(self.params.rsi_period_8)+")")

        plt.subplot(15,2, 17)
        plt.boxplot(self.array_rsi_9,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_9(period="+str(self.params.rsi_period_9)+")")
        plt.subplot(15,2, 18)
        sns.distplot(self.array_rsi_9)
        plt.title("rsi_9(period="+str(self.params.rsi_period_9)+")")

        plt.subplot(15,2, 19)
        plt.boxplot(self.array_rsi_10,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_10(period="+str(self.params.rsi_period_10)+")")
        plt.subplot(15,2, 20)
        sns.distplot(self.array_rsi_10)
        plt.title("rsi_10(period="+str(self.params.rsi_period_10)+")")

        plt.subplot(15,2, 21)
        plt.boxplot(self.array_rsi_11,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_11(period="+str(self.params.rsi_period_11)+")")
        plt.subplot(15,2, 22)
        sns.distplot(self.array_rsi_11)
        plt.title("rsi_11(period="+str(self.params.rsi_period_11)+")")

        plt.subplot(15,2, 23)
        plt.boxplot(self.array_rsi_12,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_12(period="+str(self.params.rsi_period_12)+")")
        plt.subplot(15,2, 24)
        sns.distplot(self.array_rsi_12)
        plt.title("rsi_12(period="+str(self.params.rsi_period_12)+")")

        plt.subplot(15,2, 25)
        plt.boxplot(self.array_rsi_13,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_13(period="+str(self.params.rsi_period_13)+")")
        plt.subplot(15,2, 26)
        sns.distplot(self.array_rsi_13)
        plt.title("rsi_13(period="+str(self.params.rsi_period_13)+")")

        plt.subplot(15,2, 27)
        plt.boxplot(self.array_rsi_14,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_14(period="+str(self.params.rsi_period_14)+")")
        plt.subplot(15,2, 28)
        sns.distplot(self.array_rsi_14)
        plt.title("rsi_14(period="+str(self.params.rsi_period_14)+")")

        plt.subplot(15,2, 29)
        plt.boxplot(self.array_rsi_15,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("rsi_15(period="+str(self.params.rsi_period_15)+")")
        plt.subplot(15,2, 30)
        sns.distplot(self.array_rsi_15)
        plt.title("rsi_15(period="+str(self.params.rsi_period_15)+")")

        plt.savefig('./rsi分析图.png')



if __name__ == '__main__':
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    # datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/BTC-USD-1D-coinbase-converted-date.data')
    datapath = os.path.join(modpath, 'F:/git_repo/backtrader-ccxt/datas/BTC-USD-1H-coinbase-converted-datetime.data')
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    data =   bt.feeds.BacktraderCSVData(
        dataname=datapath,
        timeframe=bt.TimeFrame.Days,
        # timeframe=bt.TimeFrame.Minutes,
        # compression=1,
        # fromdate=datetime.datetime(2015, 7, 20),
        # todate=datetime.datetime(2015, 10, 21, 21, 25, 0),
        reverse=False)
    cerebro.adddata(data)

    init_value = 5000
    cerebro.broker.setcash(init_value)
    mycommission = 0.001
    cerebro.broker.setcommission(commission=mycommission)
    strats = cerebro.run(tradehistory=True)
    # cerebro.plot()