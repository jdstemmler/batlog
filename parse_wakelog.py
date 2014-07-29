
# coding: utf-8

# In[53]:

import pandas as pd
import calendar
import numpy


# In[57]:

D = pd.read_table('wakelog.txt', names = ['host', 'dow', 'month', 'day', 'time', 'tz', 'year'],
                                          parse_dates = {'dtime': ['dow', 'month', 'day', 'time', 'year', 'tz']}, 
                                          sep = ' ', 
                                          index_col='dtime', 
                                          header=None)
#print(D)


# In[58]:

# Group the data by time of the week and show a weekly view of useage

# define a function to assign values to day of week. 0 = Monday, 6 = Sunday
# x.0 = midnight, 0.99 = 11:59 or so pm

def wk2num(dt):
    """take in a datetime object and return a number, 0-6.99 corresponding to day of week and time"""
    
    import numpy
    
    wkd = dt.isoweekday() - 1
    tme = (dt.hour + (dt.minute / 60.)) / 24.
            
    return wkd + tme
    #return str(bins[numpy.abs(bins-val).argmin()])

H = D.groupby('host')


# In[60]:

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(10,4), dpi=300)
ax = fig.add_subplot(111)

for g in H.groups.keys():
    counts = [wk2num(v) for v in H.get_group(g).index]
    ax.hist(counts, bins=numpy.arange(0, 7, 0.05),  histtype='step', label=g)
        
    

ax.set_xticks(numpy.arange(7))
ax.set_xticks(numpy.arange(7)+.5, minor=True)
ax.set_xticklabels([])
ax.set_xticklabels(calendar.day_name[0:7], minor=True)
ax.set_yticks([])

ax.set_xlabel('Day of Week')
ax.set_ylabel('Computer Useage')
plt.legend()

plt.savefig('week_use.png')

