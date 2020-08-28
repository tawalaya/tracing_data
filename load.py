#! /usr/bin/env python3

import pandas as pd
import numpy as np
import json
from datetime import datetime

def load():
    #this is ugly but i was lazy
    experimentes = {
        "baseline":("data/activations/activation_list_baseline_result.json","data/activations/fetchImages_baseline_result.json","data/performance/baseline_ow_logs.json"),
        "provider":("data/activations/activation_list_provider_side_result.json","data/activations/fetchImages_provider_side_result.json","data/performance/provider_side_ow_logs.json"),
        "function":("data/activations/activation_list_function_side_result.json","data/activations/fetchImages_function_side_result.json","data/performance/function_side_ow_logs.json")
    }

    activations = None
    performance = None
     
    for e in experimentes.keys():
        a = loadActivations(experimentes[e][0],e)
        b = loadActivations(experimentes[e][1],e)
        activation = pd.concat([a,b], sort=True)

        perf = loadPerf(experimentes[e][2],e)

        if (activations is None):
            activations = activation
        else:
            activations = pd.concat([activations, activation], sort=True)

        if (performance is None):
            performance = perf
        else:
            performance = pd.concat([performance, perf], sort=True)
    
    return activations,performance

def loadActivations(fname,ename):
    activations = pd.read_json(fname)
    activations["experiment"] = ename
    return activations

def loadPerf(fname,ename):
    with open(fname) as f:
        
        X = json.load(f)
        f.close()

        data = []
        for node in X.keys():
            for t in X[node].keys():
                        flat = list(map(lambda x:tuple(x.split()),X[node][t]+["node "+node]+["timestamp "+t]))
                        data.append(node_cpu(flat)+sumkey('node_disk_io_now',flat)+sumkey('node_network_receive_bytes',flat)+sumkey('node_network_transmit_bytes',flat)+time('timestamp',flat)+eql('node_load1',flat)+eql('node_load15',flat)+id('node_memory_Active',flat)+id('node_memory_MemFree',flat)+id('node_memory_MemTotal',flat)+eql('node',flat,False))

        frame = {}
        for d in data:
            for k in d:
                if k[0] not in frame:
                    frame[k[0]] = []
                frame[k[0]].append(k[1])
    perf = pd.DataFrame.from_dict(frame)
    perf["experiment"] = ename
    perf = perf.set_index("timestamp")
    return perf

#parsing magic ahead

from itertools import groupby
def node_cpu(l):
    node_cpu = list(map(lambda x: ("cpu_"+x[0][9:-1].split(",")[1][6:-1],float(x[1])),filter(lambda x:'node_cpu' in x[0],l)))
    node_cpu.sort(key=lambda x:x[0])
    return list(map(lambda x:(x[0],sum(x[1])),map(lambda x:(x[0],map(lambda y:y[1],x[1])),groupby(node_cpu,lambda x: x[0]))))
    

def sumkey(k,l):
    return [(k,sum(map(lambda x:float(x[1]),filter(lambda x:k in x[0],l))))]
def id(k,l):
    return list(map(lambda x:(x[0],float(x[1])),filter(lambda x:k in x[0],l)))
def eql(k,l,c=True):
    if c:
        return list(map(lambda x:(x[0],float(x[1])),filter(lambda x:k == x[0],l)))
    else:
        return list(filter(lambda x:k == x[0],l))
def time(k,l):
    return list(map(lambda x:(x[0],datetime.fromisoformat(x[1][:-1])),filter(lambda x:k in x[0],l)))