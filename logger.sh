#! /bin/bash

network_SSID="$(/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | sed -e "s/^  *SSID: //p" -e d)"

#echo `date` ${USER} '"'$network_SSID'"' standalone >> ${HOME}/.logstats/wakelog.dat
date >> ${HOME}/.logstats/batlog.dat
echo "| WiFi" `/sbin/ifconfig en0 | grep "status"` " with SSID ${network_SSID}" >> ${HOME}/.logstats/batlog.dat
echo "| Ethernet" `/sbin/ifconfig en4 | grep "status"` >> ${HOME}/.logstats/batlog.dat
/usr/sbin/ioreg -l | egrep "LegacyBatteryInfo" >> ${HOME}/.logstats/batlog.dat
/usr/sbin/ioreg -l | grep "class AppleBacklightDisplay" -A 12 | grep "IOPowerManagement" >> ${HOME}/.logstats/batlog.dat
