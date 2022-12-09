

import datetime  # For datetime objects
import backtrader as bt

try:
    datapath = '/home/liuli/github/myQuantInvest/dataTmp.csv'
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        fromdate=datetime.datetime(2020, 1, 5),
        todate=datetime.datetime(2022, 12, 8),
        timeframe = bt.TimeFrame.Minutes,
        reverse=False)
except Exception as err:
        print("Fail")
        print("Fail " + str(err))
        
data.info()