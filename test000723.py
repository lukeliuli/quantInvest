##################################################################################
#####开始用全局优化
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
import pyfolio as pf
import warnings
warnings.filterwarnings('ignore')
import math
########################################################################################################################### 

# Create a Stratey
class MyStrategy(bt.Strategy):
    params=(('printlog',False),
            ('allDat_global',None))
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        if self.params.printlog == True:
            print('%s, %s' % (dt.isoformat(), txt))
 
    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # To keep track of pending orders
        self.allDat_global = self.params.allDat_global
        
    

 
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
        self.log('权益, 赢亏 %.2f, 总赢亏（含佣金） %.2f' %(trade.pnl, trade.pnlcomm))
       
                 
                 
    def next(self):
      
        allDat_global = self.allDat_global
        index1 =self.datas[0].lines.datetime[0]
        index1 = bt.num2date(index1)
        index1 = pd.Timestamp(index1)
        operation=allDat_global.loc[index1]['operation']
        macdZeros=allDat_global.loc[index1]['macdZeros']
        sub2=allDat_global.loc[index1]['sub2']
        sub2pct=allDat_global.loc[index1]['sub2pct']
        
        
        if macdZeros>=3:
            self.log('下单买单, %.2f' % self.dataclose[0])
                    # 跟踪创建的订单以避免第二个订单
            order_value = self.broker.get_cash()*0.80
            order_amount = math.floor(order_value/self.dataclose[0]/100)*100
            #print("order_value: %.2f, order_amount: %.2f" %(order_value,order_amount))
            self.order = self.buy(size=order_amount)

            
        if operation <=-2 and self.position:
                 #self.order =self.sell()
                order =self.close()#平仓
                self.log("下单平仓单,%.2f" %self.dataclose[0])
                
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
def genFeatures1(df1,params):
    
    vCloses = df1['close']
    maChoice = params['ma']
    #print(vCloses.head(10))
    times =4;#如果是60分钟的数据需要一个加倍,每天4小时交易时间
    smaNow = ta.SMA(vCloses,maChoice*times)
    smaNowpct = smaNow.pct_change()
    
    sma10 = ta.SMA(vCloses,10*times)
    sma10pct = sma10.pct_change()
    
    sma20 = ta.SMA(vCloses,20*times)
    sma20pct = sma20.pct_change()

    sma30 = ta.SMA(vCloses,30*times)
    sma30pct = sma30.pct_change()
    sma30pctpct = sma30pct.pct_change()

   


    counter = 0
    zeros = pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    flags = pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    revertUps=pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    revertDowns= pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])

    revertUps5ma=pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    revertDowns5ma= pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])

    changeFlagDown= pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    changeFlagUp= pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])

    sub1 = pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    

    max4mon = ta.MAX(vCloses,4*21*times)#4month ,4*21*4
    min4mon = ta.MIN(vCloses,4*21*times)#4month ,4*21*4

    operation= pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    macdZeros= pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    
    
    
    diff, dea,macdhist = ta.MACD(vCloses, fastperiod=12*times, slowperiod=26*times, signalperiod=9*times)
    diffpct = diff.pct_change()
    macdhistpct = macdhist.pct_change()
    lineSLOPE = ta.LINEARREG_SLOPE(vCloses, timeperiod=20*times)

    
    counter = 0
    lastIndex = 0
    sub1= sma10-max4mon
    sub2 = ta.LINEARREG_SLOPE(sub1, timeperiod=60*times) 
    sub2pct = ta.LINEARREG_SLOPE(sub2, timeperiod=4*times) 
  
    for index, row in sma30pct.items():
        if counter ==0:
            counter= counter+1
            lastIndex = index
            continue
        
  

        ##################################################################    
        ###趋势辨别,上升趋势后边界比较放松，因为上升趋势定卖点，卖点可以由其他特征共同决策
        ###趋势辨别,下降趋势后边界比较紧张，因为下降趋势定买点。买点尽可能接近拐点，以及中间减少甚至消除正跳变

      
        flag =  1 if lineSLOPE[index] > 0 else -1
        if flags[lastIndex] == 1 and (sma10pct[index]>-0.001 or lineSLOPE[index]>-0.01) and sma20pct[index]>0:
            flag = 1


        if flags[lastIndex] == -1 and (sma10pct[index]<0.001 or lineSLOPE[index]<0.01):
            flag = -1






        ##################################################################    
        ###波动辨别
        ##1.基于5ma变化,连续穿越5ma,露出为3ma,美锦为10ma。以前固定是5ma,现在改为变化可配置的smaNow了
        if (flag == 1): 
                revertUps5ma[index]=revertUps5ma[lastIndex]  
        #上一时刻大于5ma线，下一时刻小于5ma线，上升阶段5ma反转标记次数+1
        if (flag == 1) and (vCloses[index]<smaNow[index]) and (vCloses[lastIndex]>smaNow[lastIndex]):
                revertUps5ma[index]=revertUps5ma[lastIndex]+1     

        if (flag == -1): 
                revertDowns5ma[index]=revertDowns5ma[lastIndex]
        #上一时刻小于于5ma线，下一时刻大于5ma线，下降阶段5ma反转标记次数+1
        if (flag == -1) and(vCloses[index]>smaNow[index]) and (vCloses[lastIndex]<smaNow[lastIndex]):
                revertDowns5ma[index]=revertDowns5ma[lastIndex]+1


        ##################################################################
        ###辨别卖操作,
        if(flag == 1):
            operation[index] =  operation[lastIndex]
        

        #params['revertUps5maSell_1'] = 3
        if (flag ==  1) and (revertUps5ma[index] >=params['revertUps5maSell_1']):
                operation[index] = -1
                
        #params['revertUps5maSell_2'] = 5
        #params['revertUps5maSell_3'] = 10
        if (flag ==  1) and (revertUps5ma[index] >=params['revertUps5maSell_2']) and sub2[index]<0.01:
            operation[index] = -2
        if (flag ==  1) and (revertUps5ma[index] >=params['revertUps5maSell_3']) and sub2[index]>0.01:
            operation[index] = -2

       
        if (macdhist[lastIndex]>0) and (macdhist[index]<0) and sub2[index]>0:
                    operation[index] =operation[index]-1

        ###辨别买操作,加权
        if (macdhist[index]<0.3) and (macdhist[index]>0) and (macdhist[lastIndex]>-0.3) and (macdhist[lastIndex]<0):
                macdZeros[index] = 1
        
        if ( macdZeros[index] ==1  and revertDowns5ma[index] >= params['revertDowns5maBuy_1']):
                macdZeros[index] = 2       
 

        
        
       




        if(macdZeros[index] == 2) and (sub2[index] >-0.01):
            macdZeros[index] = 3
        

        
        #####################################################
        flags[index] =  flag
        lastIndex = index
        
    #################################  
    macdAdd2 = pd.Series(index=sma10pct.index,data = [0 for i in range(len(sma10pct))])
    for index, row in macdZeros.items():
         ###macdadd操作
        macdAdd2[index] = macdAdd2[lastIndex]
        if macdZeros[index] ==1 and flags[index] == -1:
            macdAdd2[index] = macdAdd2[index]+1
        
        if (macdZeros[index] == 1 and macdAdd2[index] >= params['revertDowns5maBuy_2']):
               macdZeros[index] = 3     
                
        if flags[index] >0:
            macdAdd2[index] = 0
        
        lastIndex = index
    
    
    allDat = pd.concat([flags,lineSLOPE,sma10,sma10pct,vCloses,operation,revertUps5ma,\
                  revertDowns5ma,macdhist,macdZeros,macdAdd2,max4mon,sub2,sub2pct], axis=1,sort=True)
    allDat.columns = ['flags','lineSLOPE','sma10','sma10pct','vCloses','operation','revertUps5ma',\
                  'revertDowns5ma','macdhist','macdZeros','macdZerosAdd','max4mon','sub2','sub2pct']
    return allDat
 
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################
###########################################################################################################################    
import pyfolio as pf
 
def runBtOnce(X):
    # Create a cerebro entity
      # Create a Data Feed
    # 本地数据，笔者用Wind获取的东风汽车数据以csv形式存储在本地。
    # parase_dates = True是为了读取csv为dataframe的时候能够自动识别datetime格式的字符串，big作为index
    # 注意，这里最后的pandas要符合backtrader的要求的格式
    df1 = pd.read_csv('美锦能源000723.csv', index_col=0, parse_dates=True)
    
    params =dict()
    if X == None:
        params['revertDowns5maBuy_1'] = 7 #revertDown5ma
        params['revertDowns5maBuy_2'] = 3 #macdZerosAdd
        params['revertUps5maSell_1'] =3 #
        params['revertUps5maSell_2'] =5 #(revertUps5ma[index] >=params['revertUps5maSell_2']) and sub2[index]<0.01:
        params['revertUps5maSell_3'] =10#(revertUps5ma[index] >=params['revertUps5maSell_2']) and sub2[index]>0.01:
        params['ma'] =5
    else:
        params = X
    
    allDat =  genFeatures1(df1,params)
    #allDat.plot(linewidth=1,figsize=(15,15),subplots=True,title='ALL DATA')
    
  
    
    '''   
    allDat2 = pd.concat([allDat['flags']*10+10,allDat['sma10'],allDat['vCloses'],allDat['revertDowns5ma'],allDat['revertUps5ma'],allDat['macdZeros'],allDat['macdZerosAdd']\
                        ,allDat['flags']],axis=1,sort=True)
    allDat2.columns = ['flags','sma10','vCloses','revertDowns5ma','revertUps5ma','macdZeros','macdZerosAdd','flags']
    allDat2.plot(linewidth=1,figsize=(15,15),subplots=True,title='revertUps5ma,revertDowns5ma')
    
    allDat2.plot(linewidth=1,figsize=(35,15),title='revertUps5ma,revertDowns5ma')
    
    allDat2 = pd.concat([allDat['flags']*10+10,allDat['sma10'],allDat['vCloses'],allDat['operation']*10-10,allDat['macdZeros'],\
                        allDat['sub2']*100,allDat['sub2pct']],axis=1)
    allDat2.columns = ['flags','sma10','vCloses','operation','macdZeros','sub2','sub2pct']
    allDat2.plot(linewidth=1,figsize=(15,15),subplots=True,title='max4mon,sub1,sub2')
    
    
    allDat2 = pd.concat([allDat['flags']*10+10,allDat['vCloses'],allDat['revertUps5ma'],allDat['operation'],allDat['sub2']],axis=1,sort=True)
    allDat2.columns = ['flags','vCloses','revertUps5ma','operation','sub2']
    allDat2.plot(linewidth=1,figsize=(15,15),subplots=True,title='revertUps5ma')
    
    '''
    
    
    
    
  
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MyStrategy,allDat_global = allDat)
 
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
 
    cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='PositionsValue',cash=True)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown',fund=False)
    # Print out the starting conditions
    print('\n Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
 
    # Run over everything
    cerebro.run()
 
    
    #print("--------------- DrawDown 回撤 -----------------")
    tmp = strat.analyzers.DrawDown.get_analysis()
    max_moneyDown = tmp['max']['moneydown']
    
    #print("--------------- PositionsValue 账户股票价值-----------------")
    #print(strat.analyzers.PositionsValue.get_analysis())
    tmp = strat.analyzers.PositionsValue.get_analysis()
    dfTmp = pd.DataFrame.from_dict(tmp,orient='index')
    dfTmp.columns = ['PositionsValue','cash']
    dfTmp['PositionsValue+cash'] = dfTmp['PositionsValue']+dfTmp['cash']
    #dfTmp.plot()
   
    maxloss = 10000-dfTmp['PositionsValue+cash'].min()
    finalValue = cerebro.broker.getvalue()-10000
    rvl =  finalValue-max_moneyDown
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('max_moneyDown: %.2f,maxLoss %.2f,finalValue %.2f, finalValue-max_moneyDown:%.2f' %(max_moneyDown,maxloss,finalValue,rvl))
    return rvl

def runBtOnceAndShow(params):
    # Create a cerebro entity
      # Create a Data Feed
    # 本地数据，笔者用Wind获取的东风汽车数据以csv形式存储在本地。
    # parase_dates = True是为了读取csv为dataframe的时候能够自动识别datetime格式的字符串，big作为index
    # 注意，这里最后的pandas要符合backtrader的要求的格式
    df1 = pd.read_csv('美锦能源000723.csv', index_col=0, parse_dates=True)
    
    if params == None:
        return None
   
    
    allDat =  genFeatures1(df1,params)   
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MyStrategy,allDat_global = allDat)
    data = bt.feeds.PandasData(dataname=df1,
                        fromdate = datetime.datetime(2020, 1, 2,10,30),
                        todate = datetime.datetime(2022, 12,2,15,0),              
                        )
    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    # Set our desired cash start
    cerebro.broker.setcash(10000)
    cerebro.broker.set_slippage_perc(0.01)
    # 设定佣金
    cerebro.broker.setcommission(commission=0.003)
    # Print out the starting conditions
    print('\n Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
 
     # Run over everything
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='AnnualReturn')
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.003, annualize=True, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')
    cerebro.addanalyzer(bt.analyzers.Calmar, _name='Calmar')
    cerebro.addanalyzer(bt.analyzers.PositionsValue, _name='PositionsValue',cash=True)
    cerebro.addanalyzer(bt.analyzers.PyFolio, _name='pyfolio')
    strats= cerebro.run()
    
    strat = strats[0]

    print("--------------- AnnualReturn -----------------")
    print(strat.analyzers.AnnualReturn.get_analysis())
    print("--------------- SharpeRatio -----------------")
    print(strat.analyzers.SharpeRatio.get_analysis())
    print("--------------- DrawDown -----------------")
    print(strat.analyzers.DrawDown.get_analysis())
    tmp = strat.analyzers.DrawDown.get_analysis()
    max_moneyDown = tmp['max']['moneydown']
    #print("--------------- Calmar -----------------")
    #print(strat.analyzers.Calmar.get_analysis())
    #print("--------------- GrossLeverage -----------------")
    #print(strat.analyzers.GrossLeverage.get_analysis()
    
    print("--------------- PositionsValue 账户股票价值-----------------")
    #print(strat.analyzers.PositionsValue.get_analysis())
    tmp = strat.analyzers.PositionsValue.get_analysis()
    dfTmp = pd.DataFrame.from_dict(tmp,orient='index')
    dfTmp.columns = ['PositionsValue','cash']
    dfTmp['PositionsValue+cash'] = dfTmp['PositionsValue']+dfTmp['cash']
    dfTmp.plot()
    print('\n max \n',dfTmp.max(),'\n min \n',dfTmp.min())
    print('\n 最大亏损%:',(10000-dfTmp['PositionsValue+cash'].min())/100)
    
    
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()
    pf.create_full_tear_sheet(returns) 
    # Plot the result
    #b = Bokeh(style='bar', plot_mode='single', scheme=Tradimo())
    cerebro.plot()
    return cerebro.broker.getvalue()-10000
########################################################################################################    
########################################################################################################
from scipy.optimize import dual_annealing,basinhopping,differential_evolution

def objective(x):
    
    #params['revertDowns5maBuy_1'] = 7 #revertDown5ma，穿过ma线的次数，在下降阶段
    #params['revertDowns5maBuy_2'] = 3 #macdZerosAdd,macd累计出现次数，在下降阶段
    #params['revertUps5maSell_1'] =3 #  卖标志为-1
    #params['revertUps5maSell_2'] =5 #(revertUps5ma[index] >=params['revertUps5maSell_2']) and sub2[index]<0.01:卖标志为-2
    #params['revertUps5maSell_3'] =10#(revertUps5ma[index] >=params['revertUps5maSell_2']) and sub2[index]>0.01:卖标志为-2
    
    revertDowns5maBuy_1,revertDowns5maBuy_2, revertUps5maSell_1,revertUps5maSell_2,revertUps5maSell_3,ma  = x
    
    params =dict()
    params['revertDowns5maBuy_1'] = round(revertDowns5maBuy_1) 
    params['revertDowns5maBuy_2'] = round(revertDowns5maBuy_2)
    params['revertUps5maSell_1'] = round(revertUps5maSell_1)
    params['revertUps5maSell_2'] = round(revertUps5maSell_2)
    params['revertUps5maSell_3'] =round(revertUps5maSell_3)
    params['ma'] =round(ma)
    
    RVL = runBtOnce(params)
    print('curren params',params)
    return -RVL

####main main main main main main main main main main ###########################################################
#https://vimsky.com/examples/usage/python-scipy.optimize.dual_annealing.html
#params = {'revertDowns5maBuy_1': 7, 'revertDowns5maBuy_2': 3, 'revertUps5maSell_1': 3, 'revertUps5maSell_2': 5, 'revertUps5maSell_3': 10}
params = {'revertDowns5maBuy_1': 5, 'revertDowns5maBuy_2': 3, 'revertUps5maSell_1': 3, 'revertUps5maSell_2': 5, 'revertUps5maSell_3': 11,'ma':5}
runBtOnceAndShow(params)

if 1:
    buy1bound = [4,20]
    buy2bound = [3,5]
    sell1bound = [1,5]
    sell2bound = [5,20]
    sell3bound = [5,50]
    mabound = [2,10]
    bounds = [buy1bound, buy2bound,sell1bound,sell2bound,sell3bound,mabound]
    result = dual_annealing(objective, bounds,maxiter=100,maxfun = 2000,x0=[7,3,3,5,10,5])
    print('Status : %s' % result['message'])
    print('Total Evaluations: %d' % result['nfev'])
    # evaluate solution
    solution = result['x']
    evaluation = objective(solution)
    print('Solution: f(%s) = %.5f' % (solution, evaluation))
    print(result)
