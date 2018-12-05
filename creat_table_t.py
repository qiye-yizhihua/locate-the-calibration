#!/root/anaconda2/bin/python
#coding=utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')
#创建uli的转移矩阵表
def create_table(hive_table='xxx.uli_nextuli_cnt'):
    creat_table_sql = 'CREATE TABLE `%s` (`uli` string,`nextuli` string,`uli_cnt` int);'%hive_table
    ct_cmd = "hive -e \'" + creat_table_sql+"\'"
    print(ct_cmd)
    os.system(ct_cmd)
#创建带经纬度的转移矩阵表
def create_ulilnglat_table(hive_table='xxx.uli_nextuli_lnglat_cnt_n1'):
    creat_table_sql = 'CREATE TABLE `%s` (`uli` string,`long` string,`lat` string,`uliname` string,`next_uli` string,`next_long` string,`next_lat` string,`label` int,`next_uliname` string,`uli_count` int);'%hive_table
    ct_cmd = "hive -e \'" + creat_table_sql+"\'"
    print(ct_cmd)
    os.system(ct_cmd)

if __name__ == '__main__':
    #create_table(hive_table='xxx.uli_nextuli_cnt_1')
    #create_ulilnglat_table('xxx.uli_nextuli_lnglat_cnt_n1_1')
    print('create tabel!!')
