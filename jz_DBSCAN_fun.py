#!/root/anaconda2/bin/python
#coding=utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')

import csv
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
#from math import *
from math import cos, sin, atan2, sqrt, pi ,radians, degrees
#from shapely.geometry  import MultiPoint,Polygon
#from  geopy.distance import great_circle

#DBSCAN密度聚类算法，返回最大簇的值

def gain_result_db(data_arr,R=5,samples=3):
    eps_=float(R)/6371.0
    samples_ = samples
    initdata = pd.DataFrame(data_arr)
    initdata.columns = ['lng','lat']
    #print(initdata)
    initdata['lat']=initdata['lat'].astype('float')
    initdata['lng']=initdata['lng'].astype('float')
    scatterData = initdata.as_matrix(columns=['lat','lng'])
    modle = DBSCAN(eps=eps_,min_samples=samples_,algorithm='ball_tree',metric="haversine")  # dbscan
    resluts = modle.fit(np.radians(scatterData))
    #labels = resluts.labels_
    #print('labels\n', labels)
    #print('core_sample_indices_\n',resluts.core_sample_indices_)
    #print('components_\n', resluts.components_)	
    cluster_labels = resluts.labels_
    num_clusters = len(set(cluster_labels))
    clusters = pd.Series([scatterData[cluster_labels == n] for n in range(num_clusters)])
    max_data_index = 0;
    for n in range(0,num_clusters):
        if len(clusters[n])>len(clusters[max_data_index]):
            max_data_index = n
            #print('max_data_index:',len(clusters[max_data_index]))
    return scatterData[cluster_labels == max_data_index]


