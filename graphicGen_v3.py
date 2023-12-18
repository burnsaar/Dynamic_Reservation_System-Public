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
    plt.figure()
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

def get_analysis_data(run_params_complete, FCFS_unassigned, Full_unassigned,
                                  MPC_unassigned, diff_FCFS_Full, diff_FCFS_MPC, diff_MPC_Full):
    analysis_data = run_params_complete
    analysis_data['FCFS unassigned'] = FCFS_unassigned
    analysis_data['Full unassigned'] = Full_unassigned
    analysis_data['MPC unassigned'] = MPC_unassigned
    analysis_data['diff_FCFS_Full'] = diff_FCFS_Full
    analysis_data['diff_FCFS_MPC'] = diff_FCFS_MPC
    analysis_data['diff_MPC_Full'] = diff_MPC_Full
    
    return analysis_data

def get_high_demand(analysis_data):
    analysis_data_high_demand = analysis_data[(analysis_data['numVeh'] == 33) |
                                              (analysis_data['numVeh'] == 66)]
    return analysis_data_high_demand

def get_low_demand(analysis_data):
    analysis_data_low_demand = analysis_data[((analysis_data['numVeh'] == 11) & (analysis_data['numSpots'] == 1)) |
                                             ((analysis_data['numVeh'] == 22) & (analysis_data['numSpots'] == 2)) |
                                             ((analysis_data['numVeh'] == 55) & (analysis_data['numSpots'] == 5))]
    return analysis_data_low_demand

def get_X_parking_spaces(analysis_data, numSpots):
    numSpots_data = analysis_data[analysis_data['numSpots'] == numSpots]
    return numSpots_data

def get_zeta_data(analysis_data, zeta):
    zeta_data = analysis_data[analysis_data['zeta'] == zeta]
    return zeta_data

def get_received_data(analysis_data, received_leadtime):
    received_leadtime_data = analysis_data[analysis_data['received_delta'] == received_leadtime]
    return received_leadtime_data

def get_rho_data(analysis_data, rho):
    rho_data = analysis_data[analysis_data['rho'] == rho]
    return rho_data

def get_nu_data(analysis_data, nu):
    nu_data = analysis_data[analysis_data['nu'] == nu]
    return nu_data

def get_subset_stages(analysis_data):
    analysis_data_sub_2 = analysis_data[(analysis_data['received_delta'] == 300) &
                                        (analysis_data['rho'] == 0) & 
                                        (analysis_data['nu'] == 0)]
    
    analysis_data_sub_3 = analysis_data[(analysis_data['received_delta'] == -1) &
                                        (analysis_data['rho'] == 0) & 
                                        (analysis_data['nu'] == 0)]
    
    analysis_data_sub_4 = analysis_data[(analysis_data['received_delta'] == -1) &
                                        (analysis_data['rho'] == 60) & 
                                        (analysis_data['nu'] == 0)]
    
    analysis_data_sub_5 = analysis_data[(analysis_data['received_delta'] == -1) &
                                        (analysis_data['rho'] == 60) & 
                                        (analysis_data['nu'] == 60)]
    
    return analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5

def gen_boxplot(analysis_data, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str):
    #boxplot_data
    Stage_1_data = pd.DataFrame(columns = ['Stage', 'Diff Unassigned'])
    Stage_1_data['Diff Unassigned'] = analysis_data['diff_FCFS_Full']
    Stage_1_data['Stage'] = 'Full Day'

    Stage_2_data = pd.DataFrame(columns = ['Stage', 'Diff Unassigned'])
    Stage_2_data['Diff Unassigned'] = analysis_data_sub_2['diff_FCFS_MPC']
    Stage_2_data['Stage'] = 'BFMPC'

    Stage_3_data = pd.DataFrame(columns = ['Stage', 'Diff Unassigned'])
    Stage_3_data['Diff Unassigned'] = analysis_data_sub_3['diff_FCFS_MPC']
    Stage_3_data['Stage'] = 'SLT'

    Stage_4_data = pd.DataFrame(columns = ['Stage', 'Diff Unassigned'])
    Stage_4_data['Diff Unassigned'] = analysis_data_sub_4['diff_FCFS_MPC']
    Stage_4_data['Stage'] = 'GP'

    Stage_5_data = pd.DataFrame(columns = ['Stage', 'Diff Unassigned'])
    Stage_5_data['Diff Unassigned'] = analysis_data_sub_5['diff_FCFS_MPC']
    Stage_5_data['Stage'] = 'GAT'

    boxplot_data = pd.concat([Stage_1_data, Stage_2_data, Stage_3_data, Stage_4_data, Stage_5_data])


    #boxplot for stage 1, full day versus FCFS
    plt.figure()
    sns.boxplot(data = boxplot_data, x = 'Stage', y = 'Diff Unassigned')
    #plt.xticks(x = boxplot_data['Stage'], labels = ['Full Day', 'Best for MPC', '3', '4', '5'])
    plt.ylim([-60, 420])
    plt.ylabel('Unassigned Minutes')
    plt.suptitle('Difference in Unassigned Parking Minutes')
    plt.title(title_str)




if __name__ == '__main__':
    plt.rcParams['figure.dpi'] = 500
    file_path = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2023-12-17_Aaron Result_big_set/*.dat'
    files = load_data(file_path)
    res = parse_data(files)
    data, FullFailure_ls, MPCFailure_ls = del_incomplete_runs(res)
    completed_data, Full_status_error, Full_status_9, MPC_status_9 = del_failed_runs(data)
    
    # data = res
    run_params_OG = extract_run_params(data)
    run_params_complete = extract_run_params(completed_data)
    
    FCFS_unassigned, Full_unassigned, MPC_unassigned, diff_FCFS_Full, diff_FCFS_MPC, diff_MPC_Full = plot_unassigned(completed_data)
    
    
    
    ############ Graphic Generation Below   
    analysis_data = get_analysis_data(run_params_complete, FCFS_unassigned, Full_unassigned,
                                      MPC_unassigned, diff_FCFS_Full, diff_FCFS_MPC, diff_MPC_Full)
    
    
    #create boxplot with all data
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data)
    title_str = 'All Data'
    gen_boxplot(analysis_data, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    
    
    #create boxplot with high demand data only
    analysis_data_high_demand = get_high_demand(analysis_data)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_high_demand)
    title_str = 'High Demand Data Only'
    gen_boxplot(analysis_data_high_demand, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)

    #create boxplot with low demand data only
    analysis_data_low_demand = get_low_demand(analysis_data)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_low_demand)
    title_str = 'Low Demand Data Only'
    gen_boxplot(analysis_data_low_demand, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)


    #create boxplot with 1 parking space data only
    analysis_data_1_spot = get_X_parking_spaces(analysis_data, numSpots = 1)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_1_spot)
    title_str = '1 Parking Spot Data Only'
    gen_boxplot(analysis_data_1_spot, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)

    #create boxplot with 2 parking space data only
    analysis_data_2_spot = get_X_parking_spaces(analysis_data, numSpots = 2)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_2_spot)
    title_str = '2 Parking Spot Data Only'
    gen_boxplot(analysis_data_2_spot, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    
    #create boxplot with 5 parking space data only
    analysis_data_5_spot = get_X_parking_spaces(analysis_data, numSpots = 5)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_5_spot)
    title_str = '5 Parking Spot Data Only'
    gen_boxplot(analysis_data_5_spot, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)


    #create boxplot with 5 zeta data only
    analysis_data_5_zeta = get_zeta_data(analysis_data, zeta = 5)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_5_zeta)
    title_str = '5 minute zeta Data Only'
    gen_boxplot(analysis_data_5_zeta, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    
    #create boxplot with 10 zeta data only
    analysis_data_10_zeta = get_zeta_data(analysis_data, zeta = 10)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_10_zeta)
    title_str = '10 minute zeta Data Only'
    gen_boxplot(analysis_data_10_zeta, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    
    
    #create boxplot with 300 minute advance received time
    analysis_data_300_received = get_received_data(analysis_data, received_leadtime = 300)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_300_received)
    title_str = '300 minute received leadtime Data Only'
    gen_boxplot(analysis_data_300_received, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    
    #create boxplot with 30 minute advance received time
    analysis_data_30_received = get_received_data(analysis_data, received_leadtime = -1)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_30_received)
    title_str = '30 minute received leadtime Data Only'
    gen_boxplot(analysis_data_300_received, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)

    
    #create boxplot with 0 minute guarantee time
    analysis_data_0_rho = get_rho_data(analysis_data, rho = 0)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_0_rho)
    title_str = '0 minute parking guarantee Data Only'
    gen_boxplot(analysis_data_0_rho, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    
    #create boxplot with 60 minute guarantee time
    analysis_data_60_rho = get_rho_data(analysis_data, rho = 60)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_60_rho)
    title_str = '60 minute parking guarantee Data Only'
    gen_boxplot(analysis_data_60_rho, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    

    #create boxplot with 0 minute guarantee arrival time
    analysis_data_0_nu = get_nu_data(analysis_data, nu = 0)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_0_nu)
    title_str = '0 minute parking arrival time guarantee Data Only'
    gen_boxplot(analysis_data_0_nu, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    
    #create boxplot with 60 minute guarantee time
    analysis_data_60_nu = get_nu_data(analysis_data, nu = 60)
    analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5 = get_subset_stages(analysis_data_60_nu)
    title_str = '60 minute parking arrival time guarantee Data Only'
    gen_boxplot(analysis_data_60_nu, analysis_data_sub_2, analysis_data_sub_3, analysis_data_sub_4, analysis_data_sub_5, title_str)
    










