#!/root/anaconda2/bin/python
#coding=utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
import time
import creat_table_t as ct
import numpy as np
import pandas as pd

'''
获取一天的转移矩阵数据
'''
# hive优化参数设置
set_hive = '''set mapred.job.queue.name=chanct;set hive.map.aggr=true;set hive.exec.parallel=true;set hive.exec.reducers.max=21;set mapred.max.split.size=1024000000;set mapred.max.split.size.per.node=1024000000;set mapred.max.split.size.per.rack=1024000000;set hive.exec.dynamic.partition.mode=nonstrict;set hive.exec.mode.local.auto.inputbytes.max=33244326;'''

# 获取转移矩阵数据
def get_uli_from_hive(date,lingchen_time,hive_table='default.uli_nextuli_cnt'):
    get_uli_sql = '''add jar /home/chanct/rktj/fgw/jars/udf-fgw.jar;create temporary function isphone as "com.chanct.udf.IsPhone";insert overwrite table %s select a.uli,a.nextuli,count(a.appear_time) as uli_cnt from (select distinct t.uli,t.nextuli,t.appear_time from mdatabase.t_person_trajectory t  where  t.date=%s and t.duration<=30 and t.cdrtype<>1 and isphone(msisdn) and t.cdrtype<>2 and t.appear_time<>%s and split(uli,"-")[1]=split(nextuli,"-")[1] and uli is not null and nextuli is not null)a group by a.uli,a.nextuli having uli_cnt>10;'''%(hive_table,date,lingchen_time)
    get_uli_cmd = "hive -e \'" + set_hive + get_uli_sql + "\'"
    print(get_uli_cmd)
    os.system(get_uli_cmd)

#保持为文本文件
def get_data_to_txt(wenjianming,hive_table):
    get_uli_longlat_sql = 'select * from %s where uli!=nextuli and uli_cnt>=20;' %hive_table
    get_ulilonglat_cmd = "hive -e \'" + set_hive + get_uli_longlat_sql + "\'" +" >> "+wenjianming
    if not os.path.exists(wenjianming):
        os.system(get_ulilonglat_cmd)
    else:
        os.remove(wenjianming)
        os.system(get_ulilonglat_cmd)

def get_jwd(path1,path2):
    df_zyjuz = pd.read_csv(path1,usecols=[0,1,2],names=['uli','nextuli','cnt'],sep='\t')
    df_ulidata = pd.read_csv(path2,usecols=[0,1,2,3],names=['uli','long','lat','address'],sep='\t')
    df_nextulidata  = df_ulidata.copy()
    df_nextulidata.columns = ['nextuli','nextlong','nextlat','nextaddress']
    df_merge1 = pd.merge(df_zyjuz,df_ulidata,how='inner',on='uli')
    df_merge2 = pd.merge(df_merge1,df_nextulidata,how='inner',on='nextuli')
    df_ = df_merge2[['uli','long','lat','address','nextuli','nextlong','nextlat','nextaddress','cnt']]
    return df_
    

date_s = int(sys.argv[1])
date_e = date_s+1
if __name__ == '__main__':
    hive_table0 = 'default.xx_ulizhuanyijuzhen_%s'%str(date_s)
    ct.create_table(hive_table0)
    wenjianming = './middle_data/ulizhuanyijuzhen_%s.txt'%str(date_s)
    uli_database = 'ulidatabase.txt'
    #按天获取转移矩阵数据
    for t in xrange(date_s,date_e,1):
        date = str(t)
        print '--->',date
        ts = time.strptime(date,'%Y%m%d')
        time_stamp = int(time.mktime(ts))
        get_uli_from_hive(date,time_stamp,hive_table0)
    get_data_to_txt(wenjianming,hive_table0)
    df_zyjz =  get_jwd(wenjianming,uli_database)
    df_zyjz.to_csv('./middle_data/ulizhuanyijuzhen_lnglat_%s.txt'%str(date_s),sep='\t',index=None,header=None,encoding='utf-8')
