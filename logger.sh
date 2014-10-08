#! /bin/bash

network_SSID="$(/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | sed -e "s/^  *SSID: //p" -e d)"

echo `date` ${USER} '"'$network_SSID'"' >> ${HOME}/.logstats/wakelog.dat
date >> ${HOME}/.logstats/batlog.dat
/usr/sbin/ioreg -l | egrep "LegacyBatteryInfo" >> ${HOME}/.logstats/batlog.dat
