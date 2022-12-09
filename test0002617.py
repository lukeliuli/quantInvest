##################################################################################
#####开始自己写1
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import datetime  # For datetime objects
import os.path  # To manage paths
import sys  # To find out the script name (in argv[0])
import pandas as pd
import backtrader as bt
import talib as ta
from backtrader.order import Order
#from backtrader_plotting import Bokeh
#from backtrader_plotting.schemes import Tradimo

###########################################################################################################################

# Create a Stratey


class MyStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # 做多/做空 订单 已提交/已执行 到/被代理 - 无事可做
            return

        # 检查订单是否已经完成
        # 注意：如果没有足够资金，代理可能拒绝订单
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        return

    def notify_trade(self, trade):

        if not trade.isclosed:
            return
        self.log('权益, 赢亏 %.2f, 总赢亏（含佣金） %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        #self.datas[0] ↔ self.data0 ↔ self.data
        #self.datas[X].lines[Y] ↔self.data[Y]
        #print(self.datas[0].lines.getlinealiases())
        #print(self.datas[0].lines.datetime[0])
        #index1 =self.datas[0].lines.datetime[0]
        #index2 = bt.num2date(index1)
        #print('self.datas[0].lines.datetime[0] ',index2)

        #print(" -1",self.datas[0].datetime.date(-1)," 0",self.datas[0].datetime.date(0))
        #print(" -1",self.data[-1]," 0",self.data[0])
        #print(" -1",self.datas[0].lines.close[-1]," 0",self.datas[0].lines.close[0])
        #print(" -1",self.datas[0].close[-1]," 0",self.datas[0].close[0])

        ##self.log('Close, %.2f,operation %f,macdZeros %f' % (self.dataclose[0],operation,macdZeros))
        #print('当前可用资金', self.broker.getcash())
        #print('当前总资产', self.broker.getvalue())
        #print('当前持仓量', self.broker.getposition(self.data).size)
        #print('当前持仓成本', self.broker.getposition(self.data).price)
        # 也可以直接获取持仓
        #print('当前持仓量', self.getposition(self.data).size)
        #print('当前持仓成本', self.getposition(self.data).price)
        # 日志输出收盘价数据

        index1 = self.datas[0].lines.datetime[0]
        index1 = bt.num2date(index1)
        index1 = pd.Timestamp(index1)
        operation = allDat_global.loc[index1]['operation']
        macdZeros = allDat_global.loc[index1]['macdZeros']
        sub2 = allDat_global.loc[index1]['sub2']
        sub2pct = allDat_global.loc[index1]['sub2pct']

        if macdZeros >= 3:
            self.log('下单买单, %.2f' % self.dataclose[0])
            # 跟踪创建的订单以避免第二个订单
            self.buy(size=100)

        if operation <= -2 and self.position:
            #self.order =self.sell()
            order = self.close()  # 平仓
            self.log("下单平仓单,%.2f" % self.dataclose[0])

        #放弃以下策略，原因是复杂度提高，但是收益提高2%
        #if sub2>0.01  and sub2pct>0:
        #    if operation==-3 and self.position:
        #        order =self.close()#平仓
        #        self.log("下单平仓单,%.2f" %self.dataclose[0])
        #else:
        #    if operation <=-2 and self.position:
        #         #self.order =self.sell()
        #        order =self.close()#平仓
        #        self.log("下单平仓单,%.2f" %self.dataclose[0])

        #self.log('Close, %.2f,operation %f,macdZeros %f' % (self.dataclose[0],operation,macdZeros))
        return
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###人工调试的第1个特征集合


def genFeatures1(df1, params):

    vCloses = df1['close']
    #print(vCloses.head(10))
    times = 4  # 如果是60分钟的数据需要一个加倍,每天4小时交易时间
    sma5 = ta.SMA(vCloses, 5*times)
    sma5pct = sma5.pct_change()
    sma10 = ta.SMA(vCloses, 10*times)
    sma10pct = sma10.pct_change()
    sma20 = ta.SMA(vCloses, 20*times)
    sma20pct = sma20.pct_change()

    sma30 = ta.SMA(vCloses, 30*times)
    sma30pct = sma30.pct_change()
    sma30pctpct = sma30pct.pct_change()

    sma2 = ta.SMA(vCloses, 2*times)
    sma2pct = sma2.pct_change()
    sma3 = ta.SMA(vCloses, 3*times)
    sma3pct = sma3.pct_change()

    sma5 = ta.SMA(vCloses, 5*times)
    sma5pct = sma5.pct_change()

    counter = 0
    zeros = pd.Series(index=sma10pct.index, data=[
                      0 for i in range(len(sma10pct))])
    flags = pd.Series(index=sma10pct.index, data=[
                      0 for i in range(len(sma10pct))])
    revertUps = pd.Series(index=sma10pct.index, data=[
                          0 for i in range(len(sma10pct))])
    revertDowns = pd.Series(index=sma10pct.index, data=[
                            0 for i in range(len(sma10pct))])

    revertUps5ma = pd.Series(index=sma10pct.index, data=[
                             0 for i in range(len(sma10pct))])
    revertDowns5ma = pd.Series(index=sma10pct.index, data=[
                               0 for i in range(len(sma10pct))])

    changeFlagDown = pd.Series(index=sma10pct.index, data=[
                               0 for i in range(len(sma10pct))])
    changeFlagUp = pd.Series(index=sma10pct.index, data=[
                             0 for i in range(len(sma10pct))])

    sub1 = pd.Series(index=sma10pct.index, data=[
                     0 for i in range(len(sma10pct))])

    max4mon = ta.MAX(vCloses, 4*21*times)  # 4month ,4*21*4
    min4mon = ta.MIN(vCloses, 4*21*times)  # 4month ,4*21*4

    operation = pd.Series(index=sma10pct.index, data=[
                          0 for i in range(len(sma10pct))])
    macdZeros = pd.Series(index=sma10pct.index, data=[
                          0 for i in range(len(sma10pct))])

    diff, dea, macdhist = ta.MACD(
        vCloses, fastperiod=12*times, slowperiod=26*times, signalperiod=9*times)
    diffpct = diff.pct_change()
    macdhistpct = macdhist.pct_change()
    lineSLOPE = ta.LINEARREG_SLOPE(vCloses, timeperiod=20*times)
    sma10diff = vCloses - sma10

    counter = 0
    lastIndex = 0
    sub1 = sma10-max4mon
    sub2 = ta.LINEARREG_SLOPE(sub1, timeperiod=60*times)
    sub2pct = ta.LINEARREG_SLOPE(sub2, timeperiod=4*times)

    for index, row in sma30pct.items():
        if counter == 0:
            counter = counter+1
            lastIndex = index
            continue

        ##################################################################
        ###趋势辨别,上升趋势后边界比较放松，因为上升趋势定卖点，卖点可以由其他特征共同决策
        ###趋势辨别,下降趋势后边界比较紧张，因为下降趋势定买点。买点尽可能接近拐点，以及中间减少甚至消除正跳变

        flag = 1 if lineSLOPE[index] > 0 else -1
        if flags[lastIndex] == 1 and (sma10pct[index] > -0.001 or lineSLOPE[index] > -0.01) and sma20pct[index] > 0:
            flag = 1

        if flags[lastIndex] == -1 and (sma10pct[index] < 0.001 or lineSLOPE[index] < 0.01):
            flag = -1

        ##################################################################
        ###波动辨别
        ##1.基于5ma变化,连续穿越5ma,露出为3ma,美锦为10ma
        if (flag == 1):
            revertUps5ma[index] = revertUps5ma[lastIndex]
        #上一时刻大于5ma线，下一时刻小于5ma线，上升阶段5ma反转标记次数+1
        if (flag == 1) and (vCloses[index] < sma5[index]) and (vCloses[lastIndex] > sma5[lastIndex]):
            revertUps5ma[index] = revertUps5ma[lastIndex]+1

        if (flag == -1):
            revertDowns5ma[index] = revertDowns5ma[lastIndex]
        #上一时刻小于于5ma线，下一时刻大于5ma线，下降阶段5ma反转标记次数+1
        if (flag == -1) and (vCloses[index] > sma10[index]) and (vCloses[lastIndex] < sma10[lastIndex]):
            revertDowns5ma[index] = revertDowns5ma[lastIndex]+1

        ##################################################################
        ###辨别卖操作,
        if(flag == 1):
            operation[index] = operation[lastIndex]

        #params['revertUps5maSell_1'] = 3
        if (flag == 1) and (revertUps5ma[index] >= params['revertUps5maSell_1']):
            operation[index] = -1

        #params['revertUps5maSell_2'] = 5
        #params['revertUps5maSell_3'] = 10
        if (flag == 1) and (revertUps5ma[index] >= params['revertUps5maSell_2']) and sub2[index] < 0.01:
            operation[index] = -2
        if (flag == 1) and (revertUps5ma[index] >= params['revertUps5maSell_3']) and sub2[index] > 0.01:
            operation[index] = -2

        if (macdhist[lastIndex] > 0) and (macdhist[index] < 0) and sub2[index] > 0:
            operation[index] = operation[index]-1

        ###辨别买操作,加权
        if (macdhist[index] < 0.3) and (macdhist[index] > 0) and (macdhist[lastIndex] > -0.3) and (macdhist[lastIndex] < 0):
            macdZeros[index] = 1

        if (macdZeros[index] == 1 and revertDowns5ma[index] >= params['revertDowns5maBuy_1']):
            macdZeros[index] = 2

        if(macdZeros[index] == 2) and (sub2[index] > -0.01):
            macdZeros[index] = 3

        #####################################################
        flags[index] = flag
        lastIndex = index

    #################################
    macdAdd2 = pd.Series(index=sma10pct.index, data=[
                         0 for i in range(len(sma10pct))])
    for index, row in macdZeros.items():
        ###macdadd操作
        macdAdd2[index] = macdAdd2[lastIndex]
        if macdZeros[index] == 1 and flags[index] == -1:
            macdAdd2[index] = macdAdd2[index]+1

        if (macdZeros[index] == 1 and macdAdd2[index] >= params['revertDowns5maBuy_2']):
            macdZeros[index] = 3

        if flags[index] > 0:
            macdAdd2[index] = 0

        lastIndex = index

    allDat = pd.concat([flags, lineSLOPE, sma10, sma10pct, vCloses, operation, revertUps5ma,
                        revertDowns5ma, macdhist, macdZeros, macdAdd2, max4mon, sub2, sub2pct], axis=1, sort=True)
    allDat.columns = ['flags', 'lineSLOPE', 'sma10', 'sma10pct', 'vCloses', 'operation', 'revertUps5ma',
                      'revertDowns5ma', 'macdhist', 'macdZeros', 'macdZerosAdd', 'max4mon', 'sub2', 'sub2pct']
    return allDat


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################

###########################################################################################################################


###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    df1 = pd.read_csv('美锦能源000723.csv', index_col=0, parse_dates=True)

    params = dict()
    params['revertDowns5maBuy_1'] = 7  # revertDown5ma
    params['revertDowns5maBuy_2'] = 3  # macdZerosAdd

    params['revertUps5maSell_1'] = 3
    # (revertUps5ma[index] >=params['revertUps5maSell_2']) and sub2[index]<0.01:
    params['revertUps5maSell_2'] = 5
    # (revertUps5ma[index] >=params['revertUps5maSell_2']) and sub2[index]>0.01:
    params['revertUps5maSell_3'] = 10

    allDat = genFeatures1(df1, params)
    #allDat.plot(linewidth=1,figsize=(15,15),subplots=True,title='ALL DATA')
    allDat_global = allDat

    allDat2 = pd.concat([allDat['flags']*10+10, allDat['sma10'], allDat['vCloses'], allDat['revertDowns5ma'],
                        allDat['revertUps5ma'], allDat['macdZeros'], allDat['macdZerosAdd'], allDat['flags']], axis=1, sort=True)
    allDat2.columns = ['flags', 'sma10', 'vCloses', 'revertDowns5ma',
                       'revertUps5ma', 'macdZeros', 'macdZerosAdd', 'flags']
    allDat2.plot(linewidth=1, figsize=(15, 15), subplots=True,
                 title='revertUps5ma,revertDowns5ma')

    allDat2.plot(linewidth=1, figsize=(35, 15),
                 title='revertUps5ma,revertDowns5ma')

    allDat2 = pd.concat([allDat['flags']*10+10, allDat['sma10'], allDat['vCloses'], allDat['operation']*10-10, allDat['macdZeros'],
                        allDat['sub2']*100, allDat['sub2pct']], axis=1)
    allDat2.columns = ['flags', 'sma10', 'vCloses',
                       'operation', 'macdZeros', 'sub2', 'sub2pct']
    allDat2.plot(linewidth=1, figsize=(15, 15),
                 subplots=True, title='max4mon,sub1,sub2')

    allDat2 = pd.concat([allDat['flags']*10+10, allDat['vCloses'], allDat['revertUps5ma'],
                        allDat['operation'], allDat['sub2']], axis=1, sort=True)
    allDat2.columns = ['flags', 'vCloses', 'revertUps5ma', 'operation', 'sub2']
    allDat2.plot(linewidth=1, figsize=(15, 15),
                 subplots=True, title='revertUps5ma')

    
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MyStrategy)
 
    data = bt.feeds.PandasData(dataname=df1,
                        fromdate = datetime.datetime(2020, 1, 2,10,30),
                        todate = datetime.datetime(2022, 12,2,15,0),
                        
                        )
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
 
    # Set our desired cash start
    cerebro.broker.setcash(10000)
    # 设定佣金
    cerebro.broker.setcommission(commission=0.003)
 
    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
 
    # Run over everything
    cerebro.run()
 
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Plot the result
    #b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    cerebro.plot()
  
