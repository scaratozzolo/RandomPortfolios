import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import pandas as pd
import pandas_datareader.data as web
import csv
import random
import os
import time
import pickle

style.use('ggplot')

if not os.path.exists('TickerData'):
    os.makedirs('TickerData')

with open("sp500tickers.pickle","rb") as f:
    tickers = pickle.load(f)

tickers = []
for i in os.listdir('TickerData'):
    tickers.append(i[:-4])

start = dt.datetime(2002,1,1)
end = dt.datetime(2017,12,31)

# print(len(tickers))
# fails = 0
# for ticker in tickers:
#     print(ticker)
#     if os.path.isfile('{}.csv'.format(ticker)):
#         continue
#
#     try:
#         df = web.DataReader(ticker, 'google', start, end)
#         # df = df.reset_index(['Symbol'])           used with morningstar
#         # df = df.drop(['Symbol'], axis = 1)
#         #
#         # df = df.reset_index(['Date'])
#         # df['Date'] = pd.to_datetime(df['Date'])
#         # df.index = df['Date']
#         # df = df.drop(['Date'], axis = 1)
#
#         df.to_csv('TickerData/{}.csv'.format(ticker))
#         time.sleep(2)
#     except:
#         print('fail')
#         fails += 1

# print(fails)


df = web.DataReader('SPY', 'google', start, end)
df.to_csv('TickerData/SP500.csv')
