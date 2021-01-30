#!/usr/bin/env python
# coding: utf-8

# ## Request data

# In[10]:


qb = QuantBook()
from QuantConnect.Data.Custom.TradingEconomics import *
from QuantConnect.Data.Custom.CBOE import *

tickersForex  = [
    "EURUSD", 
    "USDCAD",
    "EURGBP",
    "AUDUSD",
    "USDJPY",
    "GBPUSD",
]
tickersCfd = [
    "DE30EUR",
    "SPX500USD",
    "US2000USD",
    "US30USD",
    "USB10YUSD",
    "USB30YUSD",
    "XAGUSD",
    "WHEATUSD",
    "WTICOUSD", #oil
    "XCUUSD", #Copper
    "XPDUSD", #Palladium
    "XPTUSD", #Platin
]

tickersCBOE = [
    "VIX"
]

tickersCBOE = []
# there is no intraday data avaible, so it needs interpolation
'''
tickersCBOE = [
    
    "VIX"
]
'''
symbols = []
tickers = tickersForex + tickersCfd

resolution = Resolution.Hour
for ticker in tickersCBOE:
    symbols.append ( qb.AddData(CBOE, ticker).Symbol )
    
for ticker in tickersCfd:
    symbols.append( qb.AddCfd(ticker, resolution, Market.Oanda).Symbol)

for ticker in tickersForex:
    symbols.append( qb.AddForex(ticker, resolution, Market.Oanda).Symbol)


# null values will be deleted    
historyShort = qb.History(symbols, 
                     7*24, 
                     resolution).close.unstack(level=0).dropna()
historyLong = qb.History(symbols, 
                     180*24, 
                     resolution).close.unstack(level=0).dropna()








# ## Standardizing

# In[11]:


from sklearn import preprocessing

scaler = preprocessing.StandardScaler()
# Get column names first
names = historyShort.columns
# Create the Scaler object
scaler = preprocessing.StandardScaler()

# Fit your data on the scaler object
scaledShort = scaler.fit_transform(historyShort)
scaledShort = pd.DataFrame(scaledShort, columns=names)



scaledLong = scaler.fit_transform(historyLong)
scaledLong = pd.DataFrame(scaledLong, columns=names)


historyLong.plot()
scaledLong.plot()


# In[12]:


#Correlation matrix 
matrixShort = scaledShort.corr()
matrixLong = scaledLong.corr()


# ## Correlation,  last 3 days

# In[13]:


print(matrixShort)
import seaborn as sns

sns.heatmap(matrixShort)


# ## Correlation,  last 360 days

# In[14]:


print(matrixLong)

import seaborn as sns

sns.heatmap(matrixLong)


# ## Correlation of one single asset 

# In[15]:


s='XAGUSD'
sdfl = matrixLong[s]
sdfs = matrixShort[s]

cdf = pd.DataFrame([sdfl, sdfs]).transpose()
cdf.columns= ['Long Term Cor', 'Short Term Cor']
cdf['Diff'] = cdf['Long Term Cor'] - cdf['Short Term Cor']
cdf = cdf.sort_values(by='Diff', ascending=False)
print('Correlation ' + s)
print(cdf)

maxRow = cdf[ cdf.Diff == cdf.Diff.max()] 


# ### Highest convergence

# In[16]:



mdf = pd.DataFrame()
for symbol in tickers:
    sdfl = matrixLong[symbol]
    sdfs = matrixShort[symbol]

    cdf = pd.DataFrame([sdfl, sdfs]).transpose()
    cdf.columns= ['Long Term Cor', 'Short Term Cor']
    cdf['Diff'] = cdf['Long Term Cor'] - cdf['Short Term Cor']

    maxRow = cdf[ cdf.Diff == cdf.Diff.max()] 
    dx = pd.DataFrame(maxRow)
    dx['Symbol2'] = symbol
    mdf = mdf.append(dx.iloc[0])

    
mdf = mdf[['Symbol2', 'Long Term Cor', 'Short Term Cor', 'Diff']]
mdf = mdf.sort_values(by='Diff', ascending=False)
print(mdf)
    


# ### Volatility

# In[17]:



stdsl = []
stdss = []

for symbol in tickers:
    stdss.append(scaledShort[symbol].std())
    stdsl.append(scaledLong[symbol].std())
print(stdss)
df_vola_long = pd.DataFrame(stdsl, index=tickers, columns=['Vola Long'])
df_vola_short = pd.DataFrame(stdss, index=tickers, columns=['Vola Short']).sort_values(by='Vola Short')
print(df_vola_long)


# ### Calculate Z-Score

# In[18]:


qb = QuantBook()
resolution = Resolution.Hour
windowlength = 10
historylength = 24 * 30
symbol = qb.AddForex('EURUSD', resolution).Symbol
h = qb.History([symbol], historylength, resolution).close.unstack(level=0).dropna()


# In[19]:


zscore = lambda x: (x[-1] - x.mean()) / x.std()

h['zscore'] = h['EURUSD'].rolling(windowlength).apply(zscore)
results = []
for n in range(0,24):
    results.append( h['zscore'].between_time(str(n) + ':00', str(n) + ':59').mean() ** 2)

df = pd.DataFrame(results)
print(df)
df.plot()

