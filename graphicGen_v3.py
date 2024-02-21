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
    SWFailure_ls = []
    SW_idx = []
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
            SWFailure_ls.append(item)
            #SW_idx.append(index)
        if type(item['full-unassigned']) is not AttributeError and type(item['sliding']) is not AttributeError:
            item['res_idx'] = index
            data.append(item)
            #data_idx.append(index)
                
        index += 1
                
    return data, FullFailure_ls, SWFailure_ls

def del_failed_runs(data):
    Full_status_error = []
    Full_status_9 = []
    
    SW_status_error = []
    SW_status_9 = []
    
    completed_data = []
    
    idx = 0
    for item in data:
        if isinstance(item['FCFS'], pd.DataFrame):
            completed_data.append(item)
            
        if isinstance(item['full'], pd.DataFrame):       
            if 'StatusCode' in item['full'].columns:
                Full_status_error.append(item)
                if item['full']['StatusCode'][0] == 9:
                    Full_status_9.append(item)
            else:
                completed_data.append(item)
        
        if isinstance(item['sliding'], pd.DataFrame):
            if 'StatusCode' in item['sliding'].columns:
                SW_status_error.append(item)
                if item['sliding']['StatusCode'].isin([9]).any():
                    SW_status_9.append(item)
            else:
                completed_data.append(item)
 
        idx += 1
    
    return completed_data, Full_status_error, Full_status_9, SW_status_9

def extract_run_params(data):
    algo = []
    numSpots = []
    demand = []
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
        algo.append(run['spec']['algo'])
        numSpots.append(run['spec']['numSpots'])
        demand.append(run['spec']['numVehicles'] / run['spec']['numSpots'] / 11)
        buffer.append(run['spec']['buffer'])
        weightCruising.append(run['spec']['weightCruising'])
        weightDblPark.append(run['spec']['weightDoubleParking'])
        zeta.append(run['spec']['zeta'])
        if run['spec']['algo'] == 'FCFS':
            numVeh.append(len(run['FCFS']))
        elif run['spec']['algo'] == 'full':
            numVeh.append(len(run['full']))
        elif run['spec']['algo'] == 'SW':
            numVeh.append(len(run['sliding']))
        tau.append(run['spec']['tau'])
        rho.append(run['spec']['rho'])
        nu.append(run['spec']['nu'])
        received_delta.append(run['spec']['received_delta'])
        
    run_params = pd.DataFrame(list(zip(algo, numSpots, demand, numVeh, zeta, buffer, weightDblPark, weightCruising, tau, rho, nu, received_delta)),
                              columns = ['algo','numSpots', 'demand', 'numVeh', 'zeta', 'buffer', 'weightDblPark', 'weightCruising', 'tau', 'rho', 'nu', 'received_delta'])
    
    return run_params

def plot_unassigned(data):
    FCFS_data = []
    FCFS_data_idx = []
    FCFS_unassigned = []
    FCFS_numspaces = []
    FCFS_scenario = []
    FCFS_numVehicles = []
    full_data = []
    full_data_idx = []
    full_unassigned = []
    full_numspaces = []
    full_scenario = []
    full_numVehicles = []
    sliding_data = []
    sliding_data_idx = []
    sliding_unassigned = []
    sliding_numspaces = []
    sliding_scenario = []
    sliding_numVehicles = []
    
    for item in data:
        if isinstance(item['FCFS'], pd.DataFrame):
            FCFS_data.append(item)
            FCFS_data_idx.append(item['spec']['data_index'])
            FCFS_unassigned.append(item['FCFS-unassigned'])
            FCFS_numspaces.append(item['spec']['numSpots'])
            FCFS_scenario.append(item['spec']['scenario'])
            FCFS_numVehicles.append(item['spec']['numVehicles'])
        if isinstance(item['full'], pd.DataFrame):
            full_data.append(item)
            full_data_idx.append(item['spec']['data_index'])
            full_unassigned.append(item['full-unassigned'])
            full_numspaces.append(item['spec']['numSpots'])
            full_scenario.append(item['spec']['scenario'])
            full_numVehicles.append(item['spec']['numVehicles'])
        if isinstance(item['sliding'], pd.DataFrame):
            sliding_data.append(item)
            sliding_data_idx.append(item['spec']['data_index'])
            sliding_unassigned.append(item['sliding-unassigned'])
            sliding_numspaces.append(item['spec']['numSpots'])
            sliding_scenario.append(item['spec']['scenario'])
            sliding_numVehicles.append(item['spec']['numVehicles'])
            
    d = {'data_idx': FCFS_data_idx, 'FCFS_unassigned': FCFS_unassigned, 'numSpots': FCFS_numspaces, 'scenario': FCFS_scenario, 'numVehicles': FCFS_numVehicles}
    FCFS_df = pd.DataFrame(d)
    d = {'data_idx': full_data_idx, 'full_unassigned': full_unassigned, 'numSpots': full_numspaces, 'scenario': full_scenario, 'numVehicles': full_numVehicles}
    full_df = pd.DataFrame(d)
    d = {'data_idx': sliding_data_idx, 'sliding_unassigned': sliding_unassigned, 'numSpots': sliding_numspaces, 'scenario': sliding_scenario, 'numVehicles': sliding_numVehicles}
    sliding_df = pd.DataFrame(d)
    
    #full_df.drop(0, inplace = True) #not sure why doing this?

    plt.figure()
    plt.scatter(FCFS_data_idx, FCFS_unassigned, label = 'FCFS')
    plt.scatter(full_data_idx, full_unassigned, label = 'Full')
    plt.scatter(sliding_data_idx, sliding_unassigned, label = 'SW')
    plt.legend()
    # plt.xticks(range(min(x), max(x), 25))
    plt.xlabel('Vehicle Request Matrix')
    plt.ylabel('unassigned minutes of service')
    plt.show()
    
    FCFS_full_df = pd.merge_ordered(FCFS_df, full_df, on = ['data_idx', 'numSpots', 'numVehicles'], how = 'inner', suffixes=['_FCFS', '_full'])
    FCFS_full_df['diff'] = FCFS_full_df['FCFS_unassigned'] - FCFS_full_df['full_unassigned']
    #FCFS_SW_df = FCFS_df.merge(sliding_df, how = 'inner', on = 'data_idx')
    FCFS_SW_df = pd.merge_ordered(FCFS_df, sliding_df, on = ['data_idx', 'numSpots', 'numVehicles'], how = 'inner', suffixes=['_FCFS', '_sliding'])
    FCFS_SW_df['diff'] = FCFS_SW_df['FCFS_unassigned'] - FCFS_SW_df['sliding_unassigned']
    FCFS_SW_df['demand'] = FCFS_SW_df['numVehicles'] / FCFS_SW_df['numSpots'] / 11
    #SW_full_df = sliding_df.merge(full_df, how = 'inner')
    SW_full_df = pd.merge_ordered(sliding_df, full_df, on = ['data_idx', 'numSpots', 'numVehicles'], how = 'inner', suffixes=['_sliding', '_full'])
    SW_full_df['diff'] = SW_full_df['sliding_unassigned'] - SW_full_df['full_unassigned']
    
    
    # diff_FCFS_Full = np.subtract(FCFS_unassigned, Full_unassigned)
    # diff_FCFS_SW = np.subtract(FCFS_unassigned, SW_unassigned)
    # diff_SW_Full = np.subtract(SW_unassigned, Full_unassigned)
    
    plt.figure()
    plt.scatter(x = FCFS_full_df['data_idx'], y = FCFS_full_df['diff'], label = 'FCFS-Full')
    plt.scatter(x = FCFS_SW_df['data_idx'], y = FCFS_SW_df['diff'], label = 'FCFS-SW')
    plt.scatter(x = SW_full_df['data_idx'], y = SW_full_df['diff'], label = 'SW-Full')
    plt.legend()
    # plt.xticks(range(min(x), max(x), 25))
    plt.xlabel('Vehicle Request Matrix')
    plt.ylabel('redux unassigned minutes of service')
    plt.show()
    

    return FCFS_df, full_df, sliding_df, FCFS_data, full_data, sliding_data, FCFS_full_df, FCFS_SW_df, SW_full_df

def get_analysis_data(run_params_complete, FCFS_unassigned, Full_unassigned,
                                  SW_unassigned, diff_FCFS_Full, diff_FCFS_SW, diff_SW_Full):
    analysis_data = run_params_complete
    analysis_data['FCFS unassigned'] = FCFS_unassigned
    analysis_data['Full unassigned'] = Full_unassigned
    analysis_data['SW unassigned'] = SW_unassigned
    analysis_data['diff_FCFS_Full'] = diff_FCFS_Full
    analysis_data['diff_FCFS_SW'] = diff_FCFS_SW
    analysis_data['diff_SW_Full'] = diff_SW_Full
    
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
    Stage_2_data['Diff Unassigned'] = analysis_data_sub_2['diff_FCFS_SW']
    Stage_2_data['Stage'] = 'BFSW'

    Stage_3_data = pd.DataFrame(columns = ['Stage', 'Diff Unassigned'])
    Stage_3_data['Diff Unassigned'] = analysis_data_sub_3['diff_FCFS_SW']
    Stage_3_data['Stage'] = 'SLT'

    Stage_4_data = pd.DataFrame(columns = ['Stage', 'Diff Unassigned'])
    Stage_4_data['Diff Unassigned'] = analysis_data_sub_4['diff_FCFS_SW']
    Stage_4_data['Stage'] = 'GP'

    Stage_5_data = pd.DataFrame(columns = ['Stage', 'Diff Unassigned'])
    Stage_5_data['Diff Unassigned'] = analysis_data_sub_5['diff_FCFS_SW']
    Stage_5_data['Stage'] = 'GAT'

    boxplot_data = pd.concat([Stage_1_data, Stage_2_data, Stage_3_data, Stage_4_data, Stage_5_data])


    #boxplot for stage 1, full day versus FCFS
    plt.figure()
    sns.boxplot(data = boxplot_data, x = 'Stage', y = 'Diff Unassigned')
    #plt.xticks(x = boxplot_data['Stage'], labels = ['Full Day', 'Best for SW', '3', '4', '5'])
    plt.ylim([-60, 420])
    plt.ylabel('Unassigned Minutes')
    plt.suptitle('Difference in Unassigned Parking Minutes')
    plt.title(title_str)

def create_boxplots(analysis_data):
    
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
    



def extract_plot_data_spaces(completed_data):
    df = pd.DataFrame(columns = ['numSpots', 'unassigned minutes', 'scenario']) #item['FCFS-unassigned']-
    
    for item in completed_data:
        if isinstance(item['FCFS'], pd.DataFrame):
            df.loc[len(df)] = [item['spec']['numSpots'], item['FCFS-unassigned'], 'FCFS'] #scenario #0
        
        if isinstance(item['full'], pd.DataFrame):
            df.loc[len(df)] = [item['spec']['numSpots'], item['full-unassigned'], 'Full-Day'] #scenario #1
        
        if isinstance(item['sliding'], pd.DataFrame):
            if (item['spec']['scenario'] == 'scenario 2'): #scenario #2
                df.loc[len(df)] = [item['spec']['numSpots'], item['sliding-unassigned'], 'scenario 2']
            elif (item['spec']['scenario'] == 'scenario 3'): #scenario #3
                df.loc[len(df)] = [item['spec']['numSpots'], item['sliding-unassigned'], 'scenario 3']
            elif (item['spec']['scenario'] == 'scenario 4'): #scenario #4
                df.loc[len(df)] = [item['spec']['numSpots'], item['sliding-unassigned'], 'scenario 4']
            elif (item['spec']['scenario'] == 'scenario 5'): #scenario #5
                df.loc[len(df)] = [item['spec']['numSpots'], item['sliding-unassigned'], 'scenario 5']
            elif (item['spec']['scenario'] == 'scenario 6'): #scenario #6
                df.loc[len(df)] = [item['spec']['numSpots'], item['sliding-unassigned'], 'scenario 6']
            elif (item['spec']['scenario'] == 'scenario 7'): #scenario #7
                df.loc[len(df)] = [item['spec']['numSpots'], item['sliding-unassigned'], 'scenario 7']
                
    df.sort_values(['scenario'], inplace = True)
    
    df_log = df.copy(deep = True)
    df_log['unassigned minutes'] = np.log(df_log['unassigned minutes'])
    
    return df, df_log

def extract_plot_data_spaces_sensitivity(completed_data):
    df = pd.DataFrame(columns = ['numSpots', 'demand', 'unassigned minutes', 'scenario']) #item['FCFS-unassigned']-
    
    for item in completed_data:
        if isinstance(item['FCFS'], pd.DataFrame):
            df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['FCFS-unassigned'], 'FCFS'] #scenario #0
        
        if isinstance(item['full'], pd.DataFrame):
            df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['full-unassigned'], 'Full-Day'] #scenario #1
        
        if isinstance(item['sliding'], pd.DataFrame):
            if (item['spec']['scenario'] == 'scenario 1'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 1']
            elif (item['spec']['scenario'] == 'scenario 1a'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 1a']
            elif (item['spec']['scenario'] == 'scenario 2'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2']
            elif (item['spec']['scenario'] == 'scenario 2a'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2a']
            elif (item['spec']['scenario'] == 'scenario 2b'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2b']
            elif (item['spec']['scenario'] == 'scenario 2c'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2c']
            elif (item['spec']['scenario'] == 'scenario 3'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3']
            elif (item['spec']['scenario'] == 'scenario 3a'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3a']
            elif (item['spec']['scenario'] == 'scenario 3b'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3b']
            elif (item['spec']['scenario'] == 'scenario 3c'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3c']
            elif (item['spec']['scenario'] == 'scenario 4'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4']
            elif (item['spec']['scenario'] == 'scenario 4a'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4a']
            elif (item['spec']['scenario'] == 'scenario 4b'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4b']
            elif (item['spec']['scenario'] == 'scenario 4c'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4c']
            elif (item['spec']['scenario'] == 'scenario 5'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 5']
            elif (item['spec']['scenario'] == 'scenario 5a'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 5a']
            elif (item['spec']['scenario'] == 'scenario 6'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6']
            elif (item['spec']['scenario'] == 'scenario 6a'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6a']
            elif (item['spec']['scenario'] == 'scenario 6b'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6b']
            elif (item['spec']['scenario'] == 'scenario 6c'): 
                df.loc[len(df)] = [item['spec']['numSpots'], item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6c']
                
    df.sort_values(['scenario'], inplace = True)
    
    df_log = df.copy(deep = True)
    df_log['unassigned minutes'] = np.log(df_log['unassigned minutes'])
    
    return df, df_log

def extract_plot_data_demand(completed_data):
    df = pd.DataFrame(columns = ['demand', 'unassigned minutes', 'scenario']) #item['FCFS-unassigned']-
    
    for item in completed_data:
        if isinstance(item['FCFS'], pd.DataFrame):
            df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['FCFS-unassigned'], 'FCFS'] #scenario #0
        
        if isinstance(item['full'], pd.DataFrame):
            df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['full-unassigned'], 'Full-Day'] #scenario #1
        
        if isinstance(item['sliding'], pd.DataFrame):
            if (item['spec']['scenario'] == 'scenario 2'): #scenario #2
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2']
            elif (item['spec']['scenario'] == 'scenario 3'): #scenario #3
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3']
            elif (item['spec']['scenario'] == 'scenario 4'): #scenario #4
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4']
            elif (item['spec']['scenario'] == 'scenario 5'): #scenario #5
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 5']
            elif (item['spec']['scenario'] == 'scenario 6'): #scenario #6
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6']
            elif (item['spec']['scenario'] == 'scenario 7'): #scenario #7
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 7']
                
    df.sort_values(['scenario'], inplace = True)
    
    df_log = df.copy(deep = True)
    df_log['unassigned minutes'] = np.log(df_log['unassigned minutes'])
    
    return df, df_log

def extract_plot_data_demand_sensitivity(completed_data):
    df = pd.DataFrame(columns = ['demand', 'unassigned minutes', 'scenario']) #item['FCFS-unassigned']-
    
    for item in completed_data:
        if isinstance(item['FCFS'], pd.DataFrame):
            df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['FCFS-unassigned'], 'FCFS'] #scenario #0
        
        if isinstance(item['full'], pd.DataFrame):
            df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['full-unassigned'], 'Full-Day'] #scenario #1
        
        if isinstance(item['sliding'], pd.DataFrame):
            if (item['spec']['scenario'] == 'scenario 1'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 1']
            elif (item['spec']['scenario'] == 'scenario 1a'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 1a']
            elif (item['spec']['scenario'] == 'scenario 2'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2']
            elif (item['spec']['scenario'] == 'scenario 2a'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2a']
            elif (item['spec']['scenario'] == 'scenario 2b'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2b']
            elif (item['spec']['scenario'] == 'scenario 2c'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 2c']
            elif (item['spec']['scenario'] == 'scenario 3'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3']
            elif (item['spec']['scenario'] == 'scenario 3a'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3a']
            elif (item['spec']['scenario'] == 'scenario 3b'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3b']
            elif (item['spec']['scenario'] == 'scenario 3c'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 3c']
            elif (item['spec']['scenario'] == 'scenario 4'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4']
            elif (item['spec']['scenario'] == 'scenario 4a'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4a']
            elif (item['spec']['scenario'] == 'scenario 4b'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4b']
            elif (item['spec']['scenario'] == 'scenario 4c'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 4c']
            elif (item['spec']['scenario'] == 'scenario 5'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 5']
            elif (item['spec']['scenario'] == 'scenario 5a'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 5a']
            elif (item['spec']['scenario'] == 'scenario 6'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6']
            elif (item['spec']['scenario'] == 'scenario 6a'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6a']
            elif (item['spec']['scenario'] == 'scenario 6b'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6b']
            elif (item['spec']['scenario'] == 'scenario 6c'): 
                df.loc[len(df)] = [item['spec']['numVehicles']/item['spec']['numSpots']/11, item['sliding-unassigned'], 'scenario 6c']
                
    df.sort_values(['scenario'], inplace = True)
    
    df_log = df.copy(deep = True)
    df_log['unassigned minutes'] = np.log(df_log['unassigned minutes'])
    
    return df, df_log

def gen_plots_spaces(df, demand, log = False):
    sns.set_palette('Spectral', n_colors = 22)  #'Spectral for large scenario sets'
    # plt.show()
    df = df[df['demand'] == demand]
    if log == False:
        plt.figure()
        sns.lineplot(data = df, x = 'numSpots', y = 'unassigned minutes', hue = 'scenario', style = 'scenario') #, err_style = 'bars'
        plt.suptitle('Total Minutes of Double Parking Across Scenarios')
        plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.figure()
        sns.lineplot(data = df, x = 'numSpots', y = 'unassigned minutes', hue = 'scenario', style = 'scenario', err_style = 'bars') #, err_style = 'bars'
        plt.suptitle('Total Minutes of Double Parking Across Scenarios')
        plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.figure()
        sns.boxplot(data = df, x = 'numSpots', y = 'unassigned minutes', hue = 'scenario')
        plt.suptitle('Total Minutes of Double Parking Across Scenarios')
        plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.figure()
        sns.stripplot(data = df, x = 'numSpots', y = 'unassigned minutes', hue = 'scenario')
        plt.suptitle('Total Minutes of Double Parking Across Scenarios')
        plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    else:
        plt.figure()
        sns.lineplot(data = df, x = 'numSpots', y = 'unassigned minutes', hue = 'scenario', style = 'scenario') #, err_style = 'bars'
        plt.suptitle('Total Minutes of Double Parking Across Scenarios')
        plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
        plt.ylabel('log unassigned minutes')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.figure()
        sns.lineplot(data = df, x = 'numSpots', y = 'unassigned minutes', hue = 'scenario', err_style = 'bars', style = 'scenario') #, err_style = 'bars'
        plt.suptitle('Total Minutes of Double Parking Across Scenarios')
        plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
        plt.ylabel('log unassigned minutes')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.figure()
        sns.boxplot(data = df, x = 'numSpots', y = 'unassigned minutes', hue = 'scenario')
        plt.suptitle('Total Minutes of Double Parking Across Scenarios')
        plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
        plt.ylabel('log unassigned minutes')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.figure()
        sns.stripplot(data = df, x = 'numSpots', y = 'unassigned minutes', hue = 'scenario')
        plt.suptitle('Total Minutes of Double Parking Across Scenarios')
        plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
        plt.ylabel('log unassigned minutes')
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    return

def gen_plots_demand(df, log = False):
    if log == False:
        plt.figure()
        sns.lineplot(data = df, x = 'demand', y = 'unassigned minutes', hue = 'scenario') #, err_style = 'bars'
        plt.figure()
        sns.lineplot(data = df, x = 'demand', y = 'unassigned minutes', hue = 'scenario', err_style = 'bars') #, err_style = 'bars'
        plt.figure()
        sns.boxplot(data = df, x = 'demand', y = 'unassigned minutes', hue = 'scenario')
        plt.figure()
        sns.stripplot(data = df, x = 'demand', y = 'unassigned minutes', hue = 'scenario')
    else:
        plt.figure()
        sns.lineplot(data = df, x = 'demand', y = 'unassigned minutes', hue = 'scenario') #, err_style = 'bars'
        plt.ylabel('log unassigned minutes')
        plt.figure()
        sns.lineplot(data = df, x = 'demand', y = 'unassigned minutes', hue = 'scenario', err_style = 'bars') #, err_style = 'bars'
        plt.ylabel('log unassigned minutes')
        plt.figure()
        sns.boxplot(data = df, x = 'demand', y = 'unassigned minutes', hue = 'scenario')
        plt.ylabel('log unassigned minutes')
        plt.figure()
        sns.stripplot(data = df, x = 'demand', y = 'unassigned minutes', hue = 'scenario')
        plt.ylabel('log unassigned minutes')
    return

def plot_contour(df, scenario):
    
    df_stepX = df[df['scenario_sliding'] == 'scenario '+str(i)]
    
    
    #FCFS_SW_df_stepX = FCFS_SW_df[FCFS_SW_df['scenario_sliding'] == 'scenario 4']
    # #FCFS_SW_df_step6['numVehicles'] = random.random()#FCFS_SW_df_step6['sliding_numSpots']*11*2
    fig = plt.figure(figsize = (6,4)) #winner
    ax = plt.tricontour(df_stepX['numSpots'], df_stepX['demand'], df_stepX['diff'], cmap = 'rainbow')
    cb = fig.colorbar(ax)
    plt.yticks([1,2,3,4])
    plt.xlabel('Number of Parking Spaces')
    plt.ylabel('demand (vehicles per hour per parking space)')
    plt.suptitle('Redux in double parking minutes')
    plt.title('(FCFS to Sliding Step ' +str(i) + ')')

    # # plt.title('Reduction in Cruising, FCFS and SW\n(minutes)')
    # # plt.xlabel('Hourly Demand\n(Vehicles per Parking Space per Hour)')
    # # plt.xticks([1,2,3])
    # # plt.xlim([0.9, 3.1])
    # # plt.ylabel('Weight Double Parking')
    # # plt.ylim([-0.05, 1.05])
    # plt.legend()
    
    return

def plot_contour_norm(df, scenario):
    
    df_stepX = df[df['scenario_sliding'] == 'scenario '+str(i)]
    
    
    #FCFS_SW_df_stepX = FCFS_SW_df[FCFS_SW_df['scenario_sliding'] == 'scenario 4']
    # #FCFS_SW_df_step6['numVehicles'] = random.random()#FCFS_SW_df_step6['sliding_numSpots']*11*2
    fig = plt.figure(figsize = (6,4)) #winner
    ax = plt.tricontour(df_stepX['numSpots'], df_stepX['demand'], df_stepX['diff_norm_spaces'], cmap = 'rainbow')
    cb = fig.colorbar(ax)
    plt.yticks([1,2,3,4])
    plt.xlabel('Number of Parking Spaces')
    plt.ylabel('demand (vehicles per hour per parking space)')
    plt.suptitle('Redux in double parking minutes per space')
    plt.title('(FCFS to Sliding Step ' +str(i) + ')')
    
    fig = plt.figure(figsize = (6,4)) #winner
    ax = plt.tricontour(df_stepX['numSpots'], df_stepX['demand'], df_stepX['diff_norm_spaces_hr'], cmap = 'rainbow')
    cb = fig.colorbar(ax)
    plt.yticks([1,2,3,4])
    plt.xlabel('Number of Parking Spaces')
    plt.ylabel('demand (vehicles per hour per parking space)')
    plt.suptitle('Redux in double parking minutes per space per hour')
    plt.title('(FCFS to Sliding Step ' +str(i) + ')')

    # # plt.title('Reduction in Cruising, FCFS and SW\n(minutes)')
    # # plt.xlabel('Hourly Demand\n(Vehicles per Parking Space per Hour)')
    # # plt.xticks([1,2,3])
    # # plt.xlim([0.9, 3.1])
    # # plt.ylabel('Weight Double Parking')
    # # plt.ylim([-0.05, 1.05])
    # plt.legend()
    
    return

def add_norm_cols(df):
    df['numVehicles'] = df['numSpots']*df['demand']*11
    
    df['min_norm_spaces'] = df['unassigned minutes'] / df['numSpots']
    df['min_norm_spaces_hr'] = df['min_norm_spaces'] / 11
    df['min_norm_demand'] = df['unassigned minutes'] / df['demand']
    df['min_norm_demand_vehicle_hr'] = df['min_norm_demand'] / df['numVehicles'] / 11
    df['min_norm_vehicles'] = df['unassigned minutes'] / df['numVehicles']
    df['min_norm_vehicles_hr'] = df['min_norm_vehicles'] / 11
    
    return df


if __name__ == '__main__':

    plt.rcParams['figure.dpi'] = 500
    
    
    #now configured to combine files from multiple runs
    run_1 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-02-18_Aaron Result_PSC_(full_7200_SW_300_iter_5)/*.dat'
    run_2 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-02-20_Aaron Result_PSC_(full_7200_SW_300_iter_5_c_cases)/*.dat'
    runs = [run_1, run_2]
    
    #run_1 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-02-18_Aaron Result_PSC_(full_7200_SW_300_iter_5)/*.dat'
    #runs = [run_1]
    
    compiled_data = []
    compiled_completed_data = []
    compiled_Full_status_error = []
    compiled_Full_status_9 = []
    compiled_SW_status_9 = []
    for run in runs:
        file_path = run
        files = load_data(file_path)
        res = parse_data(files)
        data, FullFailure_ls, SWFailure_ls = del_incomplete_runs(res)
        completed_data, Full_status_error, Full_status_9, SW_status_9 = del_failed_runs(data)
        
        #add the current data to the data from the prior run
        compiled_data.extend(data)
        compiled_completed_data.extend(completed_data)
        compiled_Full_status_error.extend(Full_status_error)
        compiled_Full_status_9.extend(Full_status_9)
        compiled_SW_status_9.extend(SW_status_9)


    run_params_OG = extract_run_params(compiled_data)
    run_params_complete = extract_run_params(compiled_completed_data)

    # ############ debug checks through graphics
    FCFS_df, full_df, sliding_df, FCFS_data, full_data, sliding_data, FCFS_full_df, FCFS_SW_df, SW_full_df = plot_unassigned(compiled_completed_data)


    # ############ Graphic generation
    
    # #graphics exploring a range of parking spaces
    # #df, df_log = extract_plot_data_spaces(compiled_completed_data)
    df, df_log = extract_plot_data_spaces_sensitivity(compiled_completed_data)
    
    # df_subset = df[(df['scenario']=='FCFS') |
    #                          (df['scenario']=='Full-Day') |
    #                          (df['scenario']=='scenario 1') |
    #                          (df['scenario']=='scenario 2') |
    #                          (df['scenario']=='scenario 3') |
    #                          (df['scenario']=='scenario 4') |
    #                          (df['scenario']=='scenario 5') |
    #                          (df['scenario']=='scenario 6')
    #                          ]
    
    for i in range(1,5):
        gen_plots_spaces(df, demand = i)
    #     gen_plots_spaces(df_log, demand = i, log = True)
    
    
    
    # #graphics exploring a range in demand
    # df, df_log = extract_plot_data_demand(completed_data)
    
    # df, df_log = extract_plot_data_demand_sensitivity(completed_data)
    
    # gen_plots_demand(df)
    # gen_plots_demand(df_log, log = True)
    
    
    # #plt.ylabel('redux unassigned minutes')


    # ################## Contour plot stuff
    FCFS_SW_norm_df = FCFS_SW_df
    FCFS_SW_norm_df['diff_norm_spaces'] = FCFS_SW_norm_df['diff'] / FCFS_SW_norm_df['numSpots']
    FCFS_SW_norm_df['diff_norm_spaces_hr'] = FCFS_SW_norm_df['diff'] / FCFS_SW_norm_df['numSpots'] / 11
    for i in range(1,7):
        plot_contour(FCFS_SW_df, scenario = i)
        plot_contour_norm(FCFS_SW_norm_df, scenario=1)
        
        
    # ################## Normalized plotting
    
    #create the missing normalization columns
    df, df_log = extract_plot_data_spaces_sensitivity(compiled_completed_data)
    df_norm = add_norm_cols(df)
        
    #subset the data
    df_norm_subset = df_norm[(df_norm['scenario']=='FCFS') |
                             (df_norm['scenario']=='Full-Day') |
                             (df_norm['scenario']=='scenario 1') |
                             (df_norm['scenario']=='scenario 2') |
                             (df_norm['scenario']=='scenario 3') |
                             (df_norm['scenario']=='scenario 4') |
                             (df_norm['scenario']=='scenario 5') |
                             (df_norm['scenario']=='scenario 6')
                             ]
    
    sns.set_palette('tab10')
                    
    plt.figure()
    sns.lineplot(data = df_norm_subset, x = 'numSpots', y = 'min_norm_spaces', hue='scenario', style='demand') #, err_style = 'bars'
    plt.ylabel('unassigned minutes per space')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.figure()
    sns.lineplot(data = df_norm_subset, x = 'numSpots', y = 'min_norm_spaces_hr', hue='scenario') #, err_style = 'bars'
    plt.ylabel('unassigned minutes per space per hour')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.figure()
    sns.lineplot(data = df_norm_subset, x = 'numSpots', y = 'min_norm_spaces_hr', hue='scenario', style='demand') #, err_style = 'bars'
    plt.ylabel('unassigned minutes per space per hour')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.figure()
    sns.lineplot(data = df_norm_subset, x = 'numSpots', y = 'min_norm_demand', hue='scenario', style='demand') #, err_style = 'bars'
    plt.ylabel('unassigned minutes per demand')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.figure()
    sns.lineplot(data = df_norm_subset, x = 'numSpots', y = 'min_norm_vehicles', hue='scenario', style='demand') #, err_style = 'bars'
    plt.ylabel('unassigned minutes per vehicle')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.figure()
    sns.lineplot(data = df_norm_subset, x = 'numSpots', y = 'min_norm_vehicles_hr', hue='scenario') #, err_style = 'bars'
    plt.ylabel('unassigned minutes per vehicle per hour')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        
    plt.figure()
    sns.lineplot(data = df_norm_subset, x = 'numSpots', y = 'min_norm_vehicles_hr', hue='scenario', style='demand') #, err_style = 'bars'
    plt.ylabel('unassigned minutes per vehicle per hour')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    plt.figure()
    sns.lineplot(data = df_norm_subset, x = 'numSpots', y = 'min_norm_demand_vehicle_hr', hue='scenario', style='demand') #, err_style = 'bars'
    plt.ylabel('unassigned minutes per demand per vehicle per hour')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    
    #plot like mad









