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
import matplotlib.colors
import copy



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

def gen_plot_spaces_bar_norm(df, demand, log=False, mylabels=None):
    sns.set_palette('tab10')
    
    df = df[df['demand'] == demand]
    
    #df.drop(df[df['scenario'] == 'Baseline FCFS'].index, inplace=True) #added for the final results graphic, remove the FCFS data from the plot
    
    # plt.figure()
    # sns.barplot(data = df, x = 'numSpots', y = 'min_norm_hr_spaces', hue = 'scenario', errorbar='ci') #, err_style = 'bars'
    # plt.suptitle('Total Minutes of Double Parking Across Scenarios')
    # plt.title('Demand fixed at ' + str(demand) + ' vehicle per hr per space')
    # plt.ylabel('Unassigned minutes per hour per space')
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.figure()
    
    colors = df[['scenario', 'color']].drop_duplicates().set_index('scenario').to_dict()
    
    fig, ax = plt.subplots()
    #sns.barplot(data = df, x = 'numSpots', y = 'redux_min_norm_hr_spaces', hue = 'scenario', palette = colors['color'], errorbar='ci') #, err_style = 'bars' , color=color, , color=color['color']
    sns.barplot(data = df, x = 'numSpots', y = 'redux_min_norm_hr_spaces_demand', hue = 'scenario', palette = colors['color'], errorbar='ci') #, err_style = 'bars' , color=color, , color=color['color']
    #plt.suptitle('Change in Total Minutes of Parking Accommodation Across Scenarios')
    #plt.suptitle('Arrival Flexibility Increases Parking Accommodation')
    plt.suptitle('Reservation Buffers Decrease Parking Accommodation')
    plt.title('(Demand set at ' + str(demand) + ' vehicles per hour per space)')
    plt.ylabel('Change in Accommodation, FCFS to STW\n(minutes per hour per space by demand)')
    plt.xlabel('Number of Parking Spaces')
    
    y_low, y_upper = ax.get_ylim()
    plt.axhspan(y_low, 0, alpha = 0.1, zorder = 0, color='k', hatch='/')
    plt.ylim(y_low, y_upper)
    #ax.margins(y=0)
    
    # ax.text(2, 2.9, 'Reservation System Better', fontsize='large')
    # ax.text(-0.2, -.7, 'First-Come First-Serve Better', fontsize='large')
    
    ax.text(2, 1.6, 'Reservation System Better', fontsize='large')
    ax.text(-0.2, -2.6, 'First-Come First-Serve Better', fontsize='large')
    
    plt.axhline(y=0, color='k')
    
    handles, previous_labels = ax.get_legend_handles_labels() #https://stackoverflow.com/questions/23037548/change-main-plot-legend-label-text
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    if mylabels != None:
        plt.legend(title='Scenarios:', handles=handles, labels=mylabels, loc='center left', bbox_to_anchor=(1, 0.5)) #
        #plt.legend(title='Scenarios:', handles=handles, labels=mylabels, loc='center left', bbox_to_anchor=(0.05, -.36))
    plt.figure()

    return

def gen_plot_base_case(df, demand, spaces, mylabels=None):
    sns.set_palette('tab10')
    
    df = df[df['demand'] == demand]
    df = df[df['numSpots'] == spaces]
    
    colors = df[['scenario', 'color']].drop_duplicates().set_index('scenario').to_dict()
    
    fig, ax = plt.subplots()
    sns.barplot(data = df, ax=ax, x = 'scenario', y = 'redux_min_norm_hr_spaces_demand', hue = 'scenario', label='scenario', 
                palette = colors['color'], errorbar='ci', legend='auto', gap=0.1)
    
    plt.suptitle('Long Lead Time Helps, Buffers Reduce Effectiveness')
    plt.title('(results from representative case)')
    
    plt.ylabel('Change in Accommodation, FCFS to STW\n(minutes per hour per space by demand)')
    plt.xlabel('Scenario')
    plt.xticks(ticks=['scenario 1', 'scenario 2', 'scenario 3', 'scenario 4', 'scenario 5'], labels=['1', '2', '3', '4', '5'])
    y_low, y_upper = ax.get_ylim()
    plt.axhspan(y_low, 0, alpha = 0.1, zorder = 0, color='k', hatch='/')
    plt.ylim(y_low, y_upper)
    #ax.margins(y=0, tight=False)
    
    ax.text(1.75, .65, 'Reservation System Better', fontsize='large')
    ax.text(-0.2, -1, 'First-Come First-Serve Better', fontsize='large')
    
    plt.axhline(y=0, color='k')
    
    # handles, previous_labels = ax.get_legend_handles_labels()
    # print(handles)
    # mylabels = ['1) Long Lead Time',
    #             '2) Short Lead Time',
    #             '3) 15min Guarantee',
    #             '4) Immediate Guarantee',
    #             '5) 5min Reservation Buffers']
    
    # plt.legend(handles, mylabels)
    
    
    handles, previous_labels = ax.get_legend_handles_labels() #https://stackoverflow.com/questions/23037548/change-main-plot-legend-label-text
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    if mylabels != None:
        plt.legend(title='Scenarios:', handles=handles, labels=mylabels, loc='center left', bbox_to_anchor=(1., .5))
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

def gen_plot_demand_bar_norm(df, spaces, log=False, mylabels=None):
    sns.set_palette('tab10')
    
    df = df[df['numSpots'] == spaces]
    
    #df.drop(df[df['scenario'] == 'Baseline FCFS'].index, inplace=True) #added for the final results graphic, remove the FCFS data from the plot
    
    # plt.figure()
    # sns.barplot(data = df, x = 'demand', y = 'min_norm_hr_spaces_demand', hue = 'scenario', errorbar='ci') #, err_style = 'bars'
    # plt.suptitle('Total Minutes of Double Parking Across Scenarios')
    # plt.title('Parking spaces fixed at ' + str(spaces))
    # plt.ylabel('Unassigned minutes per hour per space per demand')
    # plt.xlabel('Average number of vehicles per hour per space (demand)')
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.figure()
    
    colors = df[['scenario', 'color']].drop_duplicates().set_index('scenario').to_dict()
    #mylabels = ['1', '2', '3', '4', '5']
    
    fig, ax = plt.subplots()
    sns.barplot(data = df, x = 'demand', y = 'redux_min_norm_hr_spaces_demand', hue = 'scenario', palette = colors['color'], errorbar='ci') #, err_style = 'bars'
    plt.suptitle('Change in Total Minutes of Parking Accommodation Across Scenarios')
    plt.title('(Parking spaces set at ' + str(spaces) + ')')
    plt.ylabel('Change in Accommodation, FCFS to STW\n(minutes per hour per space by demand)')
    plt.xlabel('Average number of vehicles per hour per space (demand)')
    
    y_low, y_upper = ax.get_ylim()
    plt.axhspan(y_low, 0, alpha = 0.1, zorder = 0, color='k', hatch='/') #, hatch='/'
    plt.ylim(y_low, y_upper)
    
    ax.text(1.3, 1.6, 'Reservation System Better', fontsize= 'large')
    ax.text(-0.23, -4.6, 'First-Come First-Serve Better', fontsize='large')
    plt.axhline(y=0, color='k')
    
    handles, previous_labels = ax.get_legend_handles_labels() #https://stackoverflow.com/questions/23037548/change-main-plot-legend-label-text
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    if mylabels != None:
        plt.legend(title = 'Scenarios:', handles=handles, labels=mylabels, loc='center left', bbox_to_anchor=(1, 0.5))
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
    run_9 = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2024-04-11_Aaron Result_SW(3600)_iter30_FCFS_extra_space/*.dat'
    runs = [run_1, run_2, run_3, run_4, run_5, run_6, run_7, run_8, run_9]


    
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
    #matching_scenarios = pd.Series(['Baseline FCFS','scenario 1', 'scenario 2', 'scenario 3', 'scenario 4', 'scenario 5'], name='scenario')
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2a', 'scenario 3a', 'scenario 4a', 'scenario 5a']) #not full reps
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 3a', 'scenario 4a', 'scenario 5a']) #does have full reps
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2b', 'scenario 3b', 'scenario 5b'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2c', 'scenario 3c', 'scenario 5c'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 5', 'scenario 5a', 'scenario 5b', 'scenario 5c', 'scenario 5e'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 2', 'scenario 2a', 'scenario 2b', 'scenario 2c'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 3', 'scenario 3a', 'scenario 3b', 'scenario 3c', 'scenario 3d'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 4', 'scenario 4a', 'scenario 3b', 'scenario 3c', 'scenario 4d']) #not full reps
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 4d'])
    #matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2', 'scenario 3', 'scenario 4', 'scenario 5'])
    matching_scenarios = pd.Series(['Baseline FCFS', 'scenario 1', 'scenario 2', 'scenario 2b', 'scenario 2c', 'scenario 3',
                                    'scenario 3a', 'scenario 3b', 'scenario 3c', 'scenario 4', 'scenario 4a',
                                    'scenario 5', 'scenario 5a', 'scenario 5b', 'scenario 5c', 'scenario 5e'])
    
    completed_data_idx = subset_data_idx(run_params_complete, matching_scenarios) #get the data indexes that have data from all required scenarios for comparison
    compiled_completed_data_by_idx = subset_by_data_idx(run_params_complete, completed_data_idx) #subset to dataset to just these data points
    
    completed_rep_idx = subset_rep_idx(run_params_complete, matching_scenarios)
    compiled_completed_data_by_rep = subset_by_rep(run_params_complete, completed_rep_idx)
    
    X = subset_idx_rep_and_data_idx(run_params_complete, matching_scenarios)
    
    num_data_idx = len(compiled_completed_data_by_idx.data_idx.unique().tolist())  #how many data indexes are applied across the cases of interest
    print('num_data_idx = ' + str(num_data_idx))
    
    
    #add FCFS reduction and normalization columns
    compiled_completed_data_by_idx = add_redux_cols(compiled_completed_data_by_idx)
    compiled_completed_data_by_idx = add_norm_cols(compiled_completed_data_by_idx)
    
    

    
    
    #add color codes to each of the scenarios                                                             
    # compiled_completed_data_by_idx_colors = compiled_completed_data_by_idx[(compiled_completed_data_by_idx['scenario'] != 'Baseline FD') & 
    #                                                                        (compiled_completed_data_by_idx['scenario'] != 'Baseline FCFS') &
    #                                                                        (compiled_completed_data_by_idx['scenario'] != 'Baseline FCFS extra space')]
    
    compiled_completed_data_by_idx_colors = compiled_completed_data_by_idx[(compiled_completed_data_by_idx['scenario'] != 'Baseline FD')]
    
    unique_scenarios = pd.Series(compiled_completed_data_by_idx_colors['scenario'].unique(), name='scenario').sort_values().reset_index(drop=True)
    unique_scenarios.drop([0,1], inplace=True) #remove 'Baseline FCFS' and 'Baseline FCFS extra space' from the unique scenarios list for color coding
    unique_scenarios.reset_index(drop=True, inplace=True)
    
    colors = []
    #[colors.append(matplotlib.colors.to_hex(plt.cm.tab20.colors[c])) for c in range(len(unique_scenarios))]
    [colors.append(plt.cm.tab20.colors[c]) for c in range(len(unique_scenarios))]
    colors = pd.Series(colors, name='color')
    scenarios_to_colors = pd.concat([unique_scenarios, colors], axis=1)
    
    compiled_completed_data_by_idx_colors = compiled_completed_data_by_idx_colors.merge(scenarios_to_colors, on='scenario', how='left')
                 
    
    
    #subset the compiled df to just include the matching scenarios of interest
    df = create_final_df(compiled_completed_data_by_idx_colors, matching_scenarios[matching_scenarios != 'Baseline FCFS'])
    df['demand'] = pd.to_numeric(df['demand'],downcast='integer')

    
    
    #plot
    
    mylabels=None
    #mylabels = matching_scenarios[matching_scenarios != 'Baseline FCFS']
    # mylabels = ['1) Long Lead Time',
    #             '2) Short Lead Time',
    #             '3) Guarantee Reservation',
    #             '4) Immediate Guarantee',
    #             '5) Reservation Buffers']
    # mylabels = ['1) Long Lead Time',
    #             '3a) Guarantee Reservation with flexible arrival times',
    #             '4a) Immediate Guarantee with flexible arrival times',
    #             '5a) Reservation Buffer with flexible arrival times']
    # mylabels = ['5) Reservation Buffer',
    #             '5a) Reservation Buffer with flexible arrival times',
    #             '5b) Reservation Buffer and shorter lead time',
    #             '5c) Reservation Buffer and shortest lead time and shortest time window',
    #             '5e) Reservation Buffer with longer buffer']
    # mylabels = ['1) Long Lead Time',
    #             '3a) 15min Guarantee, \u03A6=10',
    #             '4a) Immediate Guarantee, \u03A6=10',
    #             '5a) 5min Reservation Buffers, \u03A6=10']
    # mylabels = ['5) 5min Reservation Buffers', 
    #             '5a) 5min Reservation Buffers, \u03A6=10', 
    #             '5b) 5min Reservation Buffers, shorter lead time',
    #             '5c) 5min Reservation Buffers, shortest lead time', 
    #             '5e) 15min Reservation Buffers']
    mylabels = ['scenario 1',
                'scenario 2',
                'scenario 2b',
                'scenario 2c',
                'scenario 3',
                'scenario 3a',
                'scenario 3b',
                'scenario 3c',
                'scenario 4',
                'scenario 4a',
                'scenario 5',
                'scenario 5a',
                'scenario 5b',
                'scenario 5c',
                'scenario 5e']
    
    
    # gen_plot_base_case(df, 2, 5, mylabels=mylabels)
    
    # # for i in range(1,5):
    # #     gen_plot_spaces_bar(df, i)
    
    # for i in range(1,5):
    #     gen_plot_spaces_bar_norm(df, i, mylabels=mylabels)
        
    # # for i in [1,2,5,20,50]:
    # #     gen_plot_demand_bar(df, i)
    
    for i in [1,2,5,20,50]:
        gen_plot_demand_bar_norm(df, i, mylabels=mylabels)
    
    
    
    # #create a convert to smart curb add a parking space df
    # df_ratio = copy.deepcopy(compiled_completed_data_by_idx_colors)
    
    # df_extra_space = df_ratio[df_ratio['scenario'] == 'Baseline FCFS extra space'][['data_idx', 'unassigned_x']]
    # df_redux_extra_space = df_ratio.merge(df_extra_space, on='data_idx')
    # df_redux_extra_space.rename(columns={'unassigned_x_x': 'unassigned_OG', 'unassigned_y': 'unassigned_FCFS', 'redux unassigned': 'unassigned_redux_to_FCFS', 'unassigned_x_y': 'unassigned_FCFS_extra_space'}, inplace=True)
    # df_redux_extra_space['unassigned_redux_to_FCFS_extra_space'] = df_redux_extra_space['unassigned_OG'] - df_redux_extra_space['unassigned_FCFS_extra_space']
    # df_redux_extra_space['redux_extra_min_norm_hr_spaces'] = df_redux_extra_space['unassigned_redux_to_FCFS_extra_space'] / 11 / df_redux_extra_space['numSpots'] #create normalization columns
    # df_redux_extra_space['redux_extra_min_norm_hr_spaces_demand'] = df_redux_extra_space['unassigned_redux_to_FCFS_extra_space'] / 11 / df_redux_extra_space['numSpots'] / df_redux_extra_space['demand'] #create normalization columns
    
    # #collect the rows of data
    # df_parking_expansion = df_redux_extra_space[df_redux_extra_space['scenario'] == 'Baseline FCFS'][['data_idx', 'unassigned_redux_to_FCFS_extra_space']]
    # #comparison_cases = ['scenario 1']
    # df_switch_to_smart_curb = df_redux_extra_space[(df_redux_extra_space['scenario'] == 'scenario 1') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 2') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 2b') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 2c') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 3') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 3a') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 3b') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 3c') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 4') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 4a') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5a') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5b') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5c') |                                                   
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5e')] #(df_redux_extra_space['scenario'] == 'scenario 4') |
    
    # df_switch_to_smart_curb = df_redux_extra_space[(df_redux_extra_space['scenario'] == 'scenario 1') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 2') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 3') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 4') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5') ]
    
    # df_switch_to_smart_curb = df_redux_extra_space[(df_redux_extra_space['scenario'] == 'scenario 1') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 3a') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 4a') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5a') ]
    
    # df_switch_to_smart_curb = df_redux_extra_space[(df_redux_extra_space['scenario'] == 'scenario 5') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5a') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5b') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5c') |
    #                                                 (df_redux_extra_space['scenario'] == 'scenario 5e') ]
    
    
    # df_ratio_plot = df_switch_to_smart_curb.merge(df_parking_expansion, on='data_idx')
    # df_ratio_plot.rename(columns={'unassigned_redux_to_FCFS_extra_space_y': 'unassigned_redux_FCFS_to_FCFS_extra_space'}, inplace=True)
    # df_ratio_plot['redux ratio'] = df_ratio_plot['unassigned_redux_to_FCFS'] / df_ratio_plot['unassigned_redux_FCFS_to_FCFS_extra_space']
    # df_ratio_plot.sort_values('scenario', inplace=True)
    
    # colors = df[['scenario', 'color']].drop_duplicates().set_index('scenario').to_dict()
    
    # plt.figure()
    # sns.boxplot(x = 'demand', y = 'redux ratio', hue = 'scenario', data = df_ratio_plot, palette=colors['color'])
    # plt.axhline(y = 1, xmin = 0, xmax = 6, linewidth=2, color='r', linestyle = '--')
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    # plt.figure()
    # sns.boxplot(x = 'numSpots', y = 'redux ratio', hue = 'scenario', data = df_ratio_plot, palette=colors['color'])
    # plt.axhline(y = 1, xmin = 0, xmax = 6, linewidth=2, color='r', linestyle = '--')
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    
    # for i in range(1,5):
    #     data = df_ratio_plot[df_ratio_plot['demand'] == i]
        
    #     fig, ax = plt.subplots()
    #     sns.boxplot(x = 'numSpots', y = 'redux ratio', hue = 'scenario', data = data, palette=colors['color'])
    #     plt.suptitle('Double Parking Reduction Ratio\n(Demand set at ' + str(i) + ' vehicles per hour per space)')
    #     #plt.title('(Demand set at ' + str(i) + ' vehicles per hour per space)')
    #     plt.axhline(y = 1, xmin = 0, xmax = 6, linewidth=2, color='r', linestyle = '--')
    #     plt.ylabel('Double Parking Reduction Ratio\n(Redux Conversion / Redux Expansion)')
    #     plt.xlabel('Number of Parking Spaces')
    #     handles, previous_labels = ax.get_legend_handles_labels() #https://stackoverflow.com/questions/23037548/change-main-plot-legend-label-text
    #     #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #     plt.legend(title = 'Scenarios:', handles=handles, labels=mylabels, loc='center left', bbox_to_anchor=(1, 0.5))
    #     #plt.legend(loc='center left', bbox_to_anchor=(0, -1.25))
    #     #plt.legend(title = 'Scenarios:', handles=handles, labels=mylabels, loc='center left', bbox_to_anchor=(1, 0.5))
        
    # for i in [1,2,5,20,50]:
    #     data = df_ratio_plot[df_ratio_plot['numSpots'] == i]
        
    #     fig, ax = plt.subplots()
    #     sns.boxplot(x = 'demand', y = 'redux ratio', hue = 'scenario', data = data, palette=colors['color'])
    #     plt.suptitle('Double Parking Reduction Ratio\n(Parking Spaces set at ' + str(i) + ')')
    #     #plt.title('(Parking Spaces set at ' + str(i) + ')')
    #     plt.axhline(y = 1, xmin = 0, xmax = 6, linewidth=2, color='r', linestyle = '--')
    #     plt.ylabel('Double Parking Reduction Ratio\n(Redux Conversion / Redux Expansion)')
    #     plt.xlabel('Average number of vehicles per hour per space (demand)')
    #     handles, previous_labels = ax.get_legend_handles_labels() #https://stackoverflow.com/questions/23037548/change-main-plot-legend-label-text
    #     plt.legend(title = 'Scenarios:', handles=handles, labels=mylabels, loc='center left', bbox_to_anchor=(1, 0.5))
    #     #plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    #     #plt.legend(loc='center left', bbox_to_anchor=(0, -1.25))
    
    
    
    
    # colors = df[['scenario', 'color']].drop_duplicates().set_index('scenario').to_dict()
    # #mylabels = ['1', '2', '3', '4', '5']
    
    # fig, ax = plt.subplots()
    # sns.barplot(data = df, x = 'demand', y = 'redux_min_norm_hr_spaces_demand', hue = 'scenario', palette = colors['color'], errorbar='ci') #, err_style = 'bars'
    # plt.suptitle('Reduction in Total Minutes of Double Parking Across Base Scenarios')
    # plt.title('(Parking spaces set at ' + str(spaces) + ')')
    # plt.ylabel('Reduction in Total Double Parking\n(minutes per hour per space by demand)')
    # plt.xlabel('Average number of vehicles per hour per space (demand)')
    # handles, previous_labels = ax.get_legend_handles_labels() #https://stackoverflow.com/questions/23037548/change-main-plot-legend-label-text
    # plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # if mylabels != None:
    #     plt.legend(title = 'Scenarios:', handles=handles, labels=mylabels, loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.figure()
    
    
    
    
    
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






