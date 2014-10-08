# coding: utf-8

import sys
sys.path.extend(['/Users/jstemm/anaconda/lib/python2.7/site-packages'])

import pandas as pd
import itertools
import datetime
import calendar
import numpy
import sys
import os

start_day = datetime.datetime(2014, 10, 8, 0, 0)

def wk2num(dt):
    """take in a datetime object and return a number, 0-6.99 corresponding to day of week and time"""
    
    import numpy
    
    wkd = dt.dayofweek
    tme = (wkd * 288) + (dt.hour * 12) + (dt.minute / 5)
    
    return tme

topdir = os.path.join(os.getenv('HOME'), '.logstats')
dbdir = os.path.join(os.getenv('HOME'), 'Dropbox', 'workshare', 'batlog')

wake = os.path.join(topdir, 'wakelog.dat')
bat = os.path.join(topdir, 'batlog.dat')

D = pd.read_table(wake, names = ['dow', 'month', 'day', 'time', 'tz', 'year', 'user', 'SSID', 'runmode'],
                                          parse_dates = {'dtime': ['dow', 'month', 'day', 'time', 'year']},
                                          sep = ' ', 
                                          index_col='dtime', 
                                          header=None)
D = D.fillna("WiFi Disconnected")
H = D.groupby('SSID')

B = pd.DataFrame(columns=['Amperage', 'Capacity', 'Current', 'Cycle Count', 'Flags', 'Voltage'])
with open(bat) as f:
    for c, e in itertools.izip_longest(*[f]*2):
        a = c.split()
        dt = a[1]+a[2].zfill(2)+a[3]+a[5]
        d = datetime.datetime.strptime(dt, '%b%d%H:%M:%S%Y')
        if e.startswith('    | |           "LegacyBatteryInfo"'):
            b = eval(e.split(" = ")[1].replace("=", ":"))
            b['Amperage'] = b['Amperage']/1e16
            B = B.append(pd.DataFrame(b, index=[d,]))
        else:
            continue

wk = [i.dayofyear for i in D.index]
wkbat = [i.dayofyear for i in B.index]

tod = [-1*numpy.int(numpy.floor((i.to_pydatetime() - datetime.datetime(i.year, i.month, i.day, 0, 0)).seconds / 300.)) for i in D.index]
todbat = [-1*numpy.int(numpy.floor((i.to_pydatetime() - datetime.datetime(i.year, i.month, i.day, 0, 0)).seconds / 300.)) for i in B.index]

pct = (B.Current / B.Capacity)*100.

SSID_namelist = D.SSID.unique()
SSID_namelist.sort()

nSSID = len(SSID_namelist)

netnames = SSID_namelist.tolist()
ssids = [netnames.index(i) for i in D.SSID]

import matplotlib.pyplot as plt
import matplotlib.cm as cm

# batfig
#################################################
batfig = plt.figure(figsize=(9,6), dpi=300)

ax = batfig.add_subplot(211)
ax.plot_date(B.index, B['Cycle Count'], '-')
ax.set_ylabel('Cycle Count')
ax.set_xticklabels([])
ax.grid('on')
ax.set_title('Battery Statistics')

ax = batfig.add_subplot(212)
ax.plot_date(B.index, (B['Capacity']/8440.)*100, 'k.')
ax.set_ylabel('Battery Capacity (%)')
#ax.set_xticklabels([])
ax.grid('on')

#ax = batfig.add_subplot(313)
#ax.plot_date(B.index, B['Capacity'], 'k.')
#ax.set_ylabel('Battery Current')
#ax.grid('on')

plt.savefig(os.path.join(dbdir, 'batstats.png'), dpi=300)

# batyear
#################################################
batyear = plt.figure(figsize=(10, 5), dpi=300)
ax = batyear.add_axes([0.12, 0.1, 0.9, 0.8])

c = ax.scatter(wkbat, todbat, c=pct, edgecolor='none', marker='s', s=1, cmap=cm.rainbow_r, vmax=100., vmin=0.)

ax.set_xlabel('Day of Year')
ax.set_ylabel('Time of Day')

ax.set_xlim((0, 366))
ax.set_ylim((-288, 0))

ax.set_yticks(numpy.arange(0, 25, 3)*-12)
ax.set_yticklabels(['Midnight', '3am', '6am', '9am', 'Noon', '3pm', '6pm', '9pm', 'Midnight'])

ax.grid('on')
cb = plt.colorbar(c, pad=0.02)
cb.set_label('Battery Percentage')
cb.ax.tick_params(labelsize=8)

plt.savefig(os.path.join(dbdir, 'batyear.png'), dpi=300)

# yearview
#################################################
fig = plt.figure(figsize=(10,5), dpi=300)
ax = fig.add_subplot(111)

c=ax.scatter(wk, tod, c=numpy.array(ssids), edgecolor='none', marker='s', s=1, cmap=cm.rainbow)
ax.set_xlabel('Day of Year')
ax.set_ylabel('Time of Day')

ax.set_xlim((0, 366))
ax.set_ylim((-288, 0))

ax.set_yticks(numpy.arange(0, 25, 3)*-12)
ax.set_yticklabels(['Midnight', '3am', '6am', '9am', 'Noon', '3pm', '6pm', '9pm', 'Midnight'])

ax.grid('on')
cb = plt.colorbar(c)
cb.set_ticks(numpy.arange(nSSID))
cb.set_ticklabels(netnames)
cb.ax.tick_params(labelsize=8)


plt.savefig(os.path.join(dbdir, 'yearview.png'), dpi=300)


# weekstats
#################################################
fig.clf()
ax = fig.add_axes([0.05, 0.1, 0.7, 0.8])

counts = [wk2num(g) for g in D.index]
ax.hist(counts, bins=numpy.arange(0, 2016), histtype='step', label='ALL')

for g in H.groups.keys():
    counts = [wk2num(v) for v in H.get_group(g).index]
    ax.hist(counts, bins=numpy.arange(0, 2016), histtype='step', label=g)

ax.set_xticks(numpy.arange(7)*288)
ax.set_xticks((numpy.arange(7)+.5)*288, minor=True)
ax.set_xticklabels([])
ax.set_xticklabels(calendar.day_name[0:7], minor=True)
ax.set_xlim((0, 2016))
ax.set_yticks([])
ax.set_ylim(0, ax.get_ylim()[1]*1.1)

ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10, title="SSID", frameon=False)

ax.set_xlabel('Day of Week')
ax.set_ylabel('Computer Useage')
plt.suptitle('Computer Useage by Day of Week and SSID')

plt.savefig(os.path.join(dbdir, 'weekstats.png'), dpi=300)

plt.close('all')