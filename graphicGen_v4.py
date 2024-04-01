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
    
    return completed_data, Full_status_error, Full_status_9, SW_status_error, SW_status_9

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
    runtime = []
    phi = []
    scenario = []
    run_idx = []
    data_idx = []
    unassigned = []
    sched = []
    rep = []
    
    for run in data:
        algo.append(run['spec']['algo'])
        scenario.append(run['spec']['scenario'])
        numSpots.append(run['spec']['numSpots'])
        demand.append(run['spec']['numVehicles'] / run['spec']['numSpots'] / 11)
        buffer.append(run['spec']['buffer'])
        weightCruising.append(run['spec']['weightCruising'])
        weightDblPark.append(run['spec']['weightDoubleParking'])
        zeta.append(run['spec']['zeta'])
        if run['spec']['algo'] == 'FCFS':
            numVeh.append(len(run['FCFS']))
            runtime.append(run['FCFS-time'])
            unassigned.append(run['FCFS-unassigned'])
            sched.append(run['FCFS'])
        elif run['spec']['algo'] == 'full':
            numVeh.append(len(run['full']))
            runtime.append(run['full-time'])
            unassigned.append(run['full-unassigned'])
            sched.append(run['full'])
        elif run['spec']['algo'] == 'SW':
            numVeh.append(len(run['sliding']))
            runtime.append(run['sliding-time'])
            unassigned.append(run['sliding-unassigned'])
            sched.append(run['sliding'])
        tau.append(run['spec']['tau'])
        rho.append(run['spec']['rho'])
        nu.append(run['spec']['nu'])
        received_delta.append(run['spec']['received_delta'])
        phi.append(run['spec']['phi'])
        run_idx.append(run['spec']['run_index'])
        data_idx.append(run['spec']['data_index'])
        rep.append(run['spec']['rep'])
    
    run_params = pd.DataFrame(list(zip(algo, scenario, rep, run_idx, data_idx, runtime, numSpots, demand, numVeh, zeta, phi, buffer, weightDblPark, weightCruising, tau, rho, nu, received_delta, unassigned)),
                              columns = ['algo', 'scenario', 'rep', 'run_idx', 'data_idx', 'runtime','numSpots', 'demand', 'numVeh', 'zeta', 'phi', 'buffer', 'weightDblPark', 'weightCruising', 'tau', 'rho', 'nu', 'received_delta', 'unassigned'])

    run_params_sched = pd.DataFrame(list(zip(algo, scenario, rep, run_idx, data_idx, runtime, numSpots, demand, numVeh, zeta, phi, buffer, weightDblPark, weightCruising, tau, rho, nu, received_delta, unassigned, sched)),
                              columns = ['algo', 'scenario', 'rep', 'run_idx', 'data_idx', 'runtime','numSpots', 'demand', 'numVeh', 'zeta', 'phi', 'buffer', 'weightDblPark', 'weightCruising', 'tau', 'rho', 'nu', 'received_delta', 'unassigned', 'sched'])
    
    return run_params, run_params_sched

def subset_data_idx(data, matching_scenarios):
    
    data_idx_ls = data.data_idx.unique().tolist() #grab all of the unique data_idx explored in the latest run
    
    completed_data_idx = []
    
    for item in data_idx_ls:
        data_subset = data[data['data_idx'] == item]
        #print(data_subset['scenario'])
        # if data_subset['scenario'].reset_index(drop=True).equals(matching_scenarios) == True:
        #     completed_data_idx.append(item)
        if matching_scenarios.isin(data_subset['scenario']).all() == True:
            completed_data_idx.append(item)
    
    return completed_data_idx

def subset_rep_idx(data, matching_scenarios):
    
    rep_ls = data.rep.unique().tolist()
    
    completed_reps = []
    
    for rep in rep_ls:
        data_subset = data[data['rep'] == rep]
        
        if matching_scenarios.isin(data_subset['scenario']).all() == True:
            completed_reps.append(rep)
    
    return completed_reps

def subset_by_data_idx(data, data_idx):
    
    compiled_completed_data_by_idx = pd.DataFrame()
    
    for item in data_idx:
        subset = data[data['data_idx'] == item]
        #print(subset)
        compiled_completed_data_by_idx = pd.concat([compiled_completed_data_by_idx, subset])
    
    return compiled_completed_data_by_idx

def subset_by_rep(data, reps):
    
    compiled_completed_data_by_rep = pd.DataFrame()
    
    for rep in reps:
        subset = data[data['rep'] == rep]
        
        compiled_completed_data_by_rep = pd.concat([compiled_completed_data_by_rep, subset])
    
    return compiled_completed_data_by_rep

def subset_idx_rep_and_data_idx(data, matching_scenarios):
    
    rep_ls = data.rep.unique().tolist()
    #data_idx_ls = data.data_idx.unique().tolist()
    
    not_completed_reps = []
    
    for rep in rep_ls:
        subset = data[data['rep'] == rep] #subset the OG dataset to the current rep
        data_idx_ls = subset.data_idx.unique().tolist() #what are the data_idx for the subset
        
        for data_idx in data_idx_ls:
            data_subset = subset[subset['data_idx'] == data_idx]
            if matching_scenarios.isin(data_subset['scenario']).all() == False:
                not_completed_reps.append(rep)
                break  #continue, as in move to the next rep and don't record the current rep as being what we are looking for
        #not_completed_reps.append(rep) #made it through all of the data_idx for the current rep and no failures, store the rep for future use
    
    return not_completed_reps

def create_final_df(data, matching_scenarios):
    
    df = pd.DataFrame()
    
    for item in matching_scenarios:
        subset = data[data['scenario'] == item]
        df = pd.concat([df, subset])
        
    return df

def add_redux_cols(df):
    
    df_FCFS = df[df['scenario'] == 'Baseline FCFS'][['data_idx', 'unassigned']]
    df_redux = df.merge(df_FCFS, on='data_idx')
    df_redux['redux unassigned'] = df_redux['unassigned_y'] - df_redux['unassigned_x']
    
    return df_redux

def add_norm_cols(df):
    
    df['min_norm_hr_spaces'] = df['unassigned_x'] / 11 / df['numSpots']
    df['min_norm_hr_spaces_demand'] = df['unassigned_x'] / 11 / df['numSpots'] / df['demand']
    df['redux_min_norm_hr_spaces'] = df['redux unassigned'] / 11 / df['numSpots']
    df['redux_min_norm_hr_spaces_demand'] = df['redux unassigned'] / 11 / df['numSpots'] / df['demand']
    
    return df

def gen_plot_spaces_bar(df, demand, log=False):
    sns.set_palette('tab10')
    
    df = df[df['demand'] == demand]
    
    plt.figure()
    sns.barplot(data = df, x = 'numSpots', y = 'unassigned', hue = 'scenario', errorbar='ci') #, err_style = 'bars'
    plt.suptitle('Total Minutes of Double Parking Across Scenarios')
    plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.figure()
    
    return

def gen_plot_spaces_bar_norm(df, demand, log=False):
    sns.set_palette('tab10')
    
    df = df[df['demand'] == demand]
    
    # plt.figure()
    # sns.barplot(data = df, x = 'numSpots', y = 'min_norm_hr_spaces', hue = 'scenario', errorbar='ci') #, err_style = 'bars'
    # plt.suptitle('Total Minutes of Double Parking Across Scenarios')
    # plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
    # plt.ylabel('Unassigned minutes per hour per space')
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.figure()
    
    plt.figure()
    sns.barplot(data = df, x = 'numSpots', y = 'redux_min_norm_hr_spaces', hue = 'scenario', errorbar='ci') #, err_style = 'bars'
    plt.suptitle('Total Minutes of Double Parking Across Scenarios')
    plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
    plt.ylabel('Unassigned minutes per hour per space')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.figure()

    return

def gen_plot_demand_bar(df, spaces, log=False):
    sns.set_palette('tab10')
    
    df = df[df['numSpots'] == spaces]
    
    plt.figure()
    sns.barplot(data = df, x = 'demand', y = 'unassigned', hue = 'scenario', errorbar='ci') #, err_style = 'bars'
    plt.suptitle('Total Minutes of Double Parking Across Scenarios')
    plt.title('Parking spaces fixed at ' + str(spaces))
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.figure()
    
    return

def gen_plot_demand_bar_norm(df, spaces, log=False):
    sns.set_palette('tab10')
    
    df = df[df['numSpots'] == spaces]
    
    # plt.figure()
    # sns.barplot(data = df, x = 'demand', y = 'min_norm_hr_spaces_demand', hue = 'scenario', errorbar='ci') #, err_style = 'bars'
    # plt.suptitle('Total Minutes of Double Parking Across Scenarios')
    # plt.title('Parking spaces fixed at ' + str(spaces))
    # plt.ylabel('Unassigned minutes per hour per space per demand')
    # plt.xlabel('Average number of vehicles per hour per space (demand)')
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.figure()
    
    plt.figure()
    sns.barplot(data = df, x = 'demand', y = 'redux_min_norm_hr_spaces_demand', hue = 'scenario', errorbar='ci') #, err_style = 'bars'
    plt.suptitle('Total Minutes of Double Parking Across Scenarios')
    plt.title('Parking spaces fixed at ' + str(spaces))
    plt.ylabel('Unassigned minutes per hour per space per demand')
    plt.xlabel('Average number of vehicles per hour per space (demand)')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.figure()

    return



if __name__ == '__main__':

    plt.rcParams['figure.dpi'] = 500
    
    
    #now configured to combine files from multiple runs

    run_1 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-22_Aaron Result_SW(900)_iter30_FD/*.dat'
    run_2 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-23_Aaron Result_SW(900)_iter30_1_1a/*.dat'
    run_3 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-23_Aaron Result_SW(900)_iter30_2b3b/*.dat'
    #run_4 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-24_Aaron Result_SW(1800)_iter30_2a/*.dat'
    run_4 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-29_Aaron Result_SW(3600)_iter30_2a/*.dat'
    run_5 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-27_Aaron Result_SW(1800)_iter30_4_4a_4d/*.dat'
    #run_5 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-30_Aaron Result_SW(3600)_iter30_4d/*.dat'
    run_6 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-28_Aaron Result_SW(1800)_iter30_FCFS_5_5a_5b_5c_5e/*.dat'
    #run_7 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-28_Aaron Result_SW(1800)_iter30_FCFS_3_3a_3c_3d/*.dat'
    run_7 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-28_Aaron Result_SW(1800)_iter30_3_3a_3c_3d/*.dat'
    #run_7 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-29_Aaron Result_SW(3600)_iter30_3d/*.dat'
    run_8 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-03-28_Aaron Result_SW(1800)_iter30_2_2c/*.dat'
    runs = [run_1, run_2, run_3, run_4, run_5, run_6, run_7, run_8]


    
    compiled_res = []
    compiled_completed_data = []
    compiled_Full_status_error = []
    compiled_Full_status_9 = []
    compiled_SW_status_error = []
    compiled_SW_status_9 = []
    
    for run in runs:
        file_path = run #set tthe path
        files = load_data(file_path) #get the file path and names for each of the files
        res = parse_data(files) #pull in the raw data to a list containing a set of dictionaries
        completed_data, Full_status_error, Full_status_9, SW_status_error, SW_status_9 = del_failed_runs(res) #remove any runs that timed out
    
        #add the current data to the data from the prior run
        compiled_res.extend(res)
        compiled_completed_data.extend(completed_data)
        compiled_Full_status_error.extend(Full_status_error)
        compiled_Full_status_9.extend(Full_status_9)
        compiled_SW_status_error.extend(SW_status_error)
        compiled_SW_status_9.extend(SW_status_9)
    
    
    run_params_OG, run_params_OG_sched = extract_run_params(compiled_res)
    run_params_complete, run_params_complete_sched = extract_run_params(compiled_completed_data)
        
    
    #filter data based on data index, is there an entry present for each scenario given a data index?
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 3', 'scenario 4', 'scenario 5'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 2', 'scenario 3', 'scenario 4', 'scenario 5']) #what scenarios do you want to filter on?
    #matching_scenarios = pd.Series(['Baseline FCFS', 'Baseline FD'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2', 'scenario 3', 'scenario 4', 'scenario 5'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1a', 'scenario 2', 'scenario 3', 'scenario 4', 'scenario 5'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 2c', 'scenario 3c', 'scenario 5c']) #fastest and the most data?
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 3a', 'scenario 4a', 'scenario 5a']) #adding in the shift
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 5', 'scenario 5a', 'scenario 5b', 'scenario 5c', 'scenario 5e']) #can buffer beat FCFS?
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 2', 'scenario 3', 'scenario 4', 'scenario 5']) #can buffer beat FCFS?
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 2a'])
    # matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 1a',
    #                                 'scenario 2', 'scenario 2b', 'scenario 2c',
    #                                 'scenario 3', 'scenario 3b', 'scenario 3c',
    #                                 'scenario 4',
    #                                 'scenario 5', 'scenario 5a', 'scenario 5b', 'scenario 5c'])
    matching_scenarios = pd.Series(['Baseline FCFS','scenario 1', 'scenario 2', 'scenario 3', 'scenario 4', 'scenario 5'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2a', 'scenario 3a', 'scenario 4a', 'scenario 5a'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2b', 'scenario 3b', 'scenario 5b'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2c', 'scenario 3c', 'scenario 5c'])
    matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 5', 'scenario 5a', 'scenario 5b', 'scenario 5c', 'scenario 5e'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 2', 'scenario 2a', 'scenario 2b', 'scenario 2c'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 3', 'scenario 3a', 'scenario 3b', 'scenario 3c', 'scenario 3d'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 4', 'scenario 4a', 'scenario 3b', 'scenario 3c', 'scenario 4d'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 4d'])
    
    completed_data_idx = subset_data_idx(run_params_complete, matching_scenarios) #get the data indexes that have data from all required scenarios for comparison
    compiled_completed_data_by_idx = subset_by_data_idx(run_params_complete, completed_data_idx) #subset to dataset to just these data points
    
    completed_rep_idx = subset_rep_idx(run_params_complete, matching_scenarios)
    compiled_completed_data_by_rep = subset_by_rep(run_params_complete, completed_rep_idx)
    
    X = subset_idx_rep_and_data_idx(run_params_complete, matching_scenarios)
    
    num_data_idx = len(compiled_completed_data_by_idx.data_idx.unique().tolist())  #how many data indexes are applied across the cases of interest
    print('num_data_idx = ' + str(num_data_idx))
    
    #subset the compiled df to just include the matching scenarios of interest
    df = create_final_df(compiled_completed_data_by_idx, matching_scenarios)
    df = add_redux_cols(df)
    df = add_norm_cols(df)

    
    
    #plot
    # for i in range(1,5):
    #     gen_plot_spaces_bar(df, i)
    
    for i in range(1,5):
        gen_plot_spaces_bar_norm(df, i)
        
    # for i in [1,2,5,20,50]:
    #     gen_plot_demand_bar(df, i)
    
    for i in [1,2,5,20,50]:
        gen_plot_demand_bar_norm(df, i)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # compiled_data = []
    # compiled_completed_data = []
    # compiled_Full_status_error = []
    # compiled_Full_status_9 = []
    # compiled_SW_status_9 = []
    # for run in runs:
    #     file_path = run
    #     files = load_data(file_path)
    #     res = parse_data(files)
    #     data, FullFailure_ls, SWFailure_ls = del_incomplete_runs(res)
    #     completed_data, Full_status_error, Full_status_9, SW_status_9 = del_failed_runs(data)
        
    #     #add the current data to the data from the prior run
    #     compiled_data.extend(data)
    #     compiled_completed_data.extend(completed_data)
    #     compiled_Full_status_error.extend(Full_status_error)
    #     compiled_Full_status_9.extend(Full_status_9)
    #     compiled_SW_status_9.extend(SW_status_9)


    # run_params_OG = extract_run_params(compiled_data)
    # run_params_complete = extract_run_params(compiled_completed_data)

    # # # ############ debug checks through graphics
    # # FCFS_df, full_df, sliding_df, FCFS_data, full_data, sliding_data, FCFS_full_df, FCFS_SW_df, SW_full_df = plot_unassigned(compiled_completed_data)
    # plot_unassigned_ILP(compiled_completed_data)






