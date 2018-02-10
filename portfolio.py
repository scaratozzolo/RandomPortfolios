import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import csv
import random
import os
import pickle

style.use('ggplot')

if not os.path.exists('Data'):
    os.makedirs('Data')

# with open("sp500tickers.pickle","rb") as f:
#     tickers = pickle.load(f)

tickers = []

for i in os.listdir('TickerData'):
    tickers.append(i[:-4])

def randomport(num):
    portfolio = []
    i = 0
    while i < num:
        ticker = tickers[random.randint(0,len(tickers)-1)]
        if ticker not in portfolio:
            portfolio.append(ticker)
            i += 1

    return sorted(portfolio)





# df = pd.read_csv('TickerData/GOOG.csv', parse_dates=True, index_col=0)
# df1 = pd.read_csv('TickerData/AAPL.csv', parse_dates=True, index_col=0)
# print(df['2005']['Close'].count())
# print(df1['2005']['Close'].count())

# df['Close'].plot()
# plt.title('AAPL')
# plt.tight_layout()
#
# plt.savefig(fname='test', dpi=320)


def portfolioyear(portfolio):

    years = [2017, 2012, 2008, 2003]        #add more years? 1987 finally and then maybe go back to russell
    confyears = []

    for year in years:
        try:
            for ticker in portfolio:
                df = pd.read_csv('TickerData/{}.csv'.format(ticker), parse_dates=True, index_col=0)
                df['{}-01'.format(year)]['Close']
                df['{}-12'.format(year)]['Close']
        except:
            continue

        for ticker in portfolio:
            df = pd.read_csv('TickerData/{}.csv'.format(ticker), parse_dates=True, index_col=0)
            jandays = df['{}-01'.format(year)]['Close'].count()
            decdays = df['{}-12'.format(year)]['Close'].count()
            for ticker in portfolio:
                df1 = pd.read_csv('TickerData/{}.csv'.format(ticker), parse_dates=True, index_col=0)
                if jandays != df1['{}-01'.format(year)]['Close'].count() or decdays != df1['{}-12'.format(year)]['Close'].count():
                        break
                        break
                        continue

        confyears.append(str(year))
    return confyears


# saved10 = []
#
# for i in range(250):
#     port = randomport(10)
#     if port not in saved10:
#         saved10.append(port)
#
# for portfolio in saved10:
#     print(portfolio)
#     print(portfolioyear(portfolio))



def portfolio(size, to_make):

    if not os.path.exists('Data/Portfolio10'):
        os.makedirs('Data/Portfolio10')

    saved10 = []

    changes = {'2017':[], '2012':[], '2008':[], '2003':[]}

    for i in range(to_make):
        port = randomport(size)
        if port not in saved10:
            saved10.append(port)

    for num, portfolio in enumerate(saved10):

        if not os.path.exists('Data/Portfolio{}/Portfolio{}'.format(size,num)):
            os.makedirs('Data/Portfolio{}/Portfolio{}'.format(size,num))

        STARTING_AMOUNT = 1000000
        WEIGHT = 1/len(portfolio)

        YEARS = portfolioyear(portfolio)
        if YEARS == []:
            continue

        stocks = {}
        for ticker in portfolio:
            stocks[ticker] = pd.read_csv('TickerData/{}.csv'.format(ticker), parse_dates=True, index_col=0)

        main_df = pd.DataFrame()
        for ticker in stocks:

            stuff = stocks[ticker].rename(columns={'Close':ticker})
            stuff.drop(['Open','High','Low','Volume'],1,inplace=True)
            if main_df.empty:
                main_df = stuff
            else:
                main_df = main_df.join(stuff, how='outer')

        for year in YEARS:
            shares = {}
            ticker_change = []

            for ticker in stocks:
                shares[ticker] = int((WEIGHT*STARTING_AMOUNT)/stocks[ticker][str(year)]['Close'].iloc[0])
                ticker_change.append(shares[ticker]*stocks[ticker][str(year)]['Close'].iloc[stocks[ticker][str(year)]['Close'].count()-1])

            dates = []
            dailychanges = []
            for index, row in main_df[str(year)].iterrows():
                dates.append(index)
                total = 0
                for ticker in portfolio:
                    total += shares[ticker]*row[ticker]
                dailychanges.append(round(((total-STARTING_AMOUNT)/STARTING_AMOUNT)*100, 2))
            percents = pd.DataFrame({'Date':dates, 'Percent Change':dailychanges})
            percents.index = percents['Date']
            percents = percents.drop(['Date'], axis = 1)
            main_df['Percent Change'] = percents['Percent Change']

            total = 0
            for i in ticker_change:
                total += i

            prctchange = round(((total-STARTING_AMOUNT)/STARTING_AMOUNT)*100, 2)
            changes[year].append(prctchange)



            plt.figure(figsize=(8, 6), dpi=320)
            main_df[str(year)]['Percent Change'].plot()
            plt.title('Percent Return {}'.format(str(year)))
            plt.tight_layout()

            plt.savefig(fname='Data/Portfolio{}/Portfolio{}/return-{}-{}.png'.format(size,num,year, num), dpi=320)
            plt.clf()
            plt.close()
            # # plt.show()

            no_percent = main_df.drop(['Percent Change'], axis=1)
            df_corr = no_percent[str(year)].corr()
            heatmap(df_corr, str(size), num, 'correlation', year)

            sp = pd.read_csv('TickerData/SP500.csv', parse_dates=True, index_col=0)
            sp.drop(['Open','High','Low','Volume'],1,inplace=True)
            plt.figure(figsize=(8, 6), dpi=320)
            sp[str(year)]['Close'].plot()
            plt.title('SPY ETF {}'.format(str(year)))
            plt.tight_layout()

            plt.savefig(fname='Data/Portfolio{}/Portfolio{}/SP500-{}.png'.format(size,num,year, num), dpi=320)
            plt.clf()
            plt.close()

            sp['Percent Return'] = percents['Percent Change']
            sp_corr = sp.corr()
            heatmap(sp_corr, size, num, 'SPYtoReturnsCorr', year)
            # print(sp_corr.head())


def heatmap(df_corr, port, num, name, year):
    data1 = df_corr.values
    if int(port) < 25:
        fig1 = plt.figure()
    else:
        fig1 = plt.figure(figsize=(24, 18))
    ax1 = fig1.add_subplot(111)

    heatmap1 = ax1.pcolor(data1, cmap=plt.cm.RdYlGn)
    fig1.colorbar(heatmap1)

    ax1.set_xticks(np.arange(data1.shape[1]) + 0.5, minor=False)
    ax1.set_yticks(np.arange(data1.shape[0]) + 0.5, minor=False)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    column_labels = df_corr.columns
    row_labels = df_corr.index
    ax1.set_xticklabels(column_labels)
    ax1.set_yticklabels(row_labels)
    plt.xticks(rotation=90)
    heatmap1.set_clim(-1,1)

    plt.tight_layout()
    plt.savefig('Data/Portfolio{}/Portfolio{}/{}-{}-{}.png'.format(port,num,name, year, num), dpi = (320))
    plt.clf()
    plt.close()
    # plt.show()

def cleanup():

    if os.listdir('Data') == []:
        os.rmdir('Data')
    else:
        for dire in os.listdir('Data'):
            if os.listdir('Data/{}'.format(dire)) == []:
                os.rmdir('Data/{}'.format(dire))
            else:
                for next_dire in os.listdir('Data/{}'.format(dire)):
                    if os.listdir('Data/{}/{}'.format(dire, next_dire)) == []:
                        os.rmdir('Data/{}/{}'.format(dire, next_dire))


sizes = [3,5,10,25,50,100]

for size in sizes:
    portfolio(size, 2)
cleanup()
