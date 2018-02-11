import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
from multiprocessing import Process, Pool
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import csv
import random
import os
import pickle
import time
import tqdm

#I don't even think all of these import are used but I'm not touching them

style.use('ggplot')

if not os.path.exists('Data'):
    os.makedirs('Data')

#loads all the tickers in the sp500
# with open("sp500tickers.pickle","rb") as f:
#     tickers = pickle.load(f)

#loads all the tickers for every stock with data that exists
tickers = []
for i in os.listdir('TickerData'):
    tickers.append(i[:-4])

def randomport(num):
    """
    Creates a random portfolio of size num
    """
    portfolio = []
    i = 0
    while i < num:
        ticker = tickers[random.randint(0,len(tickers)-1)]
        if ticker not in portfolio:
            portfolio.append(ticker)
            i += 1

    return sorted(portfolio)



years = [2017, 2012, 2008, 2003]        #add more years? 1987 finally
def portfolioyear(portfolio):
    """
    Tests all the years in the lists years to see which years have complete data for all stocks in a portfolio
    """
    confyears = []

    #run through the years to find valid years
    for year in years:

        #go through all the tickers to make sure the data exists and to make sure there is data for the whole year
        #if not it skips the year because the year because it is not longer valid for the current portfolio
        try:
            for ticker in portfolio:
                df = pd.read_csv('TickerData/{}.csv'.format(ticker), parse_dates=True, index_col=0)
                df['{}-01'.format(year)]['Close']
                df['{}-12'.format(year)]['Close']
        except:
            continue

        #making sure all stocks have the same number of data points for a year, or at least close because I think there may be an issue but not a huge one
        for ticker in portfolio:
            df = pd.read_csv('TickerData/{}.csv'.format(ticker), parse_dates=True, index_col=0)
            jandays = df['{}-01'.format(year)]['Close'].count()
            decdays = df['{}-12'.format(year)]['Close'].count()
            for ticker in portfolio:
                df1 = pd.read_csv('TickerData/{}.csv'.format(ticker), parse_dates=True, index_col=0)
                if jandays != df1['{}-01'.format(year)]['Close'].count() or decdays != df1['{}-12'.format(year)]['Close'].count():
                        break
                        break
                        continue    #these lines may be the issue because I dont think this acctually works

        #if it gets this far then the year is valid or something broke...either way add it to the confirmed years list, confyears
        confyears.append(str(year))
    return confyears



graphs_made = 0
def portfolio(size, to_make):
    """
    Analyzing randomly made portfolios of size. to_make is the number of random portfolios to make.
    """

    global graphs_made

    #dictionary of lists for every year to save overall portfolio returns per year, turned into a data frame and csv file later
    changes = {'2017':[], '2012':[], '2008':[], '2003':[]}      #TODO: loop over years from portfolioyear to create empty lists, make both global

    #randomly generated portfolios
    saved_port = []
    for i in range(to_make):
        port = randomport(size)
        if port not in saved_port:
            saved_port.append(port)

    if not os.path.exists('Data/SP500'):
        os.makedirs('Data/SP500')

    #create a data frame for the SP500 index from csv (SPY ETF)
    sp = pd.read_csv('TickerData/SP500.csv', parse_dates=True, index_col=0)
    sp.drop(['Open','High','Low','Volume'],1,inplace=True)

    #Create a chart of close prices for every year being tested
    for year in years:
        if os.path.isfile('Data/SP500/{}-SP500.png'.format(year)):
            continue
        else:
            plt.figure(figsize=(8, 6), dpi=320)
            sp[str(year)]['Close'].plot()
            plt.title('SPY ETF {}'.format(str(year)))
            plt.ylabel('Points')
            plt.tight_layout()
            plt.savefig(fname='Data/SP500/{}-SP500.png'.format(year), dpi=320)
            plt.clf()
            plt.close()
            graphs_made += 1

    #perform analysis of every randomly generated portfolio
    for num, portfolio in enumerate(saved_port):
        if num % 100 == 0:
            print(' . ', end='')

        #portfolio parameters, equal weighting
        STARTING_AMOUNT = 1000000
        WEIGHT = 1/len(portfolio)

        #if the list is empty then there are no years where all stocks in portfolio have complete data to compute analysis
        YEARS = portfolioyear(portfolio)
        if YEARS == []:
            continue

        #creates directories for saving data
        if not os.path.exists('Data/Size{}'.format(size)):
            os.makedirs('Data/Size{}'.format(size))
        if not os.path.exists('Data/Size{}/Portfolio{}'.format(size,num)):
            os.makedirs('Data/Size{}/Portfolio{}'.format(size,num))

        #loads all csv files into data frames for each stock in portfolio
        stocks = {}
        for ticker in portfolio:
            stocks[ticker] = pd.read_csv('TickerData/{}.csv'.format(ticker), parse_dates=True, index_col=0)

        #creates a data frame based on stocks in portfolio of daily closes
        main_df = pd.DataFrame()
        for ticker in stocks:

            stuff = stocks[ticker].rename(columns={'Close':ticker})
            stuff.drop(['Open','High','Low','Volume'],1,inplace=True)
            if main_df.empty:
                main_df = stuff
            else:
                main_df = main_df.join(stuff, how='outer')

        #was getting weird errors, 'fixes' them
        try:
            #loop to test every year in which all the stocks have common trading years
            for year in YEARS:
                shares = {}
                ticker_change = []

                #calculates the number of shares to based on portfolio starting amount and weight defined above
                for ticker in stocks:
                    shares[ticker] = int((WEIGHT*STARTING_AMOUNT)/stocks[ticker][str(year)]['Close'].iloc[0])
                    ticker_change.append(shares[ticker]*stocks[ticker][str(year)]['Close'].iloc[stocks[ticker][str(year)]['Close'].count()-1])

                #creates the daily percent return
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


                #calculates the overall return of the portfolio from day one to last day
                total = 0
                for i in ticker_change:
                    total += i
                prctchange = round(((total-STARTING_AMOUNT)/STARTING_AMOUNT)*100, 2)
                changes[year].append(prctchange)

                #save main_df to csv to look at later if needed
                main_df[str(year)].to_csv('Data/Size{}/Portfolio{}/{}-maindf-{}.csv'.format(size,num,year, num))

                #creates graph of daily percent return
                plt.figure(figsize=(8, 6), dpi=320)
                ax = main_df[str(year)]['Percent Change'].plot()
                plt.title('Percent Return {}'.format(str(year)))
                vals = ax.get_yticks()
                ax.set_yticklabels(['{:3.0f}%'.format(x) for x in vals])
                plt.tight_layout()
                plt.savefig(fname='Data/Size{}/Portfolio{}/{}-return-{}.png'.format(size,num,year, num), dpi=320)
                plt.clf()
                plt.close()
                # # plt.show()
                graphs_made += 1

                #create heatmap of all stocks compared to the others
                no_percent = main_df.drop(['Percent Change'], axis=1)
                df_corr = no_percent[str(year)].corr()
                heatmap(df_corr, str(size), num, 'correlation', year, True)
                graphs_made += 1

                #creates heatmap of percent return for the portfolio compared to the SP500 index close price (SPY ETF)
                sp['Percent Return'] = percents['Percent Change']
                sp_corr = sp.corr()
                heatmap(sp_corr, size, num, 'SPYtoReturnsCorr', year)
                # print(sp_corr.head())
                graphs_made += 1
        except:
            print('Error')

    #makes all lists in the changes dictionary the same length for data frame purposes
    maxlen = 0
    for key in changes:
        if len(changes[key]) > maxlen:
            maxlen = len(changes[key])
    for key in changes:
        if len(changes[key]) < maxlen:
            for _ in range(maxlen - len(changes[key])):
                changes[key].append(0)

    #creates df of percent changes for every portfolio for every year that portfolio had a return
    changedf = pd.DataFrame.from_dict(changes)
    changedf.transpose()
    if changedf.empty:
        pass
    else:
        if not os.path.exists('Data/Returns'):
            os.makedirs('Data/Returns')
        changedf.replace(0, np.nan, inplace=True)
        changedf.to_csv('Data/Returns/size{}-returns.csv'.format(size))





def heatmap(df_corr, port, num, name, year, resize = False):
    """
    Creates a heatmap of correlation between stocks
    """
    data1 = df_corr.values
    if int(port) < 25 or not resize:
        fig1 = plt.figure()
    else:
        fig1 = plt.figure(figsize=(16, 12))
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
    plt.savefig('Data/Size{}/Portfolio{}/{}-{}-{}.png'.format(port,num,year, name, num), dpi = (320))
    plt.clf()
    plt.close()
    # plt.show()

def cleanup():
    """
    Deletes empty directories from Data
    """

    if os.listdir('Data') == []:
        os.rmdir('Data')
    else:
        for dire in os.listdir('Data'):
            if os.path.isfile('Data/{}'.format(dire)):
                continue
            elif os.listdir('Data/{}'.format(dire)) == []:
                os.rmdir('Data/{}'.format(dire))
            else:
                for next_dire in os.listdir('Data/{}'.format(dire)):
                    if os.path.isfile('Data/{}/{}'.format(dire,next_dire)):
                        continue
                    elif  os.listdir('Data/{}/{}'.format(dire, next_dire)) == [] :
                        os.rmdir('Data/{}/{}'.format(dire, next_dire))







if __name__ == '__main__':
    start = time.time()
    sizes = [3,5,10,25,50,100]
    # processes  = []
    for size in sizes:
        portfolio(size, 2000)
        print('Size {} done'.format(size))
    #     p = Process(target=portfolio, args=(size,20))
    #     processes.append(p)
    #
    # for p in processes:
    #     p.start()
    # for p in processes:
    #     p.join()

    # pool = Pool(processes=4)
    # results = [pool.apply(portfolio, args=(size,20)) for size in sizes]
    # print(results)

    print('{} graphs made'.format(graphs_made))
    print(time.time()-start)
    cleanup()
