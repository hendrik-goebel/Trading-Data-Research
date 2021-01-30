#!/usr/bin/env python
# coding: utf-8

# ## CBOE Fundamental data requests

# In[7]:


from QuantConnect.Data.Custom.Fred import *
from QuantConnect.Data.Custom.CBOE import *

qb = QuantBook()
vix = qb.AddData(CBOE, "VIX")
spy = qb.AddEquity("SPY", Resolution.Daily)

vix_history = qb.History(CBOE, vix.Symbol, timedelta(days=1000))
spy_history = qb.History(spy.Symbol, timedelta(days=1000), Resolution.Daily)

# drop the Symbol index from multi-index dataframe
vix_history = vix_history.reset_index(level=0, drop=True)
spy_history = spy_history.reset_index(level=0, drop=True)

# Chart formatting
plt.title('Volatility in Markets')
plt.xlabel('Time')
plt.ylabel('Returns')

# Plot the percent change in daily close values of VIX and SPY
vix_history['close'].pct_change().plot(alpha=0.5) # Increase transparency of VIX plot
spy_history['close'].pct_change().cumsum().plot()


# In[8]:


qb = QuantBook()
resolution = Resolution.Hour
windowlength = 10
historylength = 24 * 30
symbol = qb.AddForex('EURUSD', resolution).Symbol
h = qb.History([symbol], historylength, resolution).close.unstack(level=0).dropna()


# In[9]:


zscore = lambda x: (x[-1] - x.mean()) / x.std()

h['zscore'] = h['EURUSD'].rolling(windowlength).apply(zscore)
results = []
for n in range(0,24):
    results.append( h['zscore'].between_time(str(n) + ':00', str(n) + ':59').mean() ** 2)

df = pd.DataFrame(results)
print(df)
df.plot()


# In[10]:


# The official interest rate comes from Quandl
from QuantConnect.Python import PythonQuandl
from NodaTime import DateTimeZone

class QuandlRate(PythonQuandl):
    def __init__(self):
        self.ValueColumnName = 'BCB/17900'
        
tickers = ["USDEUR", "USDZAR", "USDAUD",
                   "USDJPY", "USDTRY", "USDINR", 
                   "USDCNY", "USDMXN", "USDCAD"]
        
rate_symbols = ["BCB/17900",  # Euro Area 
                        "BCB/17906",  # South Africa
                        "BCB/17880",  # Australia
                        "BCB/17903",  # Japan
                        "BCB/17907",  # Turkey
                        "BCB/17901",  # India
                        "BCB/17899",  # China
                        "BCB/17904",  # Mexico
                        "BCB/17881"]  # Canada
       
symbols = {}
for i in range(len(tickers)):
    symbol = qb.AddForex(tickers[i], Resolution.Daily, Market.Oanda).Symbol
    qb.AddData(QuandlRate, rate_symbols[i], Resolution.Daily, DateTimeZone.Utc, True)
    symbols[str(symbol)] = rate_symbols[i]
            


# Bundesbank 10Y Yield federal Bond
# 
# https://www.quandl.com/data/BUNDESBANK/BBK01_WT1010-Daily-Yield-Of-The-Current-10-Year-Federal-Bond

# In[12]:


class QuandlCustomColumns(PythonQuandl):
    '''Custom quandl data type for setting customized value column name. Value column is used for the primary trading calculations and charting.'''
    def __init__(self):        
        self.ValueColumnName = "Value"

qb = QuantBook()
quandlCode = "BUNDESBANK/BBK01_WT1010"
gold = qb.AddData(QuandlCustomColumns, quandlCode, Resolution.Daily)

history = qb.History(qb.Securities.Keys, 360, Resolution.Daily)           
print(history.loc["BUNDESBANK/BBK01_WT1010"])

