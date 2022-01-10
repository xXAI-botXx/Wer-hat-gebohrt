# .csv data io functions
import pandas as pd
import yaml
import os
from functools import reduce
from enum import Enum
import dask.dataframe

loadData_mode = Enum('loadData_mode', 'NONE DASK')

def read_csv(csvFile, mode=loadData_mode.NONE, sampleRate=72000):
    """Method to read sensor time series data from a .csv file.
    
    Parameters
    ----------
    csvFile : string
        The path to the .csv file to read.

    sampleRate : number
        The measurement frequency.
    
    mode: enum
        Select load method

    Returns
    ----------
    df : pandas.DataFrame
        A pandas DataFrame representing the sensor data.
    """


    # Determine start time of measurement
    startTime = pd.to_datetime(os.path.basename(os.path.dirname(csvFile)), format = '%Y_%m_%d_%H-%M-%S')

    #Use Dask Dataframe
    if mode == loadData_mode.DASK:
        df = dask.dataframe.read_csv(csvFile, names=['Audio', 'Voltage', 'Current'])
        df = df.compute()
    
    else:
        #Use Pandas Dataframe
        df = pd.read_csv(csvFile, names=['Audio', 'Voltage', 'Current'])


    # Scale sensor channels
    df.Voltage = df.Voltage * 2.45
    df.Current = -15.0 * df.Current + 37

    # Construct date time index based on start time and sample rate
    df['Time'] = pd.date_range(start = startTime, periods = len(df), freq = pd.Timedelta(seconds = 1 / sampleRate))

    return df



def read_metadata(yamlFile):
    """Method to read meta data from a .yaml file.
    
    Parameters
    ----------
    yamlFile : string
        The path to the .yaml file to read.
    
    Returns
    ----------
    df : pandas.Series
        A pandas Series with the meta data information.
    """

    mds = pd.Series()

    with open(yamlFile, 'r') as f:
        meta = yaml.safe_load(f)
        mds['BoreholeSize'] = meta['boreholeSize']
        mds['Material'] = meta['material']
        mds['Gear'] = meta['gear']
        mds['SampleRate'] = meta['sampleRate']
        mds['BatteryLevel'] = meta['batteryLevel']
        mds['DrillType'] = meta['drillType']
        mds['Operator'] = meta['operator']
        mds['Annotations'] = pd.Series(reduce((lambda map1, map2: {**map1, **map2}), meta['anomalyTimestamps']))

    return mds



def read_csv_dataset(datasetPath, csvName='capture.csv', metaName='meta.yaml'):
    df = read_csv(os.path.join(datasetPath, csvName))
    mds = read_metadata(os.path.join(datasetPath, metaName))

    return (df, mds)



def load_tsfresh(datasetPath, seriesIDs, csvName='capture.csv', metaName='meta.yaml'):
    sdf = pd.DataFrame()
    mdf = pd.DataFrame()
    sID = 0

    for seriesID in seriesIDs:
        measurements = os.listdir(os.path.join(datasetPath, seriesID))

        for mDir in measurements:
            if os.path.isfile(os.path.join(datasetPath, seriesID, mDir)):
                continue

            metaData = read_metadata(os.path.join(datasetPath, seriesID, mDir, metaName))
            sensorData = read_csv(os.path.join(datasetPath, seriesID, mDir, csvName))

            metaData['ID'] = sID
            sensorData['ID'] = sID

            metaData.drop(index=['Annotations'], inplace=True)      # drop annotations
            mdf = pd.concat([mdf, metaData], axis=1, ignore_index=True)
            sdf = pd.concat([sdf, sensorData], axis=0, ignore_index=True)

            sID += 1

    mdf = mdf.transpose()

    return (sdf, mdf)


def load_single_data(person, data_path:str) -> pd.DataFrame:
    measurements = os.listdir(f"{data_path}/{person}")

    # get latest measurement
    measurements.sort()
    i = -1
    latest_drill = measurements[i]
    while os.path.isfile(f"{data_path}/{person}/{latest_drill}"):
        if i*-1 > len(measurements):
            # no dir
            return None
        i -= 1
        latest_drill = measurements[i]

    sensorData = read_csv(f"{data_path}/{person}/{latest_drill}/capture.csv")

    sensorData['ID'] = 0

    return sensorData

