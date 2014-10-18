# coding: utf-8

import sys
sys.path.extend(['/Users/jstemm/anaconda/lib/python2.7/site-packages'])

import pandas as pd
import itertools
import datetime
import calendar
import numpy
# import sys
import os

start_day = datetime.datetime(2014, 10, 8, 0, 0)

def wk2num(dt):
    """take in a datetime object and return a number, 0-6.99 corresponding to day of week and time"""
    
    # import numpy
    
    wkd = dt.dayofweek
    tme = (wkd * 288) + (dt.hour * 12) + (dt.minute / 5)
    
    return tme

def sid_check(sid):
    
    if len(sid) == 0:
        return 'No WiFi'
    
    home = ['DangerZone', 'Danger Zone', 'Office Zone']
    work = ['University of Washington']
    coffee = ['IssaquahCoffee', 'Allegro', 'Google Starbucks']
    hotspot = ['JStemm']
    
    if sid in home:
        return 'Home'
        
    elif sid in work:
        return 'Work'
        
    elif sid in coffee:
        return 'Coffee Shop'
        
    elif sid in hotspot:
        return 'Mobile Hotspot'
        
    else:
        return 'Other'

topdir = os.path.join(os.getenv('HOME'), '.logstats')
dbdir = os.path.join(os.getenv('HOME'), 'Dropbox', 'workshare', 'batlog')

log = os.path.join(topdir, 'batlog.dat')
#log = os.path.join(topdir, 'example.data')

#D = pd.read_table(wake, names = ['dow', 'month', 'day', 'time', 'tz', 'year', 'user', 'SSID', 'runmode'],
#                                          parse_dates = {'dtime': ['dow', 'month', 'day', 'time', 'year']},
#                                          sep = ' ', 
#                                          index_col='dtime', 
#                                          header=None)
#D = D.fillna("WiFi Disconnected")
#H = D.groupby('SSID')

DATA = pd.DataFrame(columns=['Capacity', 'CycleCount', 'BatLife',
                          'CurrentPowerState', 'SSID', 'PCT',
                          'WiFi', 'Eth'])
with open(log) as f:
    for a, b, c, d, e in itertools.izip_longest(*[f]*5):
        # parse the date and time
        A = a.split()
        dt = A[1]+A[2].zfill(2)+A[3]+A[5]
        dt = datetime.datetime.strptime(dt, '%b%d%H:%M:%S%Y')
        
        # parse the nework info
        sid = sid_check(b.split(' SSID ')[-1].split("\n")[0])
        wifistat = b.split()[3]
        C = c.split()
        if len(C) < 2:
            ethstat = "inactive"
        elif len(C) >= 3:
            ethstat = "active"
        
        # parse the battery info        
        D = eval(d.split(" = ")[1].replace("=", ":"))
        
        # parse the power state
        if len(e) < 7:
            E = {'CurrentPowerState': 0}
        else:
            E = eval(e.split(" = ")[1].replace("=", ":"))
        
        # Create the single-row DataFrame
        G = pd.DataFrame({'Capacity': D['Capacity'],
                          'Current': D['Current'],
                          'PCT' : (1.*D['Current']/D['Capacity'])*100.,
                          'BatLife' : D['Capacity']/8440.*100.,
                          'CycleCount': D['Cycle Count'],
                          'CurrentPowerState': E['CurrentPowerState'],
                          'SSID': sid,
                          'WiFi': wifistat,
                          'Eth': ethstat}, index=[dt,])
        
        DATA = DATA.append(G)

AWAKE = DATA[DATA.CurrentPowerState != 0]

nDays = (DATA.index[-1] - DATA.index[0]).days + 1
nTimeOfDay = (60./5)*24 # number of 5 minute samples per day

startDate = DATA.index[0].date()

SSID_namelist = DATA.SSID.unique()
SSID_namelist.sort()

nSSID = len(SSID_namelist)

netnames = SSID_namelist.tolist()
ssids = [netnames.index(i) for i in DATA.SSID]

DATA['ssids'] = ssids

batgrid = numpy.zeros((nTimeOfDay, nDays))*numpy.nan
ssidgrid = numpy.zeros_like(batgrid)*numpy.nan
awakegrid = numpy.zeros_like(batgrid)*numpy.nan

for i in DATA.iterrows():
    dS = (i[0].date() - startDate).days
    tOD = numpy.int(numpy.floor(
           (i[0].to_pydatetime() - 
            datetime.datetime(i[0].year, i[0].month, i[0].day)).seconds/300.))
    
    batgrid[tOD, dS] = i[1].PCT
    ssidgrid[tOD, dS] = i[1].ssids
    
    if i[1].CurrentPowerState !=0:
        awakegrid[tOD, dS] = 1


import matplotlib.pyplot as plt
import matplotlib.cm as cm

# batfig
#################################################
batfig = plt.figure(figsize=(9,6), dpi=300)

ax = batfig.add_subplot(211)
ax.plot_date(DATA.index, DATA['CycleCount'], '-')
ax.set_ylabel('Cycle Count')
ax.set_xticklabels([])
ax.grid('on')
ax.set_title('Battery Statistics')

ax = batfig.add_subplot(212)
ax.plot_date(DATA.index, DATA['BatLife'], 'k.')
ax.set_ylabel('Battery Capacity (%)')
#ax.set_xticklabels([])
ax.grid('on')

#ax = batfig.add_subplot(313)
#ax.plot_date(DATA.index, DATA['Capacity'], 'k.')
#ax.set_ylabel('Battery Current')
#ax.grid('on')

plt.savefig(os.path.join(dbdir, 'batstats.png'), dpi=300)

# batyear
#################################################
batyear = plt.figure(figsize=(10, 5), dpi=300)
ax = batyear.add_axes([0.12, 0.1, 0.9, 0.8])

#c = ax.scatter(DOY, TOD, c=DATA['PCT'], edgecolor='none', marker='s', s=1, 
#               cmap=cm.rainbow_r, vmax=100., vmin=0.)

c = ax.imshow(batgrid, vmin=0., vmax=100, aspect='auto', interpolation='none',
                cmap=cm.jet_r)

ax.set_xlabel('Days')
ax.set_ylabel('Time of Day')

#ax.set_xlim((0, 366))
#ax.set_ylim((-288, 0))

ax.set_yticks(numpy.arange(0, 25, 3)*12)
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

#c=ax.scatter(DOY, TOD, c=numpy.array(ssids), edgecolor='none', marker='s', 
#             s=1, cmap=cm.rainbow)

c = ax.imshow(ssidgrid, interpolation='none', aspect='auto', cmap=cm.rainbow_r)

ax.set_xlabel('Day of Year')
ax.set_ylabel('Time of Day')

#ax.set_xlim((0, 366))
#ax.set_ylim((-288, 0))

ax.set_yticks(numpy.arange(0, 25, 3)*12)
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
#ax = fig.add_axes([0.05, 0.1, 0.7, 0.8])
ax = fig.add_subplot(111)
histbins = numpy.arange(0, 2016, 3)

counts = [wk2num(g) for g in DATA.index]
ax.hist(counts, bins=histbins, histtype='step', label='ALL')

#H = AWAKE.groupby('SSID')
##H = DATA.groupby('SSID')

#for g in H.groups.keys():
#    counts = [wk2num(v) for v in H.get_group(g).index]
#    ax.hist(counts, bins=histbins, histtype='step', label=g)

ax.set_xticks(numpy.arange(7)*288)
ax.set_xticks((numpy.arange(7)+.5)*288, minor=True)
ax.set_xticklabels([])
ax.set_xticklabels(calendar.day_name[0:7], minor=True)
ax.set_xlim((0, 2016))
ax.set_yticks([])
ax.set_ylim(0, ax.get_ylim()[1]*1.1)

#ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=10, 
#          title="SSID", frameon=False)

ax.grid('on', which='major')
ax.set_xlabel('Day of Week')
ax.set_ylabel('Computer Useage')
#plt.suptitle('Computer Useage by Day of Week and SSID')

plt.savefig(os.path.join(dbdir, 'weekstats.png'), dpi=300)

plt.close('all')
