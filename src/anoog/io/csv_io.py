"""
This module used to load the drill data from csv.

Contains functions to load drill-data simply and without many features, created from drillcapture.

Author for :func:`~anoog.io.csv_io.read_csv`: Syon Kadkade
Author for :func:`~anoog.io.csv_io.load_single_data`: Tobia Ippolito
Author for :func:`~anoog.io.csv_io.read_csv` and the other functions: Stefan Glaser
"""


import pandas as pd
import yaml
import os
from functools import reduce
from enum import Enum
import dask.dataframe

loadData_mode = Enum('loadData_mode', 'NONE DASK')

def read_csv(csvFile, mode=loadData_mode.NONE, sampleRate=72000):
    """
    Method to read sensor time series data from a .csv file.
    
    :param mode: The path to the .csv file to read.
    :type mode: str
    :param mode: The measurement frequency.
    :type mode: int
    :param mode: Defines how to load the data.
    :type mode: :class:`~anoog.io.csv_io.loadData_mode`

    :return: A pandas DataFrame representing the sensor data.
    :rtype: pd.DataFrame
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
    """
    Method to read meta data from a .yaml file.
    
    :param yamlFile: The path to the .yaml file to read.
    :type yamlFile: str

    :return: A pandas Series with the meta data information.
    :rtype: pd.Series
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
    """
    Loads a measurement dataset and meta-data.

    Uses :func:`~anoog.io.csv_io.read_csv` and :func:`~anoog.io.csv_io.read_metadata` functions.
    
    :param datasetPath: The path to the dataset, to load it.
    :type datasetPath: str
    :param csvName: The name of the measurement file.
    :type csvName: str, optional
    :param metaName: The name of the measurement metadata file.
    :type metaName: str, optional

    :return: The measurement and the metadata of the drill.
    :rtype: tuple of pd.DataFrame
    """
    df = read_csv(os.path.join(datasetPath, csvName))
    mds = read_metadata(os.path.join(datasetPath, metaName))

    return (df, mds)



def load_tsfresh(datasetPath, seriesIDs, csvName='capture.csv', metaName='meta.yaml'):
    """
    Loads a complete drill-data created from drillcapture.

    :param datasetPath: The path to the dataset, to load it.
    :type datasetPath: str
    :param seriesIDs: The operators/folder names which should be loaded.
    :type seriesIDs: list of str
    :param csvName: The name of the measurement file.
    :type csvName: str, optional
    :param metaName: The name of the measurement metadata file.
    :type metaName: str, optional

    :return: The measurement and the metadata of all drills.
    :rtype: tuple of pd.DataFrame
    """
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
    """
    Loads a single drill-data created from drillcapture.

    Uses the last-drill.

    :param person: The person, who drilled at last.
    :type person: str
    :param datasetPath: The path to the dataset, to load it.
    :type datasetPath: str

    :return: The measurement of one drill.
    :rtype: tuple of pd.DataFrame
    """
    measurements = os.listdir(f"{data_path}/{person}")

    # get latest measurement
    measurements.sort()
    i = -1
    latest_drill = measurements[i]
    while os.path.isfile(f"{data_path}/{person}/{latest_drill}"):
        if i*-1 > len(measurements):
            # no dir
            raise FileNotFoundError(f"No Files in Directory{data_path}/{person}/{latest_drill}")
        i -= 1
        latest_drill = measurements[i]

    sensorData = read_csv(f"{data_path}/{person}/{latest_drill}/capture.csv")

    sensorData['ID'] = 0

    return sensorData

