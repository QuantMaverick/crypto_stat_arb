"""
Python 3.6

"""

import numpy as np
import pandas as pd
from scipy import stats
from matplotlib import pyplot as plt
from datetime import datetime
import json
from bs4 import BeautifulSoup
import requests
 
%matplotlib inline
grey = .6, .6, .6
 
# define a pair
fsym = "ETH"
tsym = "USD"
 
url = "https://www.cryptocompare.com/api/data/coinsnapshot/?fsym=" + \
       fsym + "&tsym=" + tsym
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
dic = json.loads(soup.prettify())
print(dic)

# Retrieve all exchanges
market = []
d = dic['Data']['Exchanges']  # a list
for i in range(len(d)):
    market.append(d[i]['MARKET'])
    print(market[-1])

# Retrieve volume of ETH in each exchange
vol = []
d = dic['Data']['Exchanges']  # a list
for i in range(len(d)):
    vol.append([d[i]['MARKET'], round(float(d[i]['VOLUME24HOUR']),2)])
 
# sort a list of sublists according to 2nd item in a sublist
vol = sorted(vol, key=lambda x: -x[1])
 
# Cryptocurrency Markets according to Volume traded within last 24 hours
for e in vol:
    print("%10s%15.2f" % (e[0], e[1]))

# Select Top 10 Cryptocurrency Markets
markets = [e[0] for e in vol][0:10]
print(markets)


def fetchCryptoOHLC_byExchange(fsym, tsym, exchange):
    """a function fetches a crypto OHLC price-series for fsym/tsym and stores
    it in a pandas DataFrame; uses specific Exchange as provided 
    src: https://www.cryptocompare.com/api/"""
 
    cols = ['date', 'timestamp', 'open', 'high', 'low', 'close']
    lst = ['time', 'open', 'high', 'low', 'close']
 
    timestamp_today = datetime.today().timestamp()
    curr_timestamp = timestamp_today
 
    for j in range(2):
        df = pd.DataFrame(columns=cols)
        url = "https://min-api.cryptocompare.com/data/histoday?fsym=" + fsym + \
              "&tsym=" + tsym + "&toTs=" + str(int(curr_timestamp)) + \
              "&limit=2000" + "&e=" + exchange
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        dic = json.loads(soup.prettify())
 
        for i in range(1, 2001):
            tmp = []
            for e in enumerate(lst):
                x = e[0]
                y = dic['Data'][i][e[1]]
                if(x == 0):
                    # timestamp-to-date
                    td = datetime.fromtimestamp(int(y)).strftime('%Y-%m-%d')
                    tmp.append(td)  #(str(timestamp2date(y)))
                tmp.append(y)
            if(np.sum(tmp[-4::]) > 0):
                df.loc[len(df)] = np.array(tmp)
        df.index = pd.to_datetime(df.date)
        df.drop('date', axis=1, inplace=True)
        curr_timestamp = int(df.iloc[0][0])
 
        if(j == 0):
            df0 = df.copy()
        else:
            data = pd.concat([df, df0], axis=0)
 
    return data.astype(np.float64)


# if a variable 'cp' exists, delete it
if ('cp' in globals()) or ('cp' in locals()): del cp
 
# download daily OHLC price-series for ETH/USD for a given 'market'
# extract close-price (cp)
 
print("%s/%s" % (fsym, tsym))
for market in markets:
    print("%12s... " % market, end="")
    df = fetchCryptoOHLC_byExchange(fsym, tsym, market)
    ts = df[(df.index > "2017-06-01") & (df.index <= "2017-11-05")]["close"]
    ts.name = market
    if ('cp' in globals()) or ('cp' in locals()):
        cp = pd.concat([cp, ts], axis=1, ignore_index=False)
    else:
        cp = pd.DataFrame(ts)
    print("downloaded")


print(cp.head(10))
print(cp.tail(10))


# To find average difference in daily closing price & supplement it with 1 std dev. 
dist = []
for i in range(cp.shape[1]):
    for j in range(i):
        if(i != j):
            x = np.array(cp.iloc[:,i], dtype=np.float32)
            y = np.array(cp.iloc[:,j], dtype=np.float32)
            diff = np.abs(x-y)
            avg = np.mean(diff)
            std = np.std(diff, ddof=1)
            dist.append([cp.columns[i], cp.columns[j], avg, std])
 
dist = sorted(dist, key=lambda x: -x[2])
print("%10s%10s%10s%10s\n" % ("Coin1", "Coin2", "Mean", "Std Dev"))
for e in dist:
    print("%10s%10s%10.5f%10.2f" % (e[0], e[1], e[2], e[3]))


# Select two markets with the highest mean spread at the lowest standard deviation
# From results generated on 18 Jan 2018, I have selected Exmo & Kraken
market1 = "Exmo"
market2 = "Kraken"
 
df1 = fetchCryptoOHLC_byExchange(fsym, tsym, market1)
df2 = fetchCryptoOHLC_byExchange(fsym, tsym, market2)
 
# trim
df1 = df1[(df1.index > "2017-06-01") & (df1.index <= "2017-11-05")]
df2 = df2[(df2.index > "2017-06-01") & (df2.index <= "2017-11-05")]
 
# checkpoint
print(df1.close.shape[0], df2.close.shape[0])  # both sizes must be equal
 
# plotting
plt.figure(figsize=(20,10))
plt.plot(df1.close, '.-', label=market1)
plt.plot(df2.close, '.-', label=market2)
plt.legend(loc=2)
plt.title(fsym, fontsize=12)
plt.ylabel(tsym, fontsize=12)
plt.grid()


# Backtesting Stat Arb trading strategy for ETH/USD at Exmo and Kraken
#  cryptocurrency exchanges
 
# initial parameters
investment = 10000  # USD
account1, account2 = investment/2, investment/2  # USD
position = 0.5*(investment/2)  # USD
 
roi = []
ac1 = [account1]
ac2 = [account2]
money = []
pnl_exch1 = []
pnl_exch2 = []
trade_pnl = []
 
trade = False
n = df1.close.shape[0]  # number of data points
 
# running the backtest
for i in range(n):
    p1 = float(df1.close.iloc[i])
    p2 = float(df2.close.iloc[i])
    if(p1 > p2):
        asset1 = "SHORT"
        asset2 = "LONG"
        if(trade == False):
            open_p1 = p1  # open prices
            open_p2 = p2
            open_asset1 = asset1
            open_asset2 = asset2
            trade = True
            print("new traded opened")
            new_trade = False
        elif(asset1 == open_asset1):
            new_trade = False  # flag
        elif(asset1 == open_asset2):
            new_trade = True   # flag
 
    elif(p2 > p1):
        asset1 = "LONG"
        asset2 = "SHORT"
        if(trade == False):
            open_p1 = p1  # open prices
            open_p2 = p2
            open_asset1 = asset1
            open_asset2 = asset2
            trade = True
            print("new traded opened")
            new_trade = False
        elif(asset1 == open_asset1):
            new_trade = False  # flag
        elif(asset1 == open_asset2):
            new_trade = True   # flag
 
    if(i == 0):
        print(df1.close.iloc[i], df2.close.iloc[i], \
              asset1, asset2, trade, "----first trade info")
    else:
        if(new_trade):
 
            # close current position
            if(open_asset1 == "SHORT"):
                # PnL of both trades
                pnl_asset1 = open_p1/p1 - 1
                pnl_asset2 = p2/open_p2 -1
                pnl_exch1.append(pnl_asset1)
                pnl_exch2.append(pnl_asset2)
                print(open_p1, p1, open_p2, p2, open_asset1, \
                      open_asset2, pnl_asset1, pnl_asset2)
                # update both accounts
                account1 = account1 + position*pnl_asset1
                account2 = account2 + position*pnl_asset2
                print("accounts [USD] = ", account1, account2)
                if((account1 <=0) or (account2 <=0)):
                    print("--trading halted")
                    break
                # return on investment (ROI)
                total = account1 + account2
                roi.append(total/investment-1)
                ac1.append(account1)
                ac2.append(account2)
                money.append(total)
                print("ROI = ", roi[-1])
                print("trade closed\n")
                trade = False
 
                # open a new trade
                if(asset1 == "SHORT"):
                    open_p1 = p1
                    open_p2 = p2
                    open_asset1 = asset1
                    open_asset2 = asset2
                else:
                    open_p1 = p1
                    open_p2 = p2
                    open_asset1 = asset1
                    open_asset2 = asset2
                trade = True
                print("new trade opened", asset1, asset2, \
                      open_p1, open_p2)
 
            # close current position
            if(open_asset1 == "LONG"):
                # PnL of both trades
                pnl_asset1 = p1/open_p1 -1
                pnl_asset2 = open_p2/p2 - 1
                pnl_exch1.append(pnl_asset1)
                pnl_exch2.append(pnl_asset2)
                print(open_p1, p1, open_p2, p2, open_asset1, \
                      open_asset2, pnl_asset1, pnl_asset2)
                # update both accounts
                account1 = account1 + position*pnl_asset1
                account2 = account2 + position*pnl_asset2
                print("accounts [USD] = ", account1, account2)
                if((account1 <=0) or (account2 <=0)):
                    print("--trading halted")
                    break
                # return on investment (ROI)
                total = account1 + account2
                roi.append(total/investment-1)
                ac1.append(account1)
                ac2.append(account2)
                money.append(total)
                trade_pnl.append(pnl_asset1+pnl_asset2)
                print("ROI = ", roi[-1])
                print("trade closed\n")
                trade = False
 
                # open a new trade
                if(open_asset1 == "SHORT"):
                    open_p1 = p1
                    open_p2 = p2
                    open_asset1 = asset1
                    open_asset2 = asset2
                else:
                    open_p1 = p1
                    open_p2 = p2
                    open_asset1 = asset1
                    open_asset2 = asset2
                new_trade = False
                trade = True
                print("new trade opened:", asset1, asset2, \
                      open_p1, open_p2)
 
        else:
            print("   ",df1.close.iloc[i], df2.close.iloc[i], \
                  asset1, asset2)


# Plots to display cash levels in each exchange

plt.figure(figsize=(12,7))
 
plt.subplot(2,3,1)
plt.plot(ac1)
plt.title("Exmo: Cash Level")
plt.xlabel("Trade No."); plt.ylabel("USD")
plt.grid()
plt.xlim([0, len(money)])
plt.ylim([0, 14001])
 
plt.subplot(2,3,2)
plt.plot(ac2)
plt.title("Kraken: Cash Level")
plt.xlabel("Trade No."); plt.ylabel("USD")
plt.grid()
plt.xlim([0, len(money)])
plt.ylim([0, 14001])
 
plt.subplot(2,3,3)
plt.plot(np.array(money))
plt.title("Total Cash")
plt.xlabel("Trade No."); plt.ylabel("USD")
plt.grid()
plt.xlim([0, len(money)])
plt.ylim([investment, 14000])
 
plt.tight_layout()
plt.savefig('cashlevels.png', bbox_inches='tight')


# Plot of ROI of Stat Arb 
plt.figure(figsize=(8,5))
plt.plot(np.array(roi)*100, 'g')
plt.xlabel("Trade No."); 
plt.ylabel("Equity Growth [%]")
plt.title("ROI = %f.2%%" % (100*roi[-1]))
plt.xlim([0, len(money)])
plt.ylim([0, 40])
plt.grid()
plt.savefig('roi.png', bbox_inches='tight')

