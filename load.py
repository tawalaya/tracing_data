#! /usr/bin/env python3

import pandas as pd
import numpy as np
import json
from datetime import datetime

import glob


def load():

    activations = None
    performance = None

    for f in glob.glob("data/*"):
        ename = f
        for a in glob.glob(f+"/activations/*.json"):
            fname = a[a.rindex("/")+1:]
            typeName =  "_".join(fname.split("_")[1:-1])
    
            activation = loadActivations(a,typeName,ename)
            if (activations is None):
                activations = activation
            else:
                activations = pd.concat([activations, activation], sort=True)

        for a in glob.glob(f+"/performance/*.json"):
            fname = a[a.rindex("/")+1:]
            typeName =  "_".join(fname.split("_")[:-2])
            
            perf = loadPerf(a,typeName,ename)

            if (performance is None):
                performance = perf
            else:
                performance = pd.concat([performance, perf], sort=True)
            
    
    return activations,performance

def loadActivations(fname,typeName,ename):
    activations = pd.read_json(fname)
    activations["experiment"] = typeName
    activations["enviroment"] = ename
    return activations

def loadPerf(fname,typeName,ename):
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
    perf["experiment"] = typeName
    perf["enviroment"] = ename
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