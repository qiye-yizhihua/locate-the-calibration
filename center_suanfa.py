#!/root/anaconda2/bin/python
#coding=utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')

from math import cos, sin, atan2, sqrt, pi ,radians, degrees
#求多点中心值算法
def center_geolocation(geolocations):
    x = 0
    y = 0
    z = 0
    lenth = len(geolocations)
    for lon, lat in geolocations:
        lon = radians(float(lon))
        lat = radians(float(lat))
        x += cos(lat) * cos(lon)
        y += cos(lat) * sin(lon)
        z += sin(lat)
    x = float(x / lenth)
    y = float(y / lenth)
    z = float(z / lenth)
    return (degrees(atan2(y, x)), degrees(atan2(z, sqrt(x * x + y * y))))
#求多点加权中心值算法
def jiaquan_center_jwd(lng_lat_cnt,sum_zs):
    x = 0
    y = 0
    z = 0
    sum_zs = float(sum_zs)
    lenth = len(lng_lat_cnt)
    if lenth >0:    
      for lon, lat, cnt in lng_lat_cnt:
        lon = radians(float(lon))
        lat = radians(float(lat))
        cnt = float(cnt)
        x += cos(lat) * cos(lon) * cnt / sum_zs
        y += cos(lat) * sin(lon) * cnt / sum_zs
        z += sin(lat) * cnt / sum_zs
      x = float(x / lenth)
      y = float(y / lenth)
      z = float(z / lenth)
    return (degrees(atan2(y, x)), degrees(atan2(z, sqrt(x * x + y * y))))


