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
#file_path = 'C:/Users/Aaron/Documents/GitHub/sliding_time_window (Aaron)/2023-11-16/*.dat'
#file_path = 'C:/Users/Aaron/Documents/GitHub/sliding_time_window-main (3 Dec)/results (5 Dec)/2023-12-06/*.dat'
#file_path = 'C:/Users/Aaron/Documents/GitHub/sliding_time_window_data/res_data/2023-12-06/*.dat'
#file_path = 'C:/Users/Aaron/Documents/GitHub/sliding_time_window_data/res_data_during_debug/2023-12-06 (aaron reattempting runs)/*.dat'
file_path = 'C:/Users/Aaron/Documents/GitHub/sliding_time_window_data/Aaron Result_2023-12-14/*.dat'
files = load_data(file_path)
res = parse_data(files)
data, FullFailure_ls, MPCFailure_ls = del_incomplete_runs(res)
completed_data, Full_status_error, Full_status_9, MPC_status_9 = del_failed_runs(data)

# data = res
run_params = extract_run_params(data)

FCFS_unassigned, Full_unassigned, MPC_unassigned, diff_FCFS_Full, diff_FCFS_MPC, diff_MPC_Full = plot_unassigned(completed_data)














timeFCFS = []
timeFull = []
timeMPC = []
numSpaces = []
numVehicles = []
zeta = []
buffer = []
sumSI = []
propCars = []
schedFCFS = []
schedFull = []
schedMPC = []
weightDblPark = []
statusCode = []
statusCodeMPC = []

for run in data:
    timeFCFS.append(run['FCFS-time'].total_seconds())
    timeFull.append(run['full-time'].total_seconds())
    timeMPC.append(run['sliding-time'].total_seconds())
    numSpaces.append(run['spec']['numSpots'])
    numVehicles.append(len(run['FCFS']))
    zeta.append(run['spec']['zeta'])
    buffer.append(run['spec']['buffer'])
    sumSI.append(sum(run['FCFS']['s_i']))
    schedFCFS.append(run['FCFS'])
    schedFull.append(run['full'])
    schedMPC.append(run['sliding'])
    weightDblPark.append(run['spec']['weightDoubleParking'])
    if 'StatusCode' in run['full'].columns:
        statusCode.append(9)
    else:
        statusCode.append(2)    
        
    if 'StatusCode' in run['sliding'].columns:
        statusCodeMPC.append(9)
    else:
        statusCodeMPC.append(2)    
    
numTrucks = []
for ls in schedFCFS:    
    numTrucks.append(sum(ls['Type'] == 'Truck'))
    
    
    
#starting graphic gen with new non-co-located parking spaces
    
totalDblParkFCFS = []
totalCruiseFCFS = []
totalDblParkFull = []
totalCruiseFull = []
totalDblParkMPC = []
totalCruiseMPC = []
#numTrucks = []


for ls in schedFCFS:
    ls.replace('Double-Park', 'Double Park', inplace = True) #both entries were present initially, set all to the same string
    
    dblParkSchedFCFS = ls.loc[(ls['Assigned'] == 0) &
                              (ls['No-Park Outcome'] == 'Double Park' )]
    totalDblParkFCFS.append(sum(dblParkSchedFCFS['s_i']))
    
    cruiseSchedFCFS = ls.loc[(ls['Assigned'] == 0) &
                             (ls['No-Park Outcome'] == 'Cruising')]
    totalCruiseFCFS.append(sum(cruiseSchedFCFS['Actual Cruising Time']))
    
    #numTrucks.append(sum(ls['Type'] == 'Truck'))
    
    
objValueFull = []
objValueDblParkFull = []
objValueCruisingFull = []
for i in range(len(schedFull)):
#for i in range(0,1):
    #for ls in schedFull:
    ls = schedFull[i]
    if ls is not None:  #some weird data issue where 4 of the dataframe were not recorded
        ls.replace('Double-Park', 'Double Park', inplace = True) #both entries were present initially, set all to the same string
    
        dblParkSchedFull = ls.loc[(ls['Assigned'] == 0) &
                              (ls['No-Park Outcome'] == 'Double Park' )]
        totalDblParkFull.append(sum(dblParkSchedFull['s_i']))
    
        cruiseSchedFull = ls.loc[(ls['Assigned'] == 0) &
                             (ls['No-Park Outcome'] == 'Cruising')]
        totalCruiseFull.append(sum(cruiseSchedFull['Actual Cruising Time']))
        
        #calc the objective function
        obj = 0
        weightDblPark_i = res[i]['spec']['weightDoubleParking']
        weightCruising_i = 100 - weightDblPark_i
        objDblPark = (weightDblPark_i/100)*(ls['Expected Double Park']*ls['s_i']*(1-ls['Assigned']))
        objValueDblParkFull.append(sum(objDblPark))
        objCruising = (weightCruising_i/100)*(ls['Expected Cruising']*ls['Expected Cruising Time']*(1-ls['Assigned']))
        objValueCruisingFull.append(sum(objCruising))
        obj += sum(objDblPark) + sum(objCruising)
        objValueFull.append(obj) #the objective function is minimizing the expected double parking and cruising minutes


objValueMPC = []
objValueDblParkMPC = []
objValueCruisingMPC = []
for i in range(len(schedMPC)):
#for i in range(0,1):
#for ls in schedMPC:
    ls = schedMPC[i]

    ls.replace('Double-Park', 'Double Park', inplace = True) #both entries were present initially, set all to the same string
    
    dblParkSchedMPC = ls.loc[(ls['Assigned'] == 0) &
                              (ls['No-Park Outcome'] == 'Double Park' )]
    totalDblParkMPC.append(sum(dblParkSchedMPC['s_i']))
    
    cruiseSchedMPC = ls.loc[(ls['Assigned'] == 0) &
                             (ls['No-Park Outcome'] == 'Cruising')]
    totalCruiseMPC.append(sum(cruiseSchedMPC['Actual Cruising Time']))
    
    #calc the objective function
    obj = 0
    weightDblPark_i = res[i]['spec']['weightDoubleParking']
    weightCruising_i = 100 - weightDblPark_i
    objDblPark = (weightDblPark_i/100)*(ls['Expected Double Park']*ls['s_i']*(1-ls['Assigned']))
    objValueDblParkMPC.append(sum(objDblPark))
    objCruising = (weightCruising_i/100)*(ls['Expected Cruising']*ls['Expected Cruising Time']*(1-ls['Assigned']))
    objValueCruisingMPC.append(sum(objCruising))
    obj += sum(objDblPark) + sum(objCruising)
    objValueMPC.append(obj) #the objective function is minimizing the expected double parking and cruising minutes



#calc the reduction metrics
deltaObjValueFulltoMPC = np.subtract(np.array(objValueMPC), np.array(objValueFull))
reduxDblParkFCFStoMPC = np.subtract(np.array(totalDblParkFCFS), np.array(totalDblParkMPC))
reduxCruiseFCFStoMPC = np.subtract(np.array(totalCruiseFCFS), np.array(totalCruiseMPC))

# I don't have the schedule for the full day optimization in each case
reduxDblParkMPCtoFull = np.subtract(np.array(totalDblParkMPC), np.array(totalDblParkFull))
reduxCruiseMPCtoFull = np.subtract(np.array(totalCruiseMPC), np.array(totalCruiseFull))

reduxDblParkFCFStoFull = np.subtract(np.array(totalDblParkFCFS), np.array(totalDblParkFull))

#traditional redux in double parking and cruising
data_df = pd.DataFrame(list(zip(numVehicles, numTrucks, numSpaces, zeta, sumSI, statusCode, statusCodeMPC,
                                weightDblPark, reduxDblParkFCFStoMPC, reduxCruiseFCFStoMPC, 
                                reduxDblParkMPCtoFull, reduxCruiseMPCtoFull, reduxDblParkFCFStoFull)),
                          columns = ['Vehicles', 'Trucks', 'Parking Spaces', 'zeta', 'sumSI', 'Status Code', 'Status Code MPC',
                                     'Weight Dbl Parking', 'Redux Dbl Park FCFS to MPC', 'Redux Cruising FCFS to MPC',
                                    'Redux Dbl Park MPC to Full', 'Redux Cruising MPC to Full', 'Redux Dbl Park FCFS to Full'])

    
data_df['Norm Parking Spaces'] = data_df['sumSI'] / np.sum(list(data_df['Parking Spaces']), axis = 1) / 11
data_df['Prop Trucks'] = data_df['Trucks'] / data_df['Vehicles']
data_df['Daily Demand'] = data_df['Vehicles'] / np.sum(list(data_df['Parking Spaces']), axis = 1)
data_df['Hourly Demand'] = data_df['Daily Demand'] / 11
#data_df['Perc Sub Optimal'] = ((data_df['Obj Value MPC'] - data_df['Obj Value Full']) / data_df['Obj Value Full'])*100
data_df['Weight Dbl Parking'] = data_df['Weight Dbl Parking'] / 100

data_df_sub = data_df
data_df_sub = data_df[data_df['Status Code MPC'] == 2]
    

plt.figure()
sns.lineplot(x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Trucks', y = 'Redux Dbl Park FCFS to MPC', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Weight Dbl Parking', y = 'Redux Dbl Park FCFS to MPC', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Prop Trucks', y = 'Redux Dbl Park FCFS to MPC', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
  
   
   

plt.figure()
sns.lineplot(x = 'Vehicles', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Trucks', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Weight Dbl Parking', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Hourly Demand', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Prop Trucks', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.scatterplot(x = 'Vehicles', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.scatterplot(x = 'Trucks', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.scatterplot(x = 'Weight Dbl Parking', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.scatterplot(x = 'Hourly Demand', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.scatterplot(x = 'Prop Trucks', y = 'Redux Dbl Park MPC to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
  
   

plt.figure()
sns.lineplot(x = 'Vehicles', y = 'Redux Dbl Park FCFS to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Trucks', y = 'Redux Dbl Park FCFS to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Weight Dbl Parking', y = 'Redux Dbl Park FCFS to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
plt.figure()
sns.lineplot(x = 'Prop Trucks', y = 'Redux Dbl Park FCFS to Full', data = data_df_sub, hue = 'Parking Spaces', palette = 'tab10', ci = None)
  
   
   
    
    
    
     
    
    
    
    
    
    
    
    
    
    
    
    
    
#------------------------------------------------------------------------------    
#old graphic for the M21 paper

raw_data_df = pd.DataFrame(list(zip(numVehicles, numTrucks, numSpaces, sumSI, zeta, weightDblPark, timeFCFS, timeFull, timeMPC)),
                       columns = ['Vehicles', 'Trucks', 'Parking Spaces', 'sumSI', 'zeta', 'weightDblPark',
                                  'Runtime FCFS', 'Runtime Full', 'Runtime MPC'])

raw_data_df['weightCruising'] = 100-raw_data_df['weightDblPark']

raw_data_df['Daily Demand'] = raw_data_df['Vehicles'] / raw_data_df['Parking Spaces']
raw_data_df['Hourly Demand'] = raw_data_df['Daily Demand'] / 11

raw_data_df['Norm Parking Spaces'] = raw_data_df['sumSI'] / raw_data_df['Parking Spaces']
raw_data_df['Prop Trucks'] = raw_data_df['Trucks'] / raw_data_df['Vehicles']

raw_data_df = raw_data_df.reindex(columns = ['Vehicles', 'Trucks', 'Prop Trucks', 'Parking Spaces', 'Daily Demand', 'Hourly Demand',
                                             'sumSI', 'Norm Parking Spaces', 'zeta', 'weightDblPark', 'weightCruising',
                                             'Runtime FCFS', 'Runtime Full', 'Runtime MPC'])



sns.lineplot(x = 'Hourly Demand', y = 'Runtime MPC', hue = 'zeta',
             data = raw_data_df, palette = 'tab10')
plt.xlabel('# Vehicles / Parking Spaces / hour')
plt.ylabel('Runtime MPC (seconds)')

# plt.figure()
# sns.boxplot(x = 'Hourly Demand', y = 'Runtime MPC', hue = 'zeta', data = raw_data_df,
#             palette = 'tab10')
# sns.boxplot(x = 'Hourly Demand', y = 'Runtime Full', data = raw_data_df, palette = 'tab10')


#set up the dataframe for seaborn again
dataFull = pd.DataFrame(list(zip(numVehicles, numSpaces, sumSI, zeta, weightDblPark, statusCode, timeFull)),
                        columns = ['Vehicles', 'Parking Spaces', 'sumSI', 'zeta', 'weightDblPark',
                                   'Status Code', 'Runtime'])
dataFull['Daily Demand'] = dataFull['Vehicles'] / dataFull['Parking Spaces']
dataFull['Hourly Demand'] = dataFull['Daily Demand'] / 11
dataFull['Method'] = 'Full Day'

dataFull = dataFull[dataFull['Status Code'] == 2]

dataMPC = pd.DataFrame(list(zip(numVehicles, numSpaces, sumSI, zeta, weightDblPark, statusCode, timeMPC)),
                        columns = ['Vehicles', 'Parking Spaces', 'sumSI', 'zeta', 'weightDblPark',
                                   'Status Code', 'Runtime'])
dataMPC['Daily Demand'] = dataMPC['Vehicles'] / dataMPC['Parking Spaces']
dataMPC['Hourly Demand'] = dataMPC['Daily Demand'] / 11
dataMPC['Method'] = np.where(dataMPC['zeta'] == 2, 'MPC, zeta = 2 min', 'MPC, zeta = 5 min')

data_df = pd.concat([dataFull, dataMPC])

data_df.reset_index(inplace = True)

data_df['Norm Demand'] = data_df['sumSI'] / 11 / data_df['Parking Spaces']

data_df = data_df[data_df['Status Code'] == 2]

sns.boxplot(x = 'Hourly Demand', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10', whis = 1.5) #winner
#plt.xticks(ticks = [1,2,3], labels = [1,2,3])
plt.ylabel('Runtime\n(seconds)')
plt.xlabel('Hourly Demand\n(Average Vehicles per Parking Space per Hour)')
plt.title('Algorithm Runtime Full Day vs MPC\n(Optimization runtime limited at 10 minutes)')

sns.swarmplot(x = 'Hourly Demand', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10') #winner
#plt.xticks(ticks = [1,2,3], labels = [1,2,3])
plt.ylabel('Runtime\n(seconds)')
plt.xlabel('Hourly Demand\n(Average Vehicles per Parking Space per Hour)')
plt.title('Algorithm Runtime\n(Full Day vs MPC)')

sns.lineplot(x = 'Hourly Demand', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10', ci = None)
plt.xticks([1,2,3])
plt.ylabel('Runtime\n(seconds)')
plt.xlabel('Hourly Demand\n(Average Vehicles per Parking Space per Hour)')
plt.title('Algorithm Runtime\n(Full Day vs MPC)')

sns.lineplot(x = 'Vehicles', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')
sns.lineplot(x = 'Parking Spaces', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')

fig = plt.figure()
levels = [1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 60, 100, 200, 300, 400, 500, 600]
ax = plt.tricontour(data_df['Vehicles'], data_df['Parking Spaces'], data_df['Runtime'], cmap = 'rainbow', levels = levels)
cb = fig.colorbar(ax)
plt.title('Algorithm Runtime')
plt.xlabel('Number of Vehicles')
plt.ylabel('Number of Parking Spaces')
# plt.yticks([2, 5])
# plt.ylim([1.9, 5.1])
#plt.xlim([-1, 110])
plt.legend()


sns.scatterplot(x = 'Hourly Demand', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')
sns.violinplot(x = 'Hourly Demand', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10') #negative runtimes?
sns.scatterplot(x = 'Vehicles', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')
sns.stripplot(x = 'Vehicles', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')
sns.boxplot(x = 'Vehicles', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')
sns.scatterplot(x = 'Parking Spaces', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')
sns.stripplot(x = 'Parking Spaces', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')
sns.boxplot(x = 'Parking Spaces', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10')

sns.scatterplot(x = 'Norm Demand', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10',
                style = 'Method', s = 20) #winner
plt.ylabel('Runtime\n(seconds)')
plt.xlabel('Normalized Parking Demand\n(Average minutes of parking requested per parking space per hour)')
plt.title('Individual Algorithm Runtime Observations\n(Full Day vs MPC)')

sns.lineplot(x = 'Norm Demand', y = 'Runtime', hue = 'Method', data = data_df, palette = 'tab10',
                style = 'Method')




#set up the dataframe for seaborn
dataFCFS = pd.DataFrame(list(zip(numVehicles, numSpaces, sumSI, zeta, weightDblPark, timeFCFS)),
                        columns = ['Vehicles', 'Parking Spaces', 'sumSI', 'zeta', 'weightDblPark',
                                   'Runtime'])
dataFCFS['weightCruising'] = 1-dataFCFS['weightDblPark']
dataFCFS['Daily Demand'] = dataFCFS['Vehicles'] / dataFCFS['Parking Spaces']
dataFCFS['Hourly Demand'] = dataFCFS['Daily Demand'] / 11
dataFCFS['Norm Parking Spaces'] = raw_data_df['Norm Parking Spaces']
dataFCFS['Prop Trucks'] = raw_data_df['Prop Trucks']
dataFCFS['Method'] = 'FCFS'

dataFull = pd.DataFrame(list(zip(numVehicles, numSpaces, sumSI, zeta, weightDblPark, timeFull)),
                        columns = ['Vehicles', 'Parking Spaces', 'sumSI', 'zeta', 'weightDblPark',
                                   'Runtime'])
dataFull['weightCruising'] = 1-dataFull['weightDblPark']
dataFull['Daily Demand'] = dataFull['Vehicles'] / dataFull['Parking Spaces']
dataFull['Hourly Demand'] = dataFull['Daily Demand'] / 11
dataFull['Norm Parking Spaces'] = raw_data_df['Norm Parking Spaces']
dataFull['Prop Trucks'] = raw_data_df['Prop Trucks']
dataFull['Method'] = 'Full'

dataMPC = pd.DataFrame(list(zip(numVehicles, numSpaces, sumSI, zeta, weightDblPark, timeMPC)),
                        columns = ['Vehicles', 'Parking Spaces', 'sumSI', 'zeta', 'weightDblPark',
                                   'Runtime'])
dataMPC['weightCruising'] = 1-dataMPC['weightDblPark']
dataMPC['Daily Demand'] = dataMPC['Vehicles'] / dataMPC['Parking Spaces']
dataMPC['Hourly Demand'] = dataMPC['Daily Demand'] / 11
dataMPC['Norm Parking Spaces'] = raw_data_df['Norm Parking Spaces']
dataMPC['Prop Trucks'] = raw_data_df['Prop Trucks']
dataMPC['Method'] = 'MPC'

data_df = pd.concat([dataFCFS, dataFull, dataMPC])

data_df.reset_index(inplace = True)


sub_data_df = data_df[data_df['Method'] != 'FCFS']

#seaborn plot for runtime
plt.figure()
sns.lineplot(x = 'Hourly Demand', y = 'Runtime', hue = 'zeta', style = 'Method',
             data = sub_data_df, palette = 'tab10', ci = None)
plt.xlabel('Parking Space Demand (Num Vehicles / Num Parking Spaces)')
plt.ylabel('Runtime (seconds)')
plt.title('Optimization Runtime given Different Methods and zeta Values')
#plt.ylim([-1, 20])
#plt.xlim([-1, 25])

plt.figure()
sns.lineplot(x = 'Vehicles', y = 'Runtime', hue = 'zeta', style = 'Method',
             data = sub_data_df, palette = 'tab10', ci = None)
plt.xlabel('Number of Vehicles')
plt.ylabel('Runtime (seconds)')
plt.title('Optimization Runtime given Different Methods and zeta Values')
#plt.ylim([-1, 20]) 
#plt.xlim([-1, 100])


plt.figure()
sns.lineplot(x = 'Parking Spaces', y = 'Runtime', hue = 'zeta', style = 'Method',
             data = sub_data_df, palette = 'tab10', ci = None)
plt.xlabel('Number of Parking Spaces')
plt.ylabel('Runtime (seconds)')
plt.title('Optimization Runtime given Different Methods and zeta Values')
# plt.ylim([-1, 20])
# plt.xlim([-1, 25])


plt.figure()
sns.scatterplot(x = 'Hourly Demand', y = 'Runtime', hue = 'zeta', style = 'Method',
             data = sub_data_df, palette = 'tab10', ci = None)
plt.xlabel('Parking Space Demand (Num Vehicles / Num Parking Spaces)')
plt.ylabel('Runtime (seconds)')
plt.title('Optimization Runtime given Different Methods and zeta Values')
#plt.ylim([-1, 20])
#plt.xlim([-1, 25])

sub_sub_data_df = sub_data_df[sub_data_df['Method'] == 'Full']

plt.figure()
sns.stripplot(x = 'Hourly Demand', y = 'Runtime',
             data = sub_sub_data_df, palette = 'tab10')
plt.xlabel('Parking Space Demand (Num Vehicles / Num Parking Spaces / hour)')
plt.ylabel('Runtime (seconds)')
plt.title('Optimization Runtime given Different Methods and zeta Values')
#plt.ylim([-1, 20])
#plt.xlim([-1, 25])


#calc the reduction metrics

reduxRuntimeFulltoMPC = np.subtract(np.array(timeFull), np.array(timeMPC))

data_df = pd.DataFrame(list(zip(numVehicles, numTrucks, numSpaces, zeta, sumSI, timeFull, timeMPC, reduxRuntimeFulltoMPC)),
                         columns = ['Vehicles', 'Trucks', 'Parking Spaces', 'zeta', 'sumSI', 'Runtime Full', 'Runtime MPC', 'Redux Runtime'])

data_df['Norm Parking Spaces'] = data_df['sumSI'] / data_df['Parking Spaces'] / 11
data_df['Prop Trucks'] = (data_df['Trucks'] / data_df['Vehicles']).round(1)

data_df['Daily Demand'] = data_df['Vehicles'] / data_df['Parking Spaces']
data_df['Hourly Demand'] = data_df['Daily Demand'] / 11


data_df = data_df[data_df['Norm Parking Spaces'] <= 120]


sns.lineplot(data = data_df, x = 'Vehicles', hue = 'zeta', y = 'Redux Runtime',
             palette = 'tab10')
sns.lineplot(data = data_df, x = 'Parking Spaces', hue = 'zeta', y = 'Redux Runtime',
             palette = 'tab10')
sns.lineplot(data = data_df, x = 'Hourly Demand', hue = 'zeta', y = 'Redux Runtime',
             palette = 'tab10')
sns.scatterplot(data = data_df, x = 'Norm Parking Spaces', y = 'Redux Runtime', hue = 'zeta',
             palette = 'tab10')



data_df_avg = data_df.groupby(['Hourly Demand', 'Prop Trucks'])['Redux Runtime'].mean().reset_index()

fig = plt.figure()
ax = plt.tricontour(data_df_avg['Hourly Demand'], data_df_avg['Prop Trucks'], data_df_avg['Redux Runtime'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Runtime (sec) between MPC and Full')
plt.xlabel('# Vehicles / parking space / hour')
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
#plt.xlim([-1, 125])
plt.legend()


fig = plt.figure()
ax = plt.tricontour(data_df['Hourly Demand'], data_df['zeta'], data_df['Redux Runtime'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Runtime (sec) between MPC and Full')
plt.xlabel('# Vehicles / parking space / hour')
plt.ylabel('zeta')
plt.yticks([2, 5])
plt.ylim([1.9, 5.1])
#plt.xlim([-1, 125])
plt.legend()


fig = plt.figure()
ax = plt.tricontour(data_df['Vehicles'], data_df['zeta'], data_df['Redux Runtime'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Runtime (sec) between MPC and Full')
plt.xlabel('Number of Vehicles')
plt.ylabel('zeta')
plt.yticks([2, 5])
plt.ylim([1.9, 5.1])
#plt.xlim([-1, 110])
plt.legend()


fig = plt.figure()
ax = plt.tricontour(data_df['Parking Spaces'], data_df['zeta'], data_df['Redux Runtime'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Runtime (sec) between MPC and Full')
plt.xlabel('Number of Parking Spaces')
plt.ylabel('zeta')
plt.yticks([2, 5])
plt.ylim([1.9, 5.1])
#plt.xlim([8, 52])
plt.legend()


fig = plt.figure()
ax = plt.tricontour(data_df['Vehicles'], data_df['Parking Spaces'], data_df['Redux Runtime'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Runtime (sec) between MPC and Full')
plt.xlabel('Number of Vehicles')
plt.ylabel('Number of Parking Spaces')
#plt.ylim([8, 52])
#plt.xlim([-1, 110])
plt.legend()


data_df_avg = data_df.groupby(['Vehicles', 'Parking Spaces'])['Redux Runtime'].mean().reset_index()
fig = plt.figure()
ax = plt.tricontour(data_df_avg['Vehicles'], data_df_avg['Parking Spaces'], data_df_avg['Redux Runtime'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Runtime (sec) between MPC and Full')
plt.xlabel('Number of Vehicles')
plt.ylabel('Number of Parking Spaces')
plt.ylim([-2, 32])
#plt.xlim([-1, 110])
plt.legend()


sns.kdeplot(data = data_df, x = 'Vehicles', y = 'Parking Spaces', hue = 'Redux Runtime',
            palette = 'tab10')


#could consider total vehicles and number of parking spaces as influential variables as well
#the proportion of the vehicles shouldn't matter in this case, neither should the weight on the objective function



#------------------------------------------------------------------------------
# Reduction Graphics

totalDblParkFCFS = []
totalCruiseFCFS = []
totalDblParkFull = []
totalCruiseFull = []
totalDblParkMPC = []
totalCruiseMPC = []
#numTrucks = []


for ls in schedFCFS:
    ls.replace('Double-Park', 'Double Park', inplace = True) #both entries were present initially, set all to the same string
    
    dblParkSchedFCFS = ls.loc[(ls['Assigned'] == 0) &
                              (ls['No-Park Outcome'] == 'Double Park' )]
    totalDblParkFCFS.append(sum(dblParkSchedFCFS['s_i']))
    
    cruiseSchedFCFS = ls.loc[(ls['Assigned'] == 0) &
                             (ls['No-Park Outcome'] == 'Cruising')]
    totalCruiseFCFS.append(sum(cruiseSchedFCFS['Actual Cruising Time']))
    
    #numTrucks.append(sum(ls['Type'] == 'Truck'))
    
    
objValueFull = []
objValueDblParkFull = []
objValueCruisingFull = []
for i in range(len(schedFull)):
#for i in range(0,1):
    #for ls in schedFull:
    ls = schedFull[i]
    if ls is not None:  #some weird data issue where 4 of the dataframe were not recorded
        ls.replace('Double-Park', 'Double Park', inplace = True) #both entries were present initially, set all to the same string
    
        dblParkSchedFull = ls.loc[(ls['Assigned'] == 0) &
                              (ls['No-Park Outcome'] == 'Double Park' )]
        totalDblParkFull.append(sum(dblParkSchedFull['s_i']))
    
        cruiseSchedFull = ls.loc[(ls['Assigned'] == 0) &
                             (ls['No-Park Outcome'] == 'Cruising')]
        totalCruiseFull.append(sum(cruiseSchedFull['Actual Cruising Time']))
        
        #calc the objective function
        obj = 0
        weightDblPark = res[i]['spec']['weightDoubleParking']
        weightCruising = 100 - weightDblPark
        objDblPark = (weightDblPark/100)*(ls['Expected Double Park']*ls['s_i']*(1-ls['Assigned']))
        objValueDblParkFull.append(sum(objDblPark))
        objCruising = (weightCruising/100)*(ls['Expected Cruising']*ls['Expected Cruising Time']*(1-ls['Assigned']))
        objValueCruisingFull.append(sum(objCruising))
        obj += sum(objDblPark) + sum(objCruising)
        objValueFull.append(obj) #the objective function is minimizing the expected double parking and cruising minutes


objValueMPC = []
objValueDblParkMPC = []
objValueCruisingMPC = []
for i in range(len(schedMPC)):
#for i in range(0,1):
#for ls in schedMPC:
    ls = schedMPC[i]

    ls.replace('Double-Park', 'Double Park', inplace = True) #both entries were present initially, set all to the same string
    
    dblParkSchedMPC = ls.loc[(ls['Assigned'] == 0) &
                              (ls['No-Park Outcome'] == 'Double Park' )]
    totalDblParkMPC.append(sum(dblParkSchedMPC['s_i']))
    
    cruiseSchedMPC = ls.loc[(ls['Assigned'] == 0) &
                             (ls['No-Park Outcome'] == 'Cruising')]
    totalCruiseMPC.append(sum(cruiseSchedMPC['Actual Cruising Time']))
    
    #calc the objective function
    obj = 0
    weightDblPark = res[i]['spec']['weightDoubleParking']
    weightCruising = 100 - weightDblPark
    objDblPark = (weightDblPark/100)*(ls['Expected Double Park']*ls['s_i']*(1-ls['Assigned']))
    objValueDblParkMPC.append(sum(objDblPark))
    objCruising = (weightCruising/100)*(ls['Expected Cruising']*ls['Expected Cruising Time']*(1-ls['Assigned']))
    objValueCruisingMPC.append(sum(objCruising))
    obj += sum(objDblPark) + sum(objCruising)
    objValueMPC.append(obj) #the objective function is minimizing the expected double parking and cruising minutes



#calc the reduction metrics
deltaObjValueFulltoMPC = np.subtract(np.array(objValueMPC), np.array(objValueFull))
reduxDblParkFCFStoMPC = np.subtract(np.array(totalDblParkFCFS), np.array(totalDblParkMPC))
reduxCruiseFCFStoMPC = np.subtract(np.array(totalCruiseFCFS), np.array(totalCruiseMPC))

# I don't have the schedule for the full day optimization in each case
reduxDblParkMPCtoFull = np.subtract(np.array(totalDblParkMPC), np.array(totalDblParkFull))
reduxCruiseMPCtoFull = np.subtract(np.array(totalCruiseMPC), np.array(totalCruiseFull))


#traditional redux in double parking and cruising
data_df = pd.DataFrame(list(zip(numVehicles, numTrucks, numSpaces, zeta, sumSI, statusCode, statusCodeMPC,
                                weightDblPark, reduxDblParkFCFStoMPC, reduxCruiseFCFStoMPC, 
                                reduxDblParkMPCtoFull, reduxCruiseMPCtoFull)),
                          columns = ['Vehicles', 'Trucks', 'Parking Spaces', 'zeta', 'sumSI', 'Status Code', 'Status Code MPC',
                                     'Weight Dbl Parking', 'Redux Dbl Park FCFS to MPC', 'Redux Cruising FCFS to MPC',
                                    'Redux Dbl Park MPC to Full', 'Redux Cruising MPC to Full'])

#verification of the objective function
data_df = pd.DataFrame(list(zip(numVehicles, numTrucks, numSpaces, zeta, sumSI, statusCode, weightDblPark, objValueFull, objValueMPC, deltaObjValueFulltoMPC)),
                           columns = ['Vehicles', 'Trucks', 'Parking Spaces', 'zeta', 'sumSI', 'Status Code',
                                      'Weight Dbl Parking', 'Obj Value Full', 'Obj Value MPC', 'Delta Obj Value Full to MPC'])

#pareto front study
data_df = pd.DataFrame(list(zip(numVehicles, numTrucks, numSpaces, zeta, sumSI, statusCode, 
                                weightDblPark, objValueMPC, objValueDblParkMPC, objValueCruisingMPC,
                                totalDblParkFCFS, totalCruiseFCFS, totalDblParkMPC, totalCruiseMPC)),
                           columns = ['Vehicles', 'Trucks', 'Parking Spaces', 'zeta', 'sumSI', 'Status Code', 
                                      'Weight Dbl Parking', 'Obj Value MPC', 'Obj Value Dbl Park MPC', 'Obj Value Cruising MPC',
                                      'Total Dbl Park FCFS', 'Total Cruising FCFS', 'Total Dbl Park MPC', 'Total Cruising MPC'])


# data_df = pd.DataFrame(list(zip(numVehicles, numTrucks, numSpaces, zeta, weightDblPark, sumSI, reduxDblParkFCFStoMPC, reduxCruiseFCFStoMPC)),
#                          columns = ['Vehicles', 'Trucks', 'Parking Spaces', 'zeta', 'Dbl Park Weight', 'sumSI', 'Redux Dbl Park FCFS to MPC', 'Redux Cruising FCFS to MPC'])

data_df['Norm Parking Spaces'] = data_df['sumSI'] / data_df['Parking Spaces'] / 11
data_df['Prop Trucks'] = data_df['Trucks'] / data_df['Vehicles']
data_df['Daily Demand'] = data_df['Vehicles'] / data_df['Parking Spaces']
data_df['Hourly Demand'] = data_df['Daily Demand'] / 11
data_df['Perc Sub Optimal'] = ((data_df['Obj Value MPC'] - data_df['Obj Value Full']) / data_df['Obj Value Full'])*100
data_df['Weight Dbl Parking'] = data_df['Weight Dbl Parking'] / 100

data_df_sub = data_df
data_df_sub = data_df[data_df['Status Code MPC'] == 2]

data_df_sub_all_trucks = data_df_sub[data_df_sub['Prop Trucks'] > 0.9]
data_df_sub = data_df_sub_all_trucks



#redux dbl park and cruising split out by objective function weight detailed split out
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0]

data_df_sub_weight = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.25) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.5) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.75) |
                                 (data_df_sub['Weight Dbl Parking'] == 1)]

data_df_sub_weight = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0) | #this one is for cruising
                                 (data_df_sub['Weight Dbl Parking'] == 0.25) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.5) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.75)]


#num_spaces = 10
num_spaces = [1, 10, 20, 30, 40, 50]
for n in num_spaces:
    data_df_sub_weight_n = data_df_sub_weight[data_df_sub_weight['Parking Spaces'] == n]

    fig = plt.figure() #winner
    ax = plt.tricontour(data_df_sub_weight_n['Vehicles'], data_df_sub_weight_n['Prop Trucks'], data_df_sub_weight_n['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
    cb = fig.colorbar(ax)
    plt.suptitle('Reduction in Dbl Parking (min) between FCFS and MPC')
    plt.title('Parking Spaces = ' + str(n))
    plt.xlabel('Number of Vehicles')
    # plt.xlim([-0.05, 1.05])
    plt.ylabel('Proportion of Trucks')
    #plt.ylim([-.05, 1.05])
    plt.legend()
    
for n in num_spaces:
    data_df_sub_weight_n = data_df_sub_weight[data_df_sub_weight['Parking Spaces'] == n]
    fig = plt.figure(figsize = (6,4)) #winner
    ax = plt.tricontour(data_df_sub_weight_n['Hourly Demand'], data_df_sub_weight_n['Weight Dbl Parking'], data_df_sub_weight_n['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
    cb = fig.colorbar(ax)
    plt.title('Parking Spaces = ' + str(n))
    plt.suptitle('Reduction in Double Parking, FCFS to MPC (minutes)')
    plt.xlabel('Hourly Demand\n(Vehicles per Parking Space per Hour)')
    plt.xlim([0.9, 3.1])
    plt.xticks([1,2,3])
    plt.ylabel('Weight Double Parking')
    plt.ylim([-.05, 1.05])
    plt.legend()

for n in num_spaces:
    plt.figure()
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 1) & (data_df_sub['Parking Spaces'] == n)]
    sns.lineplot(data = data_df_sub_weight_n, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', linestyle = 'solid', ci = None, label = '1')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.75) & (data_df_sub['Parking Spaces'] == n)]
    sns.lineplot(data = data_df_sub_weight_n, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', linestyle = 'dashed', ci = None, label = '0.75')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.5) & (data_df_sub['Parking Spaces'] == n)]
    sns.lineplot(data = data_df_sub_weight_n, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', linestyle = 'dotted', ci = None, label = '0.5')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.25) & (data_df_sub['Parking Spaces'] == n)]
    sns.lineplot(data = data_df_sub_weight_n, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', linestyle = 'dashdot', ci = None, label = '0.25')
    plt.legend(title = 'Weight Dbl Parking')
    plt.suptitle('Average Reduction in Double Parking, FCFS to MPC')
    plt.title('Parking Spaces = ' + str(n))
    plt.xlabel('Number of Vehicles')
    plt.ylabel('Redux Double Parking\n(minutes)')

for n in num_spaces:
    plt.figure()
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.0) & (data_df_sub['Parking Spaces'] == n)]
    sns.lineplot(data = data_df_sub_weight_n, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', linestyle = 'solid', ci = None, label = '1')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.25) & (data_df_sub['Parking Spaces'] == n)]
    sns.lineplot(data = data_df_sub_weight_n, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', linestyle = 'dashed', ci = None, label = '0.75')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.5) & (data_df_sub['Parking Spaces'] == n)]
    sns.lineplot(data = data_df_sub_weight_n, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', linestyle = 'dotted', ci = None, label = '0.5')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.75) & (data_df_sub['Parking Spaces'] == n)]
    sns.lineplot(data = data_df_sub_weight_n, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', linestyle = 'dashdot', ci = None, label = '0.25')
    plt.legend(title = 'Weight Cruising')
    plt.suptitle('Average Reduction in Cruising, FCFS to MPC')
    plt.title('Parking Spaces = ' + str(n))
    plt.xlabel('Number of Vehicles')
    plt.ylabel('Redux Cruising\n(minutes)')


for n in num_spaces:
#for n in range(1,2):
    plt.figure()
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 1) & (data_df_sub['Parking Spaces'] == n)]
    sns.scatterplot(data = data_df_sub_weight_n, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', label = '1')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.75) & (data_df_sub['Parking Spaces'] == n)]
    sns.scatterplot(data = data_df_sub_weight_n, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', label = '0.75')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.5) & (data_df_sub['Parking Spaces'] == n)]
    sns.scatterplot(data = data_df_sub_weight_n, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', label = '0.5')
    data_df_sub_weight_n = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.25) & (data_df_sub['Parking Spaces'] == n)]
    sns.scatterplot(data = data_df_sub_weight_n, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', label = '0.25')
    plt.suptitle('Average Reduction in Double Parking, FCFS to MPC')
    plt.title('Parking Spaces = ' + str(n))
    plt.xlabel('Number of Norm Parking Spaces')
    plt.ylabel('Redux Double Parking\n(minutes)')
    plt.legend(title = 'Weight Dbl Parking')



#redux dbl park and cruising split out by objective function weight average approach
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0]
data_df_sub_weight = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.5) | 
                                 (data_df_sub['Weight Dbl Parking'] == 0.75)]
data_df_sub_weight = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.25) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.5) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.75)]
data_df_sub_weight = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0.25) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.5) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.75) |
                                 (data_df_sub['Weight Dbl Parking'] == 1)]

data_df_sub_weight = data_df_sub[(data_df_sub['Weight Dbl Parking'] == 0) | #this one is for cruising
                                 (data_df_sub['Weight Dbl Parking'] == 0.25) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.5) |
                                 (data_df_sub['Weight Dbl Parking'] == 0.75)]


plt.figure()
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 1]
sns.lineplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', linestyle = 'solid', ci = None, label = '1')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.75]
sns.lineplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', linestyle = 'dashed', ci = None, label = '0.75')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.5]
sns.lineplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', linestyle = 'dotted', ci = None, label = '0.5')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.25]
sns.lineplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', linestyle = 'dashdot', ci = None, label = '0.25')
plt.legend(title = 'Weight Dbl Parking')
plt.title('Average Reduction in Double Parking, FCFS to MPC')
plt.xlabel('Number of Vehicles')
plt.ylabel('Redux Double Parking\n(minutes)')

plt.figure()
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.25]
sns.boxplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.5]
sns.boxplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.75]
sns.boxplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 1]
sns.boxplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC')
plt.legend(title = 'Weight Dbl Parking')


plt.figure()
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.0]
sns.lineplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', linestyle = 'solid', ci = None, label = '1')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.25]
sns.lineplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', linestyle = 'dashed', ci = None, label = '0.75')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.5]
sns.lineplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', linestyle = 'dotted', ci = None, label = '0.5')
data_df_sub_weight = data_df_sub[data_df_sub['Weight Dbl Parking'] == 0.75]
sns.lineplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', linestyle = 'dashdot', ci = None, label = '0.25')
plt.legend(title = 'Weight Cruising')
plt.title('Average Reduction in Cruising, FCFS to MPC')
plt.xlabel('Number of Vehicles')
plt.ylabel('Redux Cruising\n(minutes)')



plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC')
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Parking Spaces', y = 'Redux Dbl Park FCFS to MPC')
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC')
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC')
plt.figure()
sns.boxplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC')


fig = plt.figure() #winner
ax = plt.tricontour(data_df_sub_weight['Vehicles'], data_df_sub_weight['Prop Trucks'], data_df_sub_weight['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.xlabel('Number of Vehicles')
# plt.xlim([-0.05, 1.05])
plt.ylabel('Proportion of Trucks')
#plt.ylim([-.05, 1.05])
plt.legend()

fig = plt.figure(figsize = (6,4)) #winner
ax = plt.tricontour(data_df_sub_weight['Hourly Demand'], data_df_sub_weight['Weight Dbl Parking'], data_df_sub_weight['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Double Parking, FCFS to MPC\n(minutes)')
plt.xlabel('Hourly Demand\n(Vehicles per Parking Space per Hour)')
plt.xlim([0.9, 3.1])
plt.xticks([1,2,3])
plt.ylabel('Weight Double Parking')
plt.ylim([-.05, 1.05])
plt.legend()

fig = plt.figure() #winner
ax = plt.tricontour(data_df_sub_weight['Vehicles'], data_df_sub_weight['Parking Spaces'], data_df_sub_weight['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.ylabel('Hourly Demand/n(Vehicles per Parking Space per Hour')
#plt.xlim([-0.05, 1.05])
plt.yticks([1,2,3])
plt.xlabel('Vehicles')
#plt.ylim([-.05, 1.05])
plt.legend()




plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC') #winner
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Parking Spaces', y = 'Redux Cruising FCFS to MPC') #winner
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Norm Parking Spaces', y = 'Redux Cruising FCFS to MPC') #winner
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Cruising FCFS to MPC')
plt.figure()
sns.boxplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Cruising FCFS to MPC')

fig = plt.figure()
ax = plt.tricontour(data_df_sub_weight['Vehicles'], data_df_sub_weight['Prop Trucks'], data_df_sub_weight['Redux Cruising FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Cruising (min) between FCFS and MPC')
plt.xlabel('Number of Vehicles')
# plt.xlim([-0.05, 1.05])
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
plt.legend()



#add a hue
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Dbl Park FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10')
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10')
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10')
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10')
plt.figure()
sns.boxplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10')

fig = plt.figure()
ax = plt.tricontour(data_df_sub_weight['Vehicles'], data_df_sub_weight['Prop Trucks'], data_df_sub_weight['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.xlabel('Number of Vehicles')
# plt.xlim([-0.05, 1.05])
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
plt.legend()

plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Vehicles', y = 'Redux Cruising FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10') #winner
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Parking Spaces', y = 'Redux Cruising FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10') #winner
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Norm Parking Spaces', y = 'Redux Cruising FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10') #winner
plt.figure()
sns.scatterplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Cruising FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10')
plt.figure()
sns.boxplot(data = data_df_sub_weight, x = 'Hourly Demand', y = 'Redux Cruising FCFS to MPC', hue = 'Weight Dbl Parking', palette = 'tab10')


fig = plt.figure() #winner
ax = plt.tricontour(data_df_sub_weight['Parking Spaces'], data_df_sub_weight['Prop Trucks'], data_df_sub_weight['Redux Cruising FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Cruising (min) between FCFS and MPC')
plt.xlabel('Number of Vehicles')
# plt.xlim([-0.05, 1.05])
plt.ylabel('Proportion of Trucks')
#plt.ylim([-.05, 1.05])
plt.legend()

fig = plt.figure(figsize = (6,4)) #winner
ax = plt.tricontour(data_df_sub_weight['Hourly Demand'], data_df_sub_weight['Weight Dbl Parking'], data_df_sub_weight['Redux Cruising FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Cruising, FCFS and MPC\n(minutes)')
plt.xlabel('Hourly Demand\n(Vehicles per Parking Space per Hour)')
plt.xticks([1,2,3])
plt.xlim([0.9, 3.1])
plt.ylabel('Weight Double Parking')
plt.ylim([-0.05, 1.05])
plt.legend()

fig = plt.figure() #winner
ax = plt.tricontour(data_df_sub_weight['Parking Spaces'], data_df_sub_weight['Hourly Demand'], data_df_sub_weight['Redux Cruising FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Cruising (min) between FCFS and MPC')
plt.ylabel('Hourly Demand\n(Number of Vehicle per Parking Space per Hour')
#plt.xticks([1,2,3])
# # plt.xlim([-0.05, 1.05])
plt.xlabel('Vehicles')
# plt.ylim([-.05, 1.05])
plt.legend()







# pareto plot
sns.scatterplot(data = data_df_sub, x = 'Obj Value Cruising MPC', y = 'Obj Value Dbl Park MPC', hue = 'Weight Dbl Parking', palette = 'tab10')
sns.scatterplot(data = data_df_sub, x = 'Total Cruising FCFS', y = 'Total Dbl Park FCFS', palette = 'tab10')

sns.scatterplot(data = data_df_sub, x = 'Total Cruising MPC', y = 'Total Dbl Park MPC', hue = 'Weight Dbl Parking', palette = 'tab10')


# expected objective function value verification
sns.lineplot(data = data_df_sub, x = 'Hourly Demand', y = 'Delta Obj Value Full to MPC')
sns.stripplot(data = data_df, x = 'Vehicles', y = 'Delta Obj Value Full to MPC', hue = 'Status Code', palette = 'tab10')

sns.scatterplot(data = data_df_sub, x = 'Vehicles', y = 'Delta Obj Value Full to MPC') #winner
plt.xlabel('Number of Vehicles')
plt.ylabel('Delta Optimization Function\n(Full day to MPC)')
plt.title('Comparison of Objective Function Value\n(Fall Day vs MPC, status = 2, "quick" dataset)')

sns.lineplot(data = data_df_sub, x = 'Vehicles', y = 'Delta Obj Value Full to MPC') #winner
plt.xlabel('Number of Vehicles')
plt.ylabel('Average Delta Optimization Function\n(Full day to MPC)')
plt.title('Comparison of Objective Function Value\n(Fall Day vs MPC, 95% CI)')

sns.boxplot(data = data_df_sub, x = 'Hourly Demand', y = 'Delta Obj Value Full to MPC', palette = 'tab10')
sns.stripplot(data = data_df_sub, x = 'Hourly Demand', y = 'Delta Obj Value Full to MPC', palette = 'tab10') #winner
sns.scatterplot(data = data_df_sub, x = 'Hourly Demand', y = 'Delta Obj Value Full to MPC', palette = 'tab10')






#redux in double parking based on status == 2
fig = plt.figure()
ax = plt.tricontour(data_df_sub['Weight Dbl Parking'], data_df_sub['Prop Trucks'], data_df_sub['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.xlabel('Dbl Park Weight')
plt.xlim([-0.05, 1.05])
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
plt.legend()

fig = plt.figure()
ax = plt.tricontour(data_df_sub['Vehicles'], data_df_sub['Parking Spaces'], data_df_sub['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
# plt.xlabel('Dbl Park Weight')
# plt.xlim([-0.05, 1.05])
# plt.ylabel('Proportion of Trucks')
# plt.ylim([-.05, 1.05])
plt.legend()

fig = plt.figure() #winner
ax = plt.tricontour(data_df_sub['Trucks'], data_df_sub['Parking Spaces'], data_df_sub['Redux Dbl Park FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.xlabel('Number of Vehicles')
plt.xlim([-5, 1700])
plt.ylabel('Number of Parking Spaces')
plt.ylim([-1, 51])
plt.legend()

fig = plt.figure() #winner
ax = plt.tricontour(data_df_sub['Norm Parking Spaces'], data_df_sub['Vehicles'], data_df_sub['Redux Dbl Park FCFS to MPC'], cmap = 'viridis')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
# plt.xlabel('Number of Vehicles')
# plt.xlim([-5, 1700])
# plt.ylabel('Number of Parking Spaces')
# plt.ylim([-1, 51])
plt.legend()

fig = plt.figure() #winner
ax = plt.tricontour(data_df_sub['Trucks'], data_df_sub['Parking Spaces'], data_df_sub['Redux Cruising FCFS to MPC'], cmap = 'rainbow')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.xlabel('Number of Vehicles')
plt.xlim([-5, 1700])
plt.ylabel('Number of Parking Spaces')
plt.ylim([-1, 51])
plt.legend()

fig = plt.figure() #winner
ax = plt.tricontour(data_df_sub['Norm Parking Spaces'], data_df_sub['Vehicles'], data_df_sub['Redux Cruising FCFS to MPC'], cmap = 'viridis')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
# plt.xlabel('Number of Vehicles')
# plt.xlim([-5, 1700])
# plt.ylabel('Number of Parking Spaces')
# plt.ylim([-1, 51])
plt.legend()


sns.boxplot(data = data_df_sub, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC', palette = 'tab10')
sns.scatterplot(data = data_df_sub, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC', palette = 'tab10')
sns.scatterplot(data = data_df_sub, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', palette = 'tab10')
sns.scatterplot(data = data_df_sub, x = 'Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', palette = 'tab10')








# Redux versus sumSI/#parking spaces, split out by proportion trucks
sns.lineplot(data = data_df, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', hue = 'Prop Trucks', palette = 'tab10')
plt.title('Reduction in Double Parking (min) between FCFS and MPC')
plt.xlabel('Service Duration Requested per Parking Space')
#plt.xlim([-1, 125])

sns.lineplot(data = data_df, x = 'Norm Parking Spaces', y = 'Redux Dbl Park FCFS to MPC', palette = 'tab10')
plt.title('Reduction in Double Parking (min) between FCFS and MPC')
plt.xlabel('Service Duration Requested per Parking Space')

sns.lineplot(data = data_df, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC', palette = 'tab10')
plt.title('Reduction in Double Parking (min) between FCFS and MPC')
plt.xlabel('# Vehicles / # Parking Spaces')

sns.scatterplot(data = data_df, x = 'Hourly Demand', y = 'Redux Dbl Park FCFS to MPC', palette = 'tab10')


sub_data_df = data_df[data_df['Norm Parking Spaces'] <= 600]
fig = plt.figure()
#levels = [-300, -100, 0, 100, 300]
ax = plt.tricontour(sub_data_df['Norm Parking Spaces'], sub_data_df['Prop Trucks'], sub_data_df['Redux Dbl Park FCFS to MPC'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Double Parking (min) between FCFS and MPC')
plt.xlabel('Service Duration Requested per Parking Space')
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
#plt.xlim([-1, 125])
plt.legend()


fig = plt.figure()
ax = plt.tricontour(sub_data_df['Norm Parking Spaces'], sub_data_df['Prop Trucks'], sub_data_df['Redux Cruising FCFS to MPC'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Cruising (min) between FCFS and MPC')
plt.xlabel('Service Duration Requested per Parking Space')
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
#plt.xlim([-1, 125])
plt.legend()


fig = plt.figure()
ax = plt.tricontour(data_df['Vehicles'], data_df['Prop Trucks'], data_df['Redux Dbl Park FCFS to MPC'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.xlabel('Number of Vehicles')
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
plt.legend()

fig = plt.figure()
ax = plt.tricontour(data_df['Vehicles'], data_df['Prop Trucks'], data_df['Redux Cruising FCFS to MPC'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Cruising (min) between FCFS and MPC')
plt.xlabel('Number of Vehicles')
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
plt.legend()

fig = plt.figure()
ax = plt.tricontour(data_df['zeta'], data_df['Prop Trucks'], data_df['Redux Dbl Park FCFS to MPC'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.xlabel('zeta')
plt.xticks([2, 5])
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
plt.legend()

fig = plt.figure()
ax = plt.tricontour(data_df['Dbl Park Weight'], data_df['Prop Trucks'], data_df['Redux Dbl Park FCFS to MPC'], cmap = 'tab10')
cb = fig.colorbar(ax)
plt.title('Reduction in Dbl Parking (min) between FCFS and MPC')
plt.xlabel('Dbl Park Weight')
plt.xlim([-0.05, 1.05])
plt.ylabel('Proportion of Trucks')
plt.ylim([-.05, 1.05])
plt.legend()






