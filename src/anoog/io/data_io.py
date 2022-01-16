import os
import sys
import csv
from enum import Enum

import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn import tree #New Import
from sklearn.feature_selection import SelectKBest, f_classif #New Import
from sklearn.feature_selection import VarianceThreshold #New Import
from sklearn.feature_selection import SelectFromModel #New Import

# For Feature Extraction
import tsfresh as tsf

# nötig???
# Set up system path to include our "anoog" python package
#sys.path.append('../src')
from . import csv_io as io
from ..model import get_most_important_features_as_list

extraction_mode = Enum('extraction_mode', 'NONE TSFRESH_WITH_PARAMS TSFRESH MANUEL')
selection_mode = Enum('selection_mode', 'NONE TSFRESH SELECTKBEST VARIANCE MODEL_BASED')  #New Added Modes: (SelectKBest, VarianceThresholding, Modelbased)

# data loading
def load_data(data_path='../../../data/2021-11-09', 
              persons=['tippolit', 'vkorzev'], 
              extraction=extraction_mode.MANUEL,
              show_extraction=False,
              selection=selection_mode.NONE,
              train_test_split=False,
              test_size=0.3,
              save_as_csv=False,
              csv_name=None,
              normalize=False) -> pd.DataFrame:
    """Loads Data and prepares them.
    Feature Extraction and Feature Selection.
    Labeling and Resampling.

    Returns DataFrame"""

    # Loading data and meta-data
    seriesIDs = persons

    (data, meta_data) = io.load_tsfresh(data_path, seriesIDs)

    resampled_data = resampling(data)

    # Feature Extraction -> Row Time Data are not useful for ML-Algorithm
    X_imputed = feature_extraction(resampled_data, extraction, data_path, show_extraction)

    # Target Labeling
    y = y_labeling(X_imputed, meta_data, extraction)

    datasets = split_data(X_imputed, y, test_size, train_test_split)

    for data in datasets:
        # SEITENEFFEKT
        data[0] = feature_selection(data[0], data[1], selection, data_path)

    # Target adding + Normalizing
    result_datasets = []
    for data in datasets:
        new_dataset = data[0]
        new_dataset['y'] = data[1]

        # Normalizing
        if normalize:
            scaler = MinMaxScaler()
            new_dataset = pd.DataFrame(scaler.fit_transform(new_dataset), columns=new_dataset.columns)

        result_datasets += [new_dataset]

    # Saving
    if save_as_csv:
        save_data(data_path, result_datasets, csv_name)

    # returns
    if len(result_datasets) == 1:
        return result_datasets[0]
    else:
        return result_datasets


def load_single_data(person_id,
                        person='tippolit',
                        data_path='../../../data/2021-11-09',
                        drill_id=0, 
                        extraction=extraction_mode.MANUEL,
                        show_extraction=False,
                        selection=selection_mode.NONE,
                        train_test_split=False,
                        test_size=0.3,
                        save_as_csv=False,
                        csv_name=None,
                        normalize=False) -> pd.DataFrame:
    """Loading a single Drill. The last drill in the folder.
    returns a DataFrame"""

    data = io.load_single_data(person, data_path)
    if type(data) == None:
        # Case: no directory
        raise ValueError(f"Dataentry is None! Loaded from {data_path}")

    # Override ID
    data['ID'] = drill_id

    if data.empty:
        return data

    data = resampling(data)

    #y = pd.Series(LabelEncoder().fit_transform(person_id), index=meta_data['ID'])    
    data['y'] = person_id

    # Feature Extraction -> Row Time Data are not useful for ML-Algorithm
    data = feature_extraction(data, extraction, data_path, show_extraction)
    data['y'] = person_id

    data = feature_selection(data.loc[:, data.columns != 'y'], data['y'], selection, data_path)
    data['y'] = person_id

    # Normalizing
    if normalize:
        scaler = MinMaxScaler()
        data = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
     
    # Saving
    if save_as_csv:
        save_data(data_path, [data], csv_name)

    # return
    return data
    

# To many data -> Resampling for few data
def resampling(data) -> pd.DataFrame:
    resamplingInterval = '10ms'

    resampled_data = data.resample(resamplingInterval, label='right', closed='right', on='Time').mean()
    resampled_data.dropna(inplace=True)
    resampled_data.reset_index(inplace=True)
    return resampled_data


def y_labeling(data, meta_data, extraction):
    labelEnc = LabelEncoder()
    y = y_target = pd.Series(labelEnc.fit_transform(meta_data['Operator'].values), index=meta_data['ID'])

    if extraction == extraction_mode.NONE:
        y = []
        for i, id in enumerate(data['ID'].unique()):
            #print(id)
            #print(data[data['ID'] == id].shape)
            y += [y_target[i]]*data[data['ID'] == id].shape[0]

        y = pd.Series(y)

    return y

# For manuel Feature
def extract_feature(data, from_feature:str, function):
    """Extracts Features of a drill timeseries data.
    
    Returns a list"""
    feature_collection = []
    for id in data['ID'].unique():
        #feature_collection += [data[data['ID'] == id][from_feature].function()]
        feature_collection += [function(data[data['ID']==id][from_feature])]
    return feature_collection


def advanced_feature_extraction(df) -> pd.DataFrame:
    # Calc mean and transform time in duration
    time = []
    for i in df["Time"]:
        time.append(str(i))

    zeit = []
    for i in time:
        zeit.append(i[11:])

    stunden = []
    minuten = []
    sekunden = []
    for i in zeit:
        stunden.append(i[:2])
        minuten.append(i[3:5])
        sekunden.append(i[6:])

    #Konvertierung zu Sekunden
    sec = []

    for st in stunden:
        sec.append(float(st)*3600)
    z = 0
    for mi in minuten:
        sec[z]=sec[z]+(float(mi)*60)
        z +=1
    z = 0
    for se in sekunden:
        sec[z]=sec[z]+float(se)
        z +=1
    df["Time"] = sec

    current = []
    z=1
    num = 0
    current_mean = 0
    for i in df["ID"].unique():
        for j,value in enumerate(df["Current"]):
            if df["ID"][j] == i:
                current_mean += value
                num+=1
        current += [current_mean/num]
        current_mean = 0
        num = 0

    zeit = []
    z=1
    num = 0
    Zeit = []
    for i in df["ID"].unique():
        for j,value in enumerate(df["Time"]):
            if df["ID"][j] == i:
                Zeit += [value]
                num+=1
        zeit += [Zeit[-1]-Zeit[0]]
        Zeit = []
        num = 0 

    voltage = []
    z=1
    num = 0
    voltage_mean = 0
    for i in df["ID"].unique():
        for j,value in enumerate(df["Voltage"]):
            if df["ID"][j] == i:
                voltage_mean += value
                num+=1
        voltage += [voltage_mean/num]
        voltage_mean = 0
        num = 0 

    audio = []
    z=1
    num = 0
    audio_mean = 0
    for i in df["ID"].unique():
        for j,value in enumerate(df["Audio"]):
            if df["ID"][j] == i:
                audio_mean += value
                num+=1
        audio += [audio_mean/num]
        audio_mean = 0
        num = 0  

    ID = np.arange(len(zeit))    # a
    #b = np.arange(25)
    #ID=np.concatenate((a, b))
    d = {"Time" : zeit,
            "Audio" : audio,
            "Voltage" : voltage,
            "Current" : current,
            "ID" : ID}
    df_new = pd.DataFrame(data=d)

    # Berechnung vom Widerstand Ohm
    df_new["Resistance"] = df_new["Current"] / df_new["Voltage"]

    # Berechnung der Elektrischen Leistung P in Joule
    df_new["Power"] = df_new["Current"] * df_new["Voltage"]

    # Berechnung der Arbeit W
    df_new["Work"] = df_new["Current"] * df_new["Voltage"] * df_new["Time"]

    # Berechnung von mAh(milli Ampere Stunden)
    df_new["mAh"] = (df_new["Current"] / 60) * 1000

    # Berechnung von Wh(Watt Stunden)
    df_new["Wh"] = df_new["mAh"] * df_new["Voltage"]

    return df_new.drop(columns=['ID'])


# data feature extraction + labeling
def feature_extraction(data, mode, data_path, show=True) -> pd.DataFrame:
    if mode == extraction_mode.TSFRESH:
        # extract Features of time data
        reverse_show = not show
        X_extracted = tsf.extract_features(data, column_id="ID", column_sort="Time", disable_progressbar=reverse_show)

        # Impute (replace Nan/Inf) features
        return tsf.utilities.dataframe_functions.impute(X_extracted)
    elif mode == extraction_mode.TSFRESH_WITH_PARAMS:
        params = load_features(data_path)
        X_extracted = tsf.extract_features(data, column_id="ID", 
                                        column_sort="Time", kind_to_fc_parameters=params)
        
        # Impute (replace Nan/Inf) features
        return tsf.utilities.dataframe_functions.impute(X_extracted)
    elif mode == extraction_mode.MANUEL:    # by hand
        X_extracted = pd.DataFrame()

        for feature in ['Audio', 'Current', 'Voltage']:
            for new_feature in [('min',np.min), ('max',np.max), ('mean',np.mean), ('median',np.median), ('std',np.std)]:
                X_extracted[feature.lower()+"_"+new_feature[0]] = extract_feature(data, feature, new_feature[1])
        
        afe = advanced_feature_extraction(data)
        afe = afe.drop(columns=['Audio', 'Voltage', 'Current'], inplace=False)
        #X_extracted = X_extracted.drop(columns=['audio_mean', 'voltage_mean', 'current_mean'], inplace=False)
        return pd.concat([X_extracted, afe], axis=1)
    else:
        return data


# data feature extraction + labeling
def feature_selection(X, y, mode, data_path) -> pd.DataFrame:
    if mode == selection_mode.TSFRESH:
        # Selecting only important Features
        X_filtered = tsf.select_features(X, y)

        # Get selcted columns/features -> saving
        kind_to_fc_parameters = tsf.feature_extraction.settings.from_columns(X_filtered)
        save_features(data_path, kind_to_fc_parameters)

        return X_filtered
    else:
        return X


def split_data(X, y, test_size_in_percent=0.3, should_split=False) -> list:
    if should_split:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size_in_percent, stratify=y) 
        return [[X_train, y_train], [X_test, y_test]]
    else:
        return [[X, y]]


def save_features(data_path, params:dict):
    path = "/".join(data_path.split("/")[:-1])
    name = 'features_00.txt'
    files = os.listdir(path)
    i = 0
    while name in files:
        name = f"features_{i:02d}.txt"
        i += 1

    with open(path+"/"+name, "w") as f:
        f.write("{")
        for key, value in params.items():
            f.write(f"'{key}':{value},\n")
        f.write("}")


def load_features(data_path, name=None):
    # load features
    path = "/".join(data_path.split("/")[:-1])
    if name == None or not name.endswith(".txt"):
        name = 'features_99.csv'
        files = os.listdir(path)
        i = 99
        while name not in files:
            name = f"features_{i:02d}.txt"
            i -= 1

    with open(path+"/"+name, "r") as f:
        str_dict = ""
        for line in f.readlines():
            str_dict += line
    
    new_dict = eval(str_dict)

    return new_dict


def save_data(data_path, datasets, name):
    path = "/".join(data_path.split("/")[:-1])
    files = os.listdir(path)
    i = 0

    if name == None or not name.endswith(".csv"):
        name = 'data_save_00.csv'
        
    while name in files:
        name = f"features_{i:02d}.csv"
        i += 1

    for i, dataset in enumerate(datasets):
        if len(datasets) > 1:
            modified_name = f"{name.split('.csv')[0]}_{i}.csv"
        else:
            modified_name = name
            
        dataset.to_csv(path+"/"+modified_name, index=False)
        print("Saving DataFrame at:", path+"/"+modified_name)


def X_y_split(data):
    return data.iloc[:, :-1], data.loc[:, 'y']
    #or
    #return data.drop(columns=['y']), data.y


#function for different Selection methods
def feature_selectionMethod(X, y, mode): #New function
    if mode == selection_mode.SELECTKBEST:
        selectKBest = SelectKBest(f_classif, k=5).fit(X, y) #default= sf_classif,  k can be changed
        important_features = rename(selectKBest.get_support(), list(X.columns))
        X_new = X[important_features]
        return X_new
    elif mode == selection_mode.VARIANCE:
        varianceSelect= VarianceThreshold(threshold=100000) #threshold can be changed
        varianceSelect.fit_transform(X)
        important_features = rename(varianceSelect.get_support(), list(X.columns))
        X_new = X[important_features]
        return X_new
    elif mode == selection_mode.MODEL_BASED:
        Dtree = tree.DecisionTreeClassifier() #Default Values yet
        SelectM = SelectFromModel(estimator=Dtree) #Classifier can be changed
        SelectM.fit(X, y)
        important_features = rename(SelectM.get_support(), list(X.columns))
        X_new = X[important_features]
        return X_new

    else:
        return X


#function for feature name mask
def rename(score, list_names): #New function
    name_result = []
    for i, x in enumerate(score):
        if x == True:
            name_result.append(list_names[i])
    
    return name_result

def model_based_feature_selection(X, y, n=5):
    """Get the n best Features. Selected by a RandomForest.
    Returns new X with selected Features."""
    model = RandomForestClassifier(n_estimators=100, 
                               bootstrap = True,
                               max_features = 'sqrt')
    # Fit on training data
    model = model.fit(X, y)

    best_features = get_most_important_features_as_list(model, X, n=5)

    return X.loc[:, best_features]

# for testing
def remove_audio_features(data) -> pd.DataFrame:
    return data.drop(columns=['audio_mean', 'audio_max', 'audio_min', 'audio_median', 'audio_std'])
