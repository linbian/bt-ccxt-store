from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from backtrader.analyzers import TimeDrawDown
from backtrader.analyzers import DrawDown

import backtrader as bt
from tabulate import tabulate
import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

class trade_list(bt.Analyzer):

    def get_analysis(self):
        return self.trades


    def __init__(self):
        self.trades = []
        self.cumprofit = 0.0
        self.commission = self.strategy.broker.getcommissioninfo(self.strategy.datas[0]).p.commission
        self.inimoney = self.strategy.broker.getvalue()
        self.timeDrawdown = TimeDrawDown()
        self.drawDown = DrawDown()
        # self.valuecurvle = marketvaluecurvle()
        self.totalValues = []
        self.cashValues = []
        self.posValues = []
        self.totalValues.append(self.strategy.broker.getvalue())
        self.cashValues.append(self.strategy.broker.getvalue())
        self.posValues.append(0)
        self.yearInfo = {}
        self.monthInfo = {}

    def next(self):
        self.totalValues.append(self.strategy.broker.getvalue())
        self.cashValues.append(self.strategy.broker.get_cash())
        self.posValues.append(self.strategy.broker.getvalue() - self.strategy.broker.get_cash())
        tmpYear = str(self.strategy.datetime.datetime().year)
        tmpMonth = tmpYear + str(self.strategy.datetime.datetime().month)
        if tmpMonth not in self.monthInfo.keys():
            self.monthInfo[tmpMonth] = self.strategy.broker.getvalue()
        if tmpYear not in self.yearInfo.keys():
            self.yearInfo[tmpYear] = self.strategy.broker.getvalue()


    def notify_trade(self, trade):
        # print("self.commission=",self.commission)
        if trade.isclosed:
            brokervalue = self.strategy.broker.getvalue()

            dir = 'short'
            if trade.history[0].event.size > 0: dir = 'long'

            pricein = trade.history[len(trade.history)-1].status.price
            priceout = trade.history[len(trade.history)-1].event.price

            datein = bt.num2date(trade.history[0].status.dt)
            dateout = bt.num2date(trade.history[len(trade.history)-1].status.dt)
            if trade.data._timeframe >= bt.TimeFrame.Days:
                datein = datein.date()
                dateout = dateout.date()

            pcntchange = 100 * priceout / pricein - 100
            pnl = trade.history[len(trade.history)-1].status.pnlcomm
            pnlpcnt = 100 * pnl / brokervalue
            barlen = trade.history[len(trade.history)-1].status.barlen
            pbar = pnl / barlen
            self.cumprofit += pnl

            size = value = 0.0
            for record in trade.history:
                if abs(size) < abs(record.status.size):
                    size = record.status.size
                    value = record.status.value

            commission_in = self.commission * pricein * size
            commission_out = self.commission * priceout * size
            commission_trade = commission_in + commission_out
            money_buy = pricein * size + commission_in
            money_win = priceout * size - money_buy - commission_out
            money_before = brokervalue - money_win
            highest_in_trade = max(trade.data.high.get(ago=0, size=barlen+1))
            lowest_in_trade = min(trade.data.low.get(ago=0, size=barlen+1))
            hp = 100 * (highest_in_trade - pricein) / pricein
            lp = 100 * (lowest_in_trade - pricein) / pricein
            if dir == 'long':
                mfe = hp
                mae = lp
            if dir == 'short':
                mfe = -lp
                mae = -hp

            hp_money = size * (highest_in_trade - pricein)
            lp_money = size * (lowest_in_trade -  pricein)
            if dir == 'long':
                mfe_money = hp_money
                mae_money = lp_money
            if dir == 'short':
                mfe_money = -lp_money
                mae_money = -hp_money

            self.trades.append({'ref': trade.ref,
                                # 'ticker': trade.data._name,
                                'dir': dir,'size': size,
                                'datein': datein, 'pricein': pricein,
                                # 'commisionin':commission_in,
                                'dateout': dateout, 'priceout': priceout,
                                # 'commisionout':commission_out,
                                'commission_trade':commission_trade,
                                'money_use[+commissionin]':money_buy,
                                'money_before':money_before,
                                'money_win':money_win,
                                'money_after':brokervalue,
                                'mfe_money':mfe_money ,
                                'mae_money':mae_money,
                                # 'chng%': round(pcntchange, 2),
                                # 'pnl': pnl, 'pnl%': round(pnlpcnt, 2),
                                # 'size': size, 'value': value, 'cumpnl': self.cumprofit,
                                'nbars': barlen,
                                # 'pnl/bar': round(pbar, 2)
                                # 'mfe%': round(mfe, 2), 'mae%': round(mae, 2)
                                })

    def stop(self):
        # print (tabulate(self.trades, headers="keys"))

        money_arr = []
        money_lose = []
        money_win = []
        money_cost = []
        mfe_money = []
        mae_money = []
        continues_array_win = []
        continues_array_lose = []
        flag_last_win = 0
        continues_tmp_array = []
        bar_len = []
        bar_len_win = []
        bar_len_lose = []
        win_loss_arr_ratio = []
        win_loss_arr_ratio_for_total_value = []
        buy_money_arr_ratio = []
        for trade in self.trades:
            money_arr.append(trade["money_win"]) #该次交易赢或者输的金额
            money_cost.append(trade["commission_trade"]) #该次交易赢或者输的金额
            mfe_money.append(trade["mfe_money"])
            mae_money.append(trade["mae_money"])
            bar_len.append(trade["nbars"])
            win_loss_arr_ratio.append(trade["money_win"] / trade["money_use[+commissionin]"]) #盈亏金额占动用资金的比率，动用资金含买入手续费
            win_loss_arr_ratio_for_total_value.append(trade["money_win"] / trade["money_before"]) #盈亏金额占买入前总市值的比率
            buy_money_arr_ratio.append(trade["money_use[+commissionin]"] / trade["money_before"]) #动用资金【含买入手续费】占买入前总市值的比率
            if trade["money_win"] > 0:
                money_win.append(trade["money_win"])
                bar_len_win.append(trade["nbars"])
            else:
                # 记录损失交易相关信息
                money_lose.append(trade["money_win"])
                bar_len_lose.append(trade["nbars"])

            ## 统计连续盈利与损失信息
            if flag_last_win == 0 and trade["money_win"] > 0:
                continues_tmp_array.append(trade["money_win"])
                flag_last_win = 1
            elif flag_last_win == 0 and trade["money_win"] <= 0:
                continues_tmp_array.append(trade["money_win"])
                flag_last_win = -1
            elif flag_last_win == 1 and trade["money_win"] > 0:
                continues_tmp_array.append(trade["money_win"])
            elif flag_last_win == 1 and trade["money_win"] <= 0:
                continues_array_win.append(continues_tmp_array)
                continues_tmp_array = []
                continues_tmp_array.append(trade["money_win"])
                flag_last_win = -1
            elif flag_last_win == -1 and trade["money_win"] <= 0:
                continues_tmp_array.append(trade["money_win"])
            elif flag_last_win == -1 and trade["money_win"] > 0:
                continues_array_lose.append(continues_tmp_array)
                continues_tmp_array = []
                continues_tmp_array.append(trade["money_win"])
                flag_last_win = 1

        if flag_last_win == 1:
            continues_array_win.append(continues_tmp_array)
        elif flag_last_win == 0:
            continues_array_lose.append(continues_tmp_array)


        print("==========================================最终的账户信息========================================================")
        print()
        finalValue = self.strategy.broker.getvalue()
        finalCash =  self.strategy.broker.get_cash()
        finalPositionSize = self.strategy.broker.getposition(self.data0).size
        finalPositionPrice = self.strategy.broker.getposition(self.data0).price
        finalPositionValue = finalPositionSize * finalPositionPrice
        invest_return_money =  finalValue - self.inimoney
        invest_return_ratio = invest_return_money / self.inimoney
        table_header = ['账户初始资金', '当前总市值', '当前现金余额','当前仓位市值', '当前仓位','当前价格','总盈利金额','总回报率']
        table_data = [(self.inimoney,finalValue,finalCash,finalPositionValue,finalPositionSize,finalPositionPrice,invest_return_money,invest_return_ratio)]
        print(tabulate(table_data, headers=table_header, tablefmt='plain'))
        print()

        print("=======================该统计信息可能未统计最后一次买入的相关分析指标=========================================")
        print()

        ratio_win = len(money_win)/len(money_arr)
        avg_win = sum(money_win) / len(money_win)
        avg_lose = sum(money_lose) / len(money_lose)
        avg_win_lose = abs(avg_win / avg_lose)

        table_header = ["净利润总额","总盈利金额","总亏损金额","总交易手续费",
                        "交易胜率","交易次数","盈利交易次数","亏损交易次数",
                        "盈亏比","平均单笔盈利金额","平均单笔亏损金额","平均亏损或盈利金额/交易"]
        table_data = [(sum(money_arr),sum(money_win),sum(money_lose),sum(money_cost),
                       ratio_win*100,len(money_arr),len(money_win),len(money_lose),
                       abs(sum(money_win)/sum(money_lose)), avg_win, avg_lose, np.mean(money_arr))]
        print(tabulate(table_data, headers=table_header, tablefmt='plain'))

        table_header = ["交易胜率","平均盈亏比","数学期望",
                        "盈利交易标准差","平均单笔盈利金额","最大单笔盈利金额","最大/平均倍数",
                        "亏损金额标准差","平均单笔亏损金额","最大亏损金额","最大/平均倍数"]
        table_data = [(ratio_win,avg_win_lose,(1+avg_win_lose)*ratio_win-1,
                       np.std(money_win),np.mean(money_win),np.max(money_win),np.max(money_win)/np.mean(money_win),
                       np.std(money_lose),np.mean(money_lose),np.min(money_lose),np.min(money_lose)/np.mean(money_lose))]
        print(tabulate(table_data, headers=table_header, tablefmt='plain'))
        print()
        print("  备注：数学期望=（1+平均盈亏比）*交易胜率")
        print()

        print("=======================================扣除最大单笔盈利后的相关分析指标=========================================")
        print()
        avg_win_enhance = (sum(money_win) - max(money_win)) / (len(money_win)-1)
        ratio_win_enhance = (len(money_win)-1)/(len(money_arr)-1)
        table_header = ["对比名目","扣除前","扣除后",
                        "对比名目","扣除前","扣除后",
                        "对比名目","扣除前","扣除后"]
        table_data = [("净利润金额",sum(money_win),sum(money_win)-max(money_win),
                       "平均盈利金额",avg_win,avg_win_enhance,
                       "平均盈亏比",avg_win_lose,abs(avg_win_enhance / avg_lose)),
                      ("数学期望",(1+avg_win_lose)*ratio_win-1,(1+avg_win_enhance / avg_lose)*ratio_win_enhance-1,
                       "净利润总额",sum(money_arr),sum(money_arr)-max(money_win),
                       "平均亏损或盈利金额/交易",np.mean(money_arr),(sum(money_arr)-max(money_win))/(len(money_arr)-1))]
        print(tabulate(table_data, headers=table_header, tablefmt='plain'))
        print()

        print("========================================连续盈利与连续损失相关分析指标==========================================")
        # 连续盈利：最大连续盈利次数、最大连续盈利金额
        continue_max_times_win = 0
        continue_max_money_win = 0
        continue_times_win_array = []
        continue_money_win_array = []
        for continue_wins in continues_array_win:
            continue_times_win_array.append(len(continue_wins))
            continue_money_win_array.append(sum(continue_wins))
            if continue_max_times_win < len(continue_wins):
                continue_max_times_win = len(continue_wins)
                continue_max_money_win = sum(continue_wins)

        # 连续损失：最大连续损失次数、最大连续损失金额
        continue_max_times_lose = 0
        continue_max_money_lose = 0
        continue_times_lose_array = []
        continue_money_lose_array = []
        for continue_lose in continues_array_lose:
            continue_times_lose_array.append(len(continue_lose))
            continue_money_lose_array.append(sum(continue_lose))
            if continue_max_times_lose < len(continue_lose):
                continue_max_times_lose = len(continue_lose)
                continue_max_money_lose = sum(continue_lose)
        # print("连续盈利次数数组 =》",continue_times_win_array)
        # print("连续损失次数数组 =》",continue_times_lose_array)
        # print(self.timeDrawdown.get_analysis())
        # print(self.drawDown.get_analysis())
        table_header = ["最大连续盈利次数","最大连续盈利次数累计盈利金额","最大连续损失次数",
                        "最大连续损失次数累计金额","平均连续盈利次数","平均连续亏损次数","校验连续盈利次数与连续损失次数之和"]
        table_data = [(continue_max_times_win, continue_max_money_win, continue_max_times_lose,
                       continue_max_money_lose, np.mean(continue_times_win_array), np.mean(continue_times_lose_array), sum(continue_times_win_array)+sum(continue_times_lose_array))]
        print(tabulate(table_data, headers=table_header, tablefmt='plain'))

        print("=============================================持仓bar数相关分析指标=============================================")
        table_header = ["最大盈利持仓bar数","平均盈利持仓bar数","最小盈利持仓bar数",
                        "最大亏损持仓bar数","平均亏损持仓bar数","最小亏损持仓bar数",
                        "最大持仓bar数","平均持仓bar数","最小持仓bar数"]
        table_data = [(max(bar_len_win), np.mean(bar_len_win), min(bar_len_win),
                       max(bar_len_lose), np.mean(bar_len_lose), min(bar_len_lose),
                       max(bar_len), np.mean(bar_len), min(bar_len))]
        print(tabulate(table_data, headers=table_header, tablefmt='plain'))

        print("============================================（最大）回测相关分析指标===========================================")
        drawdown = self.drawDown.get_analysis()
        # print(drawdown['max'])
        # print(drawdown['max']['drawdown'])
        timedrawdown = self.timeDrawdown.get_analysis()
        # print(timedrawdown)
        table_header = ["最长持续回测bar数","最大持续回测金额","最大回测百分比","最大回测百分比对应的持续回测bar数"]
        table_data = [(drawdown["max"]["len"], drawdown["max"]["moneydown"], drawdown["max"]["drawdown"],timedrawdown["maxdrawdownperiod"])]
        print(tabulate(table_data, headers=table_header, tablefmt='plain'))

        ######################################################下面开始画图################################################
        ####   盈亏序列图
        figsize=(14, 20)
        figure, ax = plt.subplots(figsize=figsize)
        plt.subplot(3,1, 1)
        plt.bar(list(range(0,len(money_arr),1)),money_arr,color='orange')
        plt.xlabel('横轴：交易序列',fontproperties='SimHei',fontsize=10)
        plt.ylabel('纵轴：盈利/亏损金额',fontproperties='SimHei',fontsize=10)
        plt.title("交易盈亏序列图-全交易序列图")
        plt.subplot(3,1, 2)
        plt.bar(list(range(0,len(money_win),1)),money_win,color='orange')
        plt.xlabel('横轴：交易序列',fontproperties='SimHei',fontsize=10)
        plt.ylabel('纵轴：盈利/亏损金额',fontproperties='SimHei',fontsize=10)
        plt.title("交易盈亏序列图-盈利交易序列图")
        plt.subplot(3,1, 3)
        plt.bar(list(range(0,len(money_lose),1)),money_lose,color='orange')
        plt.xlabel('横轴：交易序列',fontproperties='SimHei',fontsize=10)
        plt.ylabel('纵轴：盈利/亏损金额',fontproperties='SimHei',fontsize=10)
        plt.title("交易盈亏序列图-亏损交易序列图")
        plt.savefig('./1-交易盈亏分析图.png')
        ##plt.show()


        ####   mfe与mar序列图
        total_length = len(money_arr)
        length_size = 100
        total_pic_num = math.ceil(total_length/length_size)
        figsize=(14, 5*(total_pic_num+1))
        width = 0.3
        figure, ax = plt.subplots(figsize=figsize)
        for pic_index in range(1,total_pic_num+1):
            plt.subplot(total_pic_num + 1,1, pic_index)
            begin_index = (pic_index-1)*length_size
            end_index = begin_index + length_size
            if total_pic_num == pic_index:
                end_index = total_length
            curren_final = money_arr[begin_index:end_index]
            curren_mfe = mfe_money[begin_index:end_index]
            curren_mae = mae_money[begin_index:end_index]

            x = list(range(0,len(curren_final),1))
            plt.bar(x,curren_final,color='orange',width=width, label='$final$')
            for i in range(len(x)):
                x[i] = x[i] + width
            plt.bar(x,curren_mfe,color='red',width=width, label='$mfe$')
            for i in range(len(x)):
                x[i] = x[i] + width
            plt.bar(x,curren_mae,color='green',width=width, label='$mae$')
            plt.title("潜在盈亏分析对比图-"+str(pic_index))
            plt.legend()

        plt.subplot(total_pic_num + 1,1, total_pic_num+1)
        x = list(range(0,len(money_arr),1))
        plt.bar(x,money_arr,color='orange',width=width, label='$final$')
        for i in range(len(x)):
            x[i] = x[i] + width
        plt.bar(x,mfe_money,color='red',width=width, label='$mfe$')
        for i in range(len(x)):
            x[i] = x[i] + width
        plt.bar(x,mae_money,color='green',width=width, label='$mae$')
        plt.title("潜在盈亏分析对比图-总图")
        plt.legend()
        plt.savefig('./2-最大潜在盈利与潜在亏分析图.png')
        ##plt.show()


        ####   连续盈利与连续亏损分析图
        figsize=(14, 10)
        figure, ax = plt.subplots(figsize=figsize)
        plt.subplot(2,2, 1)
        plt.bar(list(range(0,len(continue_money_win_array),1)),continue_money_win_array,color='orange')
        plt.hlines(np.mean(continue_money_win_array), 0, len(continue_money_win_array), color='blue')
        plt.ylabel('纵轴：连续盈利金额',fontproperties='SimHei',fontsize=10)
        plt.title("连续盈利金额图")
        plt.subplot(2,2, 2)
        plt.bar(list(range(0,len(continue_times_win_array),1)),continue_times_win_array,color='orange')
        plt.hlines(np.mean(continue_times_win_array), 0, len(continue_times_win_array), color='blue')
        plt.ylabel('纵轴：连续盈利次数',fontproperties='SimHei',fontsize=10)
        plt.title("连续盈利次数图")
        plt.subplot(2,2, 3)
        plt.bar(list(range(0,len(continue_money_lose_array),1)),continue_money_lose_array,color='orange')
        plt.hlines(np.mean(continue_money_lose_array), 0, len(continue_money_lose_array), color='blue')
        plt.ylabel('纵轴：连续亏损金额',fontproperties='SimHei',fontsize=10)
        plt.title("连续亏损金额图")
        plt.subplot(2,2, 4)
        plt.bar(list(range(0,len(continue_times_lose_array),1)),continue_times_lose_array,color='orange')
        plt.hlines(np.mean(continue_times_lose_array), 0, len(continue_times_lose_array), color='blue')
        plt.ylabel('纵轴：连续亏损次数',fontproperties='SimHei',fontsize=10)
        plt.title("连续亏损次数图")
        plt.savefig('./3-连续盈利与连续亏损分析图.png')
        ##plt.show()


        ####   持仓分析图
        figsize=(16, 16)
        figure, ax = plt.subplots(figsize=figsize)
        ax=figure.add_subplot(3,2, 1)
        ax.set_title('盈利交易持仓bar数箱型图')
        plt.boxplot(bar_len_win,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        ax=figure.add_subplot(3,2, 2)
        ax.set_title('盈利交易持仓时间分布图')
        sns.distplot(bar_len_win)
        ax=figure.add_subplot(3,2, 3)
        ax.set_title('亏损交易持仓bar数箱型图')
        plt.boxplot(bar_len_lose,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        ax=figure.add_subplot(3,2, 4)
        ax.set_title('亏损交易持仓bar数分布图')
        sns.distplot(bar_len_lose)
        ax=figure.add_subplot(3,2, 5)
        ax.set_title('交易持仓bar数箱型图')
        plt.boxplot(bar_len,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        ax=figure.add_subplot(3,2, 6)
        ax.set_title('交易持仓bar数分布图')
        sns.distplot(bar_len)
        plt.savefig('./4-交易持仓bar数分析图.png')
        ##plt.show()

        figsize=(14, 10)
        figure, ax = plt.subplots(figsize=figsize)
        plt.subplot(2,2, 1)
        plt.bar(list(range(0,len(money_arr),1)),money_arr,color='orange')
        plt.title("交易盈亏金额序列图")
        plt.subplot(2,2, 2)
        plt.bar(list(range(0,len(win_loss_arr_ratio),1)),win_loss_arr_ratio,color='orange')
        plt.title("交易盈亏/动用资金的比例序列图")
        plt.subplot(2,2, 3)
        plt.bar(list(range(0,len(win_loss_arr_ratio_for_total_value),1)),win_loss_arr_ratio_for_total_value,color='orange')
        plt.title("交易盈亏/买入前总市值序列图")
        plt.subplot(2,2, 4)
        plt.bar(list(range(0,len(buy_money_arr_ratio),1)),buy_money_arr_ratio,color='orange')
        plt.title("动用资金占买入前总市值的资金比例序列图")
        plt.savefig('./5-盈亏与资金比例分析图.png')
        ##plt.show()

        figsize=(14, 10)
        figure, ax = plt.subplots(figsize=figsize)
        plt.subplot(2,2, 1)
        plt.boxplot(money_win,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("盈利交易箱图")
        plt.subplot(2,2, 2)
        plt.boxplot(money_lose,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("亏损交易箱图")
        plt.subplot(2,2, 3)
        sns.distplot(money_win)
        plt.title("盈利交易分布图")
        plt.subplot(2,2, 4)
        sns.distplot(money_lose)
        plt.title("亏损交易分布图")
        plt.savefig('./6-盈亏金额分布分析图.png')

        # print(len(self.totalValues))
        # print(len(self.cashValues))
        # print(len(self.posValues))
        # print(len(self.strategy.datas[0]['da']))

        figsize=(14, 10)
        figure, ax = plt.subplots(figsize=figsize)
        plt.subplot(1,1, 1)
        plt.plot(range(0,len(self.totalValues)),self.totalValues,'r--',label="$totalValue$",color="red",linewidth=2)
        plt.plot(range(0,len(self.cashValues)),self.cashValues,'b--',label="$cashValues$")
        plt.plot(range(0,len(self.posValues)),self.posValues,'g--',label="$posValues$")
        plt.boxplot(money_win,sym='r*',vert=False,patch_artist=True,meanline=False,showmeans=True) #也可用plot.box()
        plt.title("资金曲线图")
        col_labels = ['col1','col2','col3']
        row_labels = ['row1','row2','row3']
        table_vals = [[11,12,13],[21,22,23],[28,29,30]]
        row_colors = ['red','gold','green']
        # my_table = plt.table(cellText=table_vals, colWidths=[0.1]*3,
        #              rowLabels=row_labels, colLabels=col_labels,
        #              rowColours=row_colors, colColours=row_colors,
        #              loc='best')
        your_table = plt.table(cellText=table_vals,colWidths=[0.1]*3,
                               colLabels=col_labels,colColours=row_colors,loc='best')
        plt.legend()
        plt.savefig('./7-资金曲线图.png')

        # print(self.yearInfo)
        # print(self.monthInfo)
        month_key = []
        month_win = []
        last_key = ''
        for key in self.monthInfo.keys():
            if last_key != '':
                month_key.append(last_key)
                month_win.append(self.monthInfo[key] - self.monthInfo[last_key])
            last_key = key
        month_win.append(self.strategy.broker.getvalue() - self.monthInfo[last_key])
        month_key.append(last_key)

        year_key = []
        year_win = []
        last_key = ''
        for key in self.yearInfo.keys():
            if last_key != '':
                year_key.append(last_key)
                year_win.append(self.yearInfo[key] - self.yearInfo[last_key])
            last_key = key
        year_win.append(self.strategy.broker.getvalue() - self.yearInfo[last_key])
        year_key.append(last_key)

        figsize=(14, 10)
        figure, ax = plt.subplots(figsize=figsize)
        plt.subplot(2,1, 1)
        plt.bar(month_key, month_win,color='orange')
        plt.title("月度盈亏分析图")
        plt.subplot(2,1, 2)
        plt.bar(year_key,year_win,color='orange')
        plt.title("年度盈亏分析图")
        plt.savefig('./8-月度与年度盈亏分析图.png')