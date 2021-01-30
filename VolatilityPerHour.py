#!/usr/bin/env python
# coding: utf-8

# ![QuantConnect Logo](https://cdn.quantconnect.com/web/i/icon.png)
# <hr>

# # Volatility per Hour
# 
# 
# At what hour of the day do we see how much volatility?
# 
# volatility means standard derivation
# 
# a high value means price is a in average far away from the mean price
# 

# In[3]:


qb = QuantBook()
resolution = Resolution.Hour
windowlength = 24
historylength = 24  * 360 * 5

pairs = ['EURUSD']
symbols = []
for pair in pairs:
    symbols.append( qb.AddForex(pair, resolution).Symbol )
h = qb.History(symbols, historylength, resolution).close.unstack(level=0).dropna()


# In[4]:


zscore = lambda x: (x[-1] - x.mean()) / x.std()


results = {}
for pair in pairs:
    h['zscore'] = h[pair].rolling(windowlength).apply(zscore)
    results[pair] = []
    for n in range(0,24):
        results[pair].append( h['zscore'].between_time(str(n) + ':00', str(n) + ':59').mean() ** 2)

df = pd.DataFrame(results)
df.plot.bar(figsize=(5,3))


# In[ ]:




