# -*- coding: utf-8 -*-
"""
Created on Wed Jul  5 11:14:19 2023

@author: Aaron
"""


import pickle
import glob
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime




def load_data(fp):
    files = glob.glob(fp)
    return files

def parse_data(files):
    res = []
    for file in files:
        with open(file, 'rb') as temp:
            res.append(pickle.load(temp))
            temp.close() 
    return res

def del_incomplete_runs(res):
    FullFailure_ls = []
    Full_idx = []
    MPCFailure_ls = []
    MPC_idx = []
    data = []
    data_idx = []
    
    index = 0
    for item in res:
        if type(item['full-unassigned']) is AttributeError:
            item['res_idx'] = index
            FullFailure_ls.append(item)
            #Full_idx.append(index)
        if type(item['sliding']) is AttributeError:
            item['res_idx'] = index
            MPCFailure_ls.append(item)
            #MPC_idx.append(index)
        if type(item['full-unassigned']) is not AttributeError and type(item['sliding']) is not AttributeError:
            item['res_idx'] = index
            data.append(item)
            #data_idx.append(index)
                
        index += 1
                
    return data, FullFailure_ls, MPCFailure_ls

def del_failed_runs(data):
    Full_status_error = []
    Full_status_9 = []
    
    MPC_status_9 = []
    completed_data = []
    
    idx = 0
    for item in data:
        if 'StatusCode' in item['full'].columns:
            Full_status_error.append(item)
            if item['full']['StatusCode'][0] == 9:
                Full_status_9.append(item)
        else:
            completed_data.append(item)
        
        if 'StatusCode' in item['sliding'].columns:
            MPC_status_9.append(item)
            
        idx += 1
    
    return completed_data, Full_status_error, Full_status_9, MPC_status_9

def extract_run_params(data):
    numSpots = []
    buffer = []
    weightCruising = []
    weightDblPark = []
    zeta = []
    numVeh = []
    tau = []
    rho = []
    nu = []
    received_delta = []
    
    for run in data:
        numSpots.append(run['spec']['numSpots'])
        buffer.append(run['spec']['buffer'])
        weightCruising.append(run['spec']['weightCruising'])
        weightDblPark.append(run['spec']['weightDoubleParking'])
        zeta.append(run['spec']['zeta'])
        numVeh.append(len(run['FCFS']))
        tau.append(run['spec']['tau'])
        rho.append(run['spec']['rho'])
        nu.append(run['spec']['nu'])
        received_delta.append(run['spec']['received_delta'])
        run_params = pd.DataFrame(list(zip(numSpots, numVeh, zeta, buffer, weightDblPark, weightCruising, tau, rho, nu, received_delta)),
                                  columns = ['numSpots', 'numVeh', 'zeta', 'buffer', 'weightDblPark', 'weightCruising', 'tau', 'rho', 'nu', 'received_delta'])
    
    return run_params

def plot_unassigned(data):
    FCFS_unassigned = []
    Full_unassigned = []
    MPC_unassigned = []
    
    for i in range(len(data)):
        FCFS_unassigned.append(data[i]['FCFS-unassigned'])
        Full_unassigned.append(data[i]['full-unassigned'])
        MPC_unassigned.append(data[i]['sliding-unassigned'])
        
    x = range(len(data))
    x = [item['OG_index'] for item in completed_data]
    #x = range(min(x), max(x), 5)
    #x.sort()
    plt.scatter(x, FCFS_unassigned, label = 'FCFS')
    plt.scatter(x, Full_unassigned, label = 'Full')
    plt.scatter(x, MPC_unassigned, label = 'MPC')
    plt.legend()
    plt.xticks(range(min(x), max(x), 25))
    plt.xlabel('res #')
    plt.ylabel('unassigned minutes of service')
    plt.show()
    
    diff_FCFS_Full = np.subtract(FCFS_unassigned, Full_unassigned)
    diff_FCFS_MPC = np.subtract(FCFS_unassigned, MPC_unassigned)
    diff_MPC_Full = np.subtract(MPC_unassigned, Full_unassigned)
    
    plt.scatter(x, diff_FCFS_Full, label = 'FCFS-Full')
    plt.scatter(x, diff_FCFS_MPC, label = 'FCFS-MPC')
    plt.scatter(x, diff_MPC_Full, label = 'MPC-Full')
    plt.legend()
    plt.xticks(range(min(x), max(x), 25))
    plt.xlabel('OG run #')
    plt.ylabel('unassigned minutes of service')
    plt.show()
    

    return FCFS_unassigned, Full_unassigned, MPC_unassigned, diff_FCFS_Full, diff_FCFS_MPC, diff_MPC_Full


plt.rcParams['figure.dpi'] = 500
file_path = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2023-12-15_Aaron Result/*.dat'
files = load_data(file_path)
res = parse_data(files)
data, FullFailure_ls, MPCFailure_ls = del_incomplete_runs(res)
completed_data, Full_status_error, Full_status_9, MPC_status_9 = del_failed_runs(data)

# data = res
run_params = extract_run_params(data)

FCFS_unassigned, Full_unassigned, MPC_unassigned, diff_FCFS_Full, diff_FCFS_MPC, diff_MPC_Full = plot_unassigned(completed_data)





