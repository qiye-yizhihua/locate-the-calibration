#!/root/anaconda2/bin/python
#coding=utf-8
import csv
#import creat_table_t as ct #导入创建表模块
#import get_data_jzjz as gj #导入获取表模块
import jz_DBSCAN_fun as dbf #导入DBSCAN模块
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
from center_suanfa import jiaquan_center_jwd #导入加权平均值模块


def get_data_to_df(path):
    '''导入固定的字段转移表的数据，返回为DataFrame'''
    #path = u'uli_longlat_count_n1.txt'
    df = pd.read_csv(path,header=None,sep='\t',usecols=[0,1,2,3,4,5,6,7,8,9],names=['uli','long','lat','uliname','nextuli','next_long','next_lat','next_label','next_uliname','z_count'])
    df_new = df.dropna(subset=['uli','long','lat','nextuli','next_long','next_lat'],axis=0).drop_duplicates()
    df_new['lng_lat_n'] = df_new.next_long.astype('str')+'_'+df_new.next_lat.astype('str')
    df_new = df_new.sort_values('uli')
    df_new =  df_new[df_new.next_label==1]
    return df_new

#########################################################################

def uli_jq_jwd_v1(df_n,df_db):
    df_n=df_n.groupby('lng_lat_n').z_count.sum().reset_index()
    df_n1 = pd.merge(df_db,df_n,on='lng_lat_n',how='inner')
    n_count1 = df_n1['z_count']
    df_n1['n_long'] = df_n1.lng_lat_n.apply(lambda x:x.split('_')[0])
    df_n1['n_lat'] = df_n1.lng_lat_n.apply(lambda x:x.split('_')[1])
    n_long_jq = df_n1['n_long']
    n_lat_jq = df_n1['n_lat']
    lng_lat_cnt = zip(n_long_jq,n_lat_jq,n_count1)
    sum_zs=df_n.z_count.sum()
    newjq_long,newjq_lat=jiaquan_center_jwd(lng_lat_cnt,sum_zs)
    return newjq_long,newjq_lat

def julei_fx_v1(df_n,uli_o):
    '''
    对每个服务小区uli进行DBSCAN聚类
    返回每个服务小区对应的label
    0：原始坐标点在最大簇内的标签
    1：校准坐标点在最大簇内的标签
    2：原始坐标点和校准坐标点都不在最大簇内的标签
    3：没有最大聚类簇的uli的标签
    4：邻近小区坐标点位置小于3个的uli标签
    '''
    if len(df_n.lng_lat_n.unique())>=3:
        try:
            #print(len(df_n.lng_lat_n.unique()))
            df_ysjwd = df_n[['long','lat']].drop_duplicates()
            long_o = float(df_ysjwd.long.iloc[0])
            lat_o = float(df_ysjwd.lat.iloc[0])
            df_nextjwd = df_n[['next_long','next_lat']].drop_duplicates()
            result_maxcu=dbf.gain_result_db(df_nextjwd,R=3,samples=3)#DBSCAN聚类，默认半径为5km，返回最大簇的标签

            df_result = pd.DataFrame(result_maxcu,columns=['lat_','long_'])
            df_result['lng_lat_n'] = df_result.long_.astype('str')+'_'+df_result.lat_.astype('str')
            df_result=df_result.drop(['long_','lat_'],axis=1)
            long_jq,lat_jq = uli_jq_jwd_v1(df_n,df_result) #最大簇进行加权校准

            max_lat_long = np.amax(result_maxcu,axis=0)
            max_lat,max_long = max_lat_long[0],max_lat_long[1]#簇的经纬度最大值
            min_lat_long = np.amin(result_maxcu,axis=0)
            min_lat,min_long = min_lat_long[0],min_lat_long[1]#簇的经纬度最小值
            #print(min_long,long_o,max_long)
            #print(min_lat,lat_o,max_lat)
            if min_long<long_o<max_long and min_lat<lat_o<max_lat:
               return [uli_o,'0']
            elif min_long<long_jq<max_long and min_lat<lat_jq<max_lat:
               dist = gt.haversine(long_jq,lat_jq,long_o,lat_o)
               if dist>5000:
                   return [uli_o,'1_dy5km']
               else:
                   return [uli_o,'1_xy5km']
            else:
               return [uli_o,'2']
        except:
            pass
            return [uli_o,'3']
    else:
        return [uli_o,'4']

def data_to_dict(filename):
    '''把DataFrame变为dict'''
    dict_uli = {}
    data_txt = csv.reader(file(filename, 'r'), delimiter='\t')
    for line in data_txt:
        if dict_uli.has_key(line[0]) == False:
            dict_uli[line[0]] = [line[:]]
        else:
            dict_uli[line[0]].append(line[:])
    return dict_uli

def data_to_dict_delold(filename,filename1,flag):
    '''把DataFrame变为dict,删除旧表中的uli'''
    df_uli = pd.read_csv(filename1,sep='\t',usecols=[0],names=['uli'])
    uli_set = set(list(df_uli.uli.unique())[:])
    print(len(df_uli.uli.unique()))
    #print(uli_set)
    dict_uli = {}
    data_txt = csv.reader(file(filename, 'r'), delimiter='\t')
    c = 0
    for line in data_txt:
        if flag == True:
            if line[0] not in uli_set:
                c+=1
                if dict_uli.has_key(line[0]) == False:
                    dict_uli[line[0]] = [line[:]]
                else:  
                  dict_uli[line[0]].append(line[:])
        else:
            if line[0] in uli_set:
                c+=1
                if dict_uli.has_key(line[0]) == False:
                    dict_uli[line[0]] = [line[:]]
                else:
                    dict_uli[line[0]].append(line[:])
    #print(c)
    return dict_uli

def to_df(v):
    '''字典的value变为DF形式'''
    df=pd.DataFrame(v,columns=['uli','long','lat','address','nextuli','next_long','next_lat','next_address','z_count'])
    df_n = df.dropna(subset=['uli','long','lat','nextuli','next_long','next_lat'],axis=0).drop_duplicates()
    df_n['lng_lat_n'] = df_n.next_long.astype('str')+'_'+df_n.next_lat.astype('str')
    return df_n
#传入校准数据的时间
dates = int(sys.argv[1])
if __name__ =='__main__':
    t1 = time.time()
    wenjianming='./middle_data/ulizhuanyijuzhen_lnglat_%s.txt'%dates
    result=data_to_dict(wenjianming） 
    result_dict = result
    pool=Pool(processes=int(15)) #创建资源池
    print('end!!')
    jieguo = []
    for k,v in result_dict.items():   
       print(k) #k就是服务小区uli
       df_n=to_df(v) #邻近小区
       #jieguo.append(julei_fx_v1(df_n,k))
       jieguo.append(pool.apply_async(julei_fx_v1,(df_n,k)))
    pool.close()
    pool.join()
    uli_list1 = []
    for res in jieguo:
        uli_list1.append(res.get())
    df_list = pd.DataFrame(uli_list1,columns=['uli','label'])
    df_list.to_csv('./middle_data/dbscan_jiaozhun_reslut_%s.txt'%dates,index=None,sep='\t')
    #print(jieguo) 
    print '0-->',len([True  for i in jieguo if i.get()[1]=='0'])
    print '1-->',len([True  for i in jieguo if i.get()[1]=='1'])
    print '2-->',len([True  for i in jieguo if i.get()[1]=='2'])
    print '3-->',len([True  for i in jieguo if i.get()[1]=='3'])
    print '4-->',len([True  for i in jieguo if i.get()[1]=='4'])
    t2 = time.time()
    print('time::::',t2-t1) 
