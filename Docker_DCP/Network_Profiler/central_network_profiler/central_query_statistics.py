"""
 ** Copyright (c) 2017, Autonomous Networks Research Group. All rights reserved.
 **     contributor: Quynh Nguyen, Bhaskar Krishnamachari
 **     Read license file in main directory for more details
"""
import os
import csv
import pymongo
from pymongo import MongoClient
import pandas as pd
import json
import sys
import numpy as np


class central_query_statistics():
    def __init__(self):
        self.client_mongo = None
        self.db = None
    def do_query_quaratic(self,source,destination,file_size):
        self.client_mongo = MongoClient('mongodb://localhost:27017/')
        self.db = self.client_mongo.central_network_profiler
        predicted = None
        relation_info = 'central_input/nodes.txt'
        df_rel = pd.read_csv(relation_info, header=0, delimiter=',',index_col=0)
        dict_rel = df_rel.T.to_dict('list')
        sourceIP = dict_rel.get(source)[0].split('@')[1]
        destinationIP = dict_rel.get(destination)[0].split('@')[1]
        cursor = self.db['quadratic_parameters'].find({"Source[IP]":sourceIP,"Destination[IP]":destinationIP},{"Parameters":1}).sort([('Time_Stamp[UTC]', -1)]).limit(1)
        try:
            record = cursor.next()
            quadratic = record['Parameters']
            quadratic = quadratic.split(" ")
            quadratic = [float(x) for x in quadratic]
            predicted = np.square(file_size*8)*quadratic[0]+file_size*8*quadratic[1]+quadratic[2]#file_size[Bytes]
        except StopIteration:
            print('No valid links')
            exit()
        return predicted

if __name__ == '__main__':
    if len(sys.argv)<3:
        print('Please run the script as following: python central_query_statistics Source_Tag Destination_Tag FileSize[KB]')
        exit()
    source = sys.argv[1]
    destination = sys.argv[2]
    file_size = int(sys.argv[3])
    d = central_query_statistics()
    predicted = d.do_query_quaratic(source,destination,file_size)
    msg = "Expected latency is %f [ms]" %predicted
    print(msg)
    #d.do_update_iperf_manual() not yet needed

