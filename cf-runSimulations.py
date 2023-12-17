from multiprocessing import Pool
import multiprocessing as mp
from cfImplementation import runFullSetOfResults, simulateData, load_nhts_data
import numpy as np
import pickle #added
import glob #added
from copy import deepcopy
import os
from datetime import datetime, date
import pandas as pd


# def gen_vehicles_and_parameters(replications, numSpots, truckProps, nhts_data, 
#                                 doubleParkWeights, tauValues, zetaValues, saveIndex=1):
    
#     args = []
#     i = 0
#     reps = range(replications)
#     for rep in reps:
#         for numSpot in numSpots:
#             totalNumVehicles = list(range(11*numSpot, 34*numSpot, 11*numSpot))
#             # totalNumVehicles = list(range(11, 78, 11))
#             for numVehicles in totalNumVehicles:
#                 # numTrucks = list(range(1*numSpot, numVehicles*numSpot, 10*numSpot))

#                 for truckProp in truckProps:
#                     numTruck = int(np.round(truckProp*numVehicles))
#                     numCar = numVehicles-numTruck
#                     tempData = simulateData(min(max(numCar, 0), numVehicles), min(max(numTruck, 0), numVehicles), nhts_data)
#                     #args = []
#                     for doubleParkWeight in doubleParkWeights:
#                         cruisingWeight = 100-doubleParkWeight
#                         for tauValue in tauValues:
#                             for bufferValue in bufferValues:
#                                 for zetaValue in zetaValues:
#                                     #tempArg = (numSpot, tempData, bufferValue, zetaValue, doubleParkWeight, cruisingWeight, i, tauValue)
#                                     tempArg = {'numSpot': numSpot, 
#                                                     'tempData': tempData, 
#                                                     'bufferValue': bufferValue, 
#                                                     'zetaValue': zetaValue, 
#                                                     'doubleParkWeight': doubleParkWeight, 
#                                                     'cruisingWeight': cruisingWeight, 
#                                                     'i': i, 
#                                                     'tauValue': tauValue}
                                    
#                                     if (numSpot == 1 and doubleParkWeight == 100 and numVehicles == 77):
#                                         args.append(tempArg)
#                                     else:
#                                         args.append(tempArg)
#                                         pass
#                                     i += 1
#                                     print(i) 
    
    
#     saveFile = 'AaronRes/Veh_and_Params.dat'.format(saveIndex)

#     with open(saveFile, 'wb') as file:
#         pickle.dump(args, file)
#         file.close()
    
#     return args


def gen_vehicles_and_parameters(replications, numSpots, truckProps, nhts_data,
                                receivedDeltas, doubleParkWeights, tauValues,
                                bufferValues, zetaValues, rhoValues, nuValues):
    args = []
    i = 0
    #reps = range(0,5)
    for rep in range(0, replications):
        for numSpot in numSpots:
            totalNumVehicles = list(range(11*numSpot, 34*numSpot, 11*numSpot))

            for numVehicles in totalNumVehicles:
                for truckProp in truckProps:
                    numTruck = int(np.round(truckProp/100*numVehicles))
                    numCar = numVehicles-numTruck
                    baseData = simulateData(min(max(numCar, 0), numVehicles), min(max(numTruck, 0), numVehicles), nhts_data)
                    #args = []
                    for receivedDelta in receivedDeltas:
                        tempData = apply_received_delta(baseData, receivedDelta)
                        for doubleParkWeight in doubleParkWeights:
                            cruisingWeight = 100-doubleParkWeight
                            for tauValue in tauValues:
                                for bufferValue in bufferValues:
                                    for zetaValue in zetaValues:
                                        for rhoValue in rhoValues:
                                            for nuValue in nuValues:
                                                tempArg = (numSpot, tempData, bufferValue, zetaValue, doubleParkWeight, cruisingWeight, i, tauValue, rhoValue, nuValue) #, rhoValue, nuValue

                                                # if i == 8:
                                                #     print('i = ' + str(i))
                                                #runFullSetOfResults(*tempArg)
                                                if (numSpot == 1 and doubleParkWeight == 100 and numVehicles == 77):
                                                    args.append(tempArg)
                                                else:
                                                    args.append(tempArg)
                                                    pass
                                                i += 1
                                                print(i)
    
    current_date = date.today().strftime('%Y-%m-%d')                                            

    if('connorforsythe' in os.getcwd()):
        saveFile = '/Users/connorforsythe/Library/CloudStorage/Box-Box/CMU/SmartCurbs/Results/' + str(current_date) + '_Args.dat'
        #current_date = 'Connor Result_'+current_date
    else:
        saveFile = 'C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/' + str(current_date) + '_Args.dat'
        #current_date = 'Aaron Result_' + current_date    


    with open(saveFile, 'wb') as file:
        pickle.dump(args, file)
        file.close()
    
    return args


def apply_received_delta(data, received_delta):
    r = deepcopy(data)
    if(received_delta<0):
        r.loc[:, 'Received'] = r.loc[:, 'Received_OG']
    else:
        r.loc[:, 'Received'] = r.loc[:, 'a_i_OG']-received_delta

    r.loc[:, 'received_delta'] = received_delta

    return r




if __name__ == '__main__':

    #numSpots = [1, 2, 5, 10, 25]
    numSpots = [1, 2, 5]
    #numSpots = [1]
    # totalNumVehicles = list(range(11,78,11))
    # totalNumVehicles = [405]
    #doubleParkWeights = range(0, 101,25)
    doubleParkWeights = [1]
    bufferValues = [0]
    # bufferValues = [0]
    tauValues = [30]
    #zetaValues = [1,5]
    zetaValues = [5]
    truckProps = [100]
    replications = 3 #added by Aaron
    windowShift = 10 #added by Aaron
    rhoValues = [0, 60]
    nuValues = [0, 60]
    receivedDeltas = [-1, 300]# Aaron - this is the parameter that will enforce how early a request is received.
    #When receivedDelta < 0, the behavior will default to NHTS for cars and 30 minutes for truck

    np.random.seed(3102023)
    np.random.seed(16112023)



    #execute worflow
    
    #nhts_data = load_nhts_data(windowShift)  #added windowShift

    #args = gen_vehicles_and_parameters(replications, numSpots, truckProps, nhts_data, receivedDeltas, doubleParkWeights, tauValues, bufferValues, zetaValues, rhoValues, nuValues)

    
    # numThreads = mp.cpu_count()-2
    # #numThreads = 4
    # chunkSize = max(int(len(args)/numThreads), 1)
    # np.random.shuffle(args)
    # with Pool(numThreads) as pool:
    #     r = pool.starmap(runFullSetOfResults, args, chunksize=chunkSize)
    #     pool.close()


    #debugging workflow
    file = open('C:/Users/Aaron/Documents/GitHub/sliding_time_horizon_new/results/2023-12-15_Args.dat', 'rb')
    args_reload = pickle.load(file)
    file.close()
    run = args_reload[176]
    outcomes = runFullSetOfResults(numSpots = run[0],
                                   data = run[1],
                                   buffer = run[2],
                                   zeta = run[3],
                                   weightDoubleParking = 1,
                                   weightCruising = run[5],
                                   saveIndex = run[6],
                                   tau = run[7],
                                   rho = run[8],
                                   nu = run[9])






















    # numSpots = [10]
    # numSpots[0] = 1
    # numTrucks = list(range(5, 506,500))
    # numCars = list(500-np.array(numTrucks)+10)
    # doubleParkWeights = range(0, 101,100)
    # cruisingWeights = list(100-np.array(doubleParkWeights))
    # bufferValues = [10]
    # tauValues = [10]



    # np.random.seed(3102023)
    # np.random.seed(16112023)

    # nhts_data = load_nhts_data(windowShift)  #added windowShift
    
    # args = gen_vehicles_and_parameters(replications, numSpots, truckProps, nhts_data, 
    #                                 doubleParkWeights, tauValues, zetaValues)

    # #debugging workflow
    #
    # fp = 'AaronRes/Veh_and_Params.dat'
    # files = glob.glob(fp)
    #
    # args = []
    # for file in files:
    #     with open(file, 'rb') as temp:
    #         args.append(pickle.load(temp))
    #         temp.close()
    # args = args[0]
    #
    # run = args[8]
    # outcomes = runFullSetOfResults(idx = run['i'],
    #                     numSpots = 1,
    #                     data = run['tempData'],
    #                     buffer = run['bufferValue'],
    #                     zeta = run['zetaValue'],
    #                     weightDoubleParking = run['doubleParkWeight'],
    #                     weightCruising = run['cruisingWeight'],
    #                     tau = run['tauValue'])
    #
    #
    # slidingSorted = outcomes['sliding'].sort_values(['Assigned', 'a_i_Final'], ascending=[False, True])
    # fullSorted = outcomes['full'].sort_values(['Assigned', 'a_i_Final'], ascending=[False, True])
    # fcfsSorted = outcomes['FCFS'].sort_values(['Assigned', 'a_i_OG'], ascending=[False, True])

    # slidingFull = outcomes['sliding'][1]
    # slidingPastInfo = outcomes['sliding'][2]
    #run for record workflow
    # nhts_data = load_nhts_data(windowShift) 
    
    # args = gen_vehicles_and_parameters(replications, numSpots, truckProps, nhts_data, 
    #                                 doubleParkWeights, tauValues, zetaValues)
    
    # arg_tuples = []
    # for arg_set in args:
    #     arg_tuple = (arg_set['i'], arg_set['numSpot'], arg_set['tempData'], arg_set['bufferValue'],
    #                   arg_set['zetaValue'], arg_set['doubleParkWeight'], arg_set['cruisingWeight'],
    #                   0, arg_set['tauValue']) #0 is for the saveIndex input parameter
    #     arg_tuples.append(arg_tuple)
    
    # numThreads = mp.cpu_count()-2
    # #numThreads = 4
    # chunkSize = max(int(len(arg_tuples)/numThreads), 1)
    # np.random.shuffle(arg_tuples)
    # with Pool(numThreads) as pool:
    #     r = pool.starmap(runFullSetOfResults, arg_tuples, chunksize=chunkSize)
    #     pool.close()

    #a = simulateData(10, 10, nhts_data)
    #b = apply_received_delta(a, 15)
    
    # Connor's original code

    # args = []
    # i = 0
    # reps = range(0,5)
    # for rep in reps:
    #     for numSpot in numSpots:
    #         totalNumVehicles = list(range(11*numSpot, 34*numSpot, 11*numSpot))

    #         for numVehicles in totalNumVehicles:
    #             for truckProp in truckProps:
    #                 numTruck = int(np.round(truckProp/100*numVehicles))
    #                 numCar = numVehicles-numTruck
    #                 baseData = simulateData(min(max(numCar, 0), numVehicles), min(max(numTruck, 0), numVehicles), nhts_data)
    #                 #args = []
    #                 for receivedDelta in receivedDeltas:
    #                     tempData = apply_received_delta(baseData, receivedDelta)
    #                     for doubleParkWeight in doubleParkWeights:
    #                         cruisingWeight = 100-doubleParkWeight
    #                         for tauValue in tauValues:
    #                             for bufferValue in bufferValues:
    #                                 for zetaValue in zetaValues:
    #                                     for rhoValue in rhoValues:
    #                                         for nuValue in nuValues:
    #                                             tempArg = (numSpot, tempData, bufferValue, zetaValue, doubleParkWeight, cruisingWeight, i, tauValue, rhoValue, nuValue) #, rhoValue, nuValue

    #                                             # if i == 8:
    #                                             #     print('i = ' + str(i))
    #                                             #runFullSetOfResults(*tempArg)
    #                                             if (numSpot == 1 and doubleParkWeight == 100 and numVehicles == 77):
    #                                                 args.append(tempArg)
    #                                             else:
    #                                                 args.append(tempArg)
    #                                                 pass
    #                                             i += 1
    #                                             print(i)

    # saveFile = '/results/Veh_and_Params_15_Dec_2023.dat'

    # with open(saveFile, 'wb') as file:
    #     pickle.dump(args, file)
    #     file.close()

                                        # #numThreads = mp.cpu_count()-2
                                        # numThreads = 4
                                        # chunkSize = max(int(len(args)/numThreads), 1)
                                        # np.random.shuffle(args)
                                        # with Pool(numThreads) as pool:
                                        #     r = pool.starmap(runFullSetOfResults, args, chunksize=chunkSize)
                                        #     pool.close()