#!/root/anaconda2/bin/python
#coding=utf-8
import csv
import creat_table_t as ct
import get_data_jzjz as gj
from multiprocessing import Pool
import sys
import time
import numpy as np
import pandas as pd
import geoutils as gt
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from center_suanfa import center_geolocation
from center_suanfa import jiaquan_center_jwd

def distance_list(distance,dict_cs):
    if distance<1000:
        dict_cs['0-1000'] += 1
    elif distance<2000 and distance>=1000:
        dict_cs['1000-2000'] += 1
    elif distance<3000 and distance>=2000:
        dict_cs['2000-3000'] += 1
    elif distance<4000 and distance>=3000:
        dict_cs['3000-4000'] += 1
    elif distance<5000 and distance>=4000:
        dict_cs['4000-5000'] += 1
    else:
        dict_cs['5000-inf'] += 1
    return dict_cs

        plt.figure(figsize=(15,15))
        #print(u'-->当前uli:%s'%u)
        #print(u'-->红点与绿点的距离:%s米。'%distance1)
        #print(u'-->黑点与绿点的距离:%s米。'%distancejq)

        plt.scatter(n_long_n,n_lat_n,c='b',s=20)
        plt.scatter(new_long,new_lat,s=60,c='r')
        plt.scatter(long1,lat1,s=70,c='g')
        plt.scatter(newjq_long,newjq_lat,c='k',s=60)

        for x_y, c in zip(lng_lat_n1, n_count1):
            x = float(x_y.split('_')[0])
            y = float(x_y.split('_')[1])
            plt.annotate(
                '(%s)' %(c),
                xy=(x, y),
                xytext=(0, -10),
                textcoords='offset points',
                ha='center',
                va='top')
        def to_percent(temp, position):
            return '%.3f'%(temp)
        plt.gca().yaxis.set_major_formatter(FuncFormatter(to_percent))
        plt.gca().xaxis.set_major_formatter(FuncFormatter(to_percent))
        plt.savefig('./save_tupian/uli_%s_%s-%s.jpg'%(u,distance_cs_min,distance_cs_max,))

def jizhang_to_txt(df_n,newjq_long,newjq_lat,distancejq,wenjian_name):
    df_totxt=df_n[['uli','long','lat','uliname']].drop_duplicates()
    df_totxt['jq_long'] = newjq_long
    df_totxt['jq_lat'] = newjq_lat
    df_totxt['distance_jq']=distancejq
    df_totxt.to_csv('./new_data/%s.txt'%(wenjian_name) ,index=None,header=None,sep='\t',mode='a')

def uli_distance_tj(df_new,uli_list,wenjian_name,flge):
   count1 = 0
   max_count = 100
   distance_cs_min = 5000
   distance_cs_max = 10000000
   for u in uli_list[:]:  #uli_list is uli list
       print(u)
       #u='460-00-17082-2'
       df_n=df_new[df_new.uli==u]
       if len(df_n.lng_lat_n.unique())>=3:
           #print('---->',len(df_n.lng_lat_n.unique()))
           long1=df_n.long.iloc[0]
           lat1 = df_n.lat.iloc[0]
           n_long_n = df_n['next_long']
           df_n1=df_n.groupby('lng_lat_n').z_count.sum().reset_index()
           n_count1 = df_n1['z_count']
           lng_lat_n1 = df_n1['lng_lat_n']
           df_n1['n_long'] = df_n1.lng_lat_n.apply(lambda x:x.split('_')[0])
           df_n1['n_lat'] = df_n1.lng_lat_n.apply(lambda x:x.split('_')[1])
           n_long_jq = df_n1['n_long']
           n_lat_jq = df_n1['n_lat']
           lng_lat_cnt = zip(n_long_jq,n_lat_jq,n_count1)
           sum_zs=df_n.z_count.sum()
           newjq_long,newjq_lat=jiaquan_center_jwd(lng_lat_cnt,sum_zs)
           ##
           #distancejq_calc = gt.calcDistance(newjq_long,newjq_lat,long1,lat1)
           #jqcenter_jwd_calc =distance_list(distancejq_calc,dict_1)
           ##
           distancejq=gt.haversine(newjq_long,newjq_lat,long1,lat1)
           #jqcenter_jwd=distance_list(distancejq,dict_2)
           if flge == False:
               jizhang_to_txt(df_n,newjq_long,newjq_lat,distancejq,wenjian_name)
           else:
               if distancejq<distance_cs_max and distancejq>distance_cs_min:
                   plot_scatter(df_n,u,n_long_n,n_lat_n,distance1,new_long,new_lat,distance_cs_min,distance_cs_max,long1,lat1,newjq_long,newjq_lat,distancejq,n_count1,lng_lat_n1)
                   count1+=1
                   if count1>max_count:
                       break #for yujushiyingyong break

       else:
           pass
   return jqcenter_jwd


