"""
This module is used to hold the train/predict data and also to train/predict with a ML-Algorithm

Author: Tobia Ippolito
"""

import os
from enum import Enum
from datetime import datetime
from time import time
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

from ..model import train_random_forest, train_svc, train_knn, train_naive_bayes, train_logistic_regression, train_adaboost, train_voting_classifier
from ..model import predict, predict_proba 
from ..io import load_single_data, extraction_mode, selection_mode, X_y_split

ALGORITHM = Enum('ALGORITHM', 'RANDOM_FOREST SVC KNN NAIVE_BAYES LOGISTIC_REGRESSION ADA_BOOST VOTING_CLASSIFIER')

class AI_Model(object):
    """
    This class used to:
        - collect train- and predict-data
        - train supervised classification ML-Algorithmn
        - make prediction with the trained model 

    This class makes an protocoll of it tasks, to understand the progress.
    By init or resetting it clears this protocol.
    """
    def __init__(self):
        """
        Constructor method
        """
        self.train_data = pd.DataFrame()
        self.predict_data = pd.DataFrame()
        self.model = None
        self.should_normalize = False
        self.drill_id = 0
        self.file_path = os.path.abspath(__file__).replace("\\", "/")
        self.dir_path = "/".join(self.file_path.split("/")[:-1])
        self.clean_log()
        # constant
        self.cv = 3

    def add_train_dataset(self, person_id:int, person:str, data_path:str):
        """
        Load last train-drill-data in DataFrame. Using buffer with 30s timeout (if the data need some time to saving).
        
        :param person_id: ID of the Person who drill last time.
        :type person_id: int
        :param person: Name of the Person who drill last time.
        :type person: str
        :param data_path: Path to the data-directory. To know where collect the data.
        :type data_path: str
        """
        now = datetime.now()
        date = f"{now.year}-{now.month}-{now.day}"
        data_path = f"{data_path}/{date}"
        self.write_log("Load a single train_data")
        # load new dataset + buffer
        begin = time()
        while True:
            try:
                new_data = load_single_data(person_id,
                                            person=person,
                                            data_path=data_path, 
                                            drill_id =self.drill_id,
                                            extraction=extraction_mode.MANUEL,
                                            #extraction=extraction_mode.TSFRESH,
                                            show_extraction=False,
                                            selection=selection_mode.NONE,
                                            train_test_split=False,
                                            test_size=0.3,
                                            save_as_csv=False,
                                            csv_name=None,
                                            normalize=False)
                if new_data.empty != True:
                    break
            except FileNotFoundError as e:
                print("File not found...")
                if int(time() - begin) > 30:
                    print("Wait too long for File saving!")
                    raise FileNotFoundError("While Saving Single Train-Data")
            except IndexError as e:
                print("Latest drill not found (Index out of Bounds)...")
                if int(time() - begin) > 30:
                    print("Wait too long for File saving!")
                    raise IndexError("While Saving Single Train-Data")

        if type(new_data) != None:
            # add new dataset
            self.train_data = self.train_data.append(new_data)
            print("Dataentry added:\n", new_data)
            self.drill_id += 1
        self.write_log("Loading a single train_data is finished")

    def add_predict_dataset(self, person_id:int, person:str, data_path:str):
        """
        Load last predict-drill-data in DataFrame. Using buffer with 30s timeout (if the data need some time to saving).

        :param person_id: ID of the Person who drill last time.
        :type person_id: int
        :param person: Name of the Person who drill last time.
        :type person: str
        :param data_path: Path to the data-directory. To know where collect the data.
        :type data_path: str
        """
        now = datetime.now()
        date = f"{now.year}-{now.month}-{now.day}"
        data_path = f"{data_path}/{date}"
        self.write_log("Load a single predict_data")
        # load new dataset + buffer
        begin = time()
        while True:
            try:
                new_data = load_single_data(person_id,
                                            person=person,
                                            data_path=data_path, 
                                            drill_id =self.drill_id,
                                            extraction=extraction_mode.MANUEL,
                                            show_extraction=False,
                                            selection=selection_mode.NONE,
                                            train_test_split=False,
                                            test_size=0.3,
                                            save_as_csv=False,
                                            csv_name=None,
                                            normalize=False)
                if new_data.empty != True:
                    break
            except FileNotFoundError as e:
                print("File not found...")
                if int(time() - begin) > 30:
                    print("Wait too long for File saving!")
                    raise FileNotFoundError("While Saving Single Predict-Data")
            except IndexError as e:
                print("Latest drill not found (Index out of Bounds)...")
                if int(time() - begin) > 30:
                    print("Wait too long for File saving!")
                    raise IndexError("While Saving Single Predict-Data")
                    
        if type(new_data) != None:
            # add new dataset
            try:
                self.predict_data = self.predict_data.append(new_data.drop(columns=['y']))
            except KeyError as e:
                self.predict_data = self.predict_data.append(new_data)
            self.drill_id += 1
        self.write_log("Loading a single predict_data is finished")

    def remove_last_train_dataset(self):
        """
        Removes last train-data-entry from DataFrame.
        """
        self.train_data = self.train_data.head(self.train_data.shape[0]-1)
        self.write_log("Removed Last Train Dataset")

    def remove_last_predict_dataset(self):
        """
        Removes last predict-data-entry from DataFrame.
        """
        self.predict_data = self.predict_data.head(self.predict_data.shape[0]-1)
        self.write_log("Removed Last Predict Dataset")

    def remove_predict_dataset(self):
        """
        Removes complete predict-data from DataFrame.
        """
        self.predict_data = pd.DataFrame()
        self.write_log("Removed Complete Predict Dataset")

    def train(self, algorithm=ALGORITHM.RANDOM_FOREST, auto_params=False, normalize=True):
        """
        Train a model of choice. The Hyperparameters can choose as predefined or searched with GridSearchCV.
        And the data can be normalized if needed.

        Note:
        If there are not enough data-entries, GridSearchCV don't be choosen. 
        There have to be more than 5 entries.

        :param algorithm: To know which ML-Algorithmn to choose
        :type algorithm: int, optional
        :param auto_params: To know if Hyperparameter choose predefined or GridSearchCV
        :type auto_params: str, optional
        :param normalize: To know if the data should be normalized
        :type normalize: str, optional
        """
        # auto-params only if greater than CV*2
        if auto_params:
            if len(self.train_data) < self.cv*2:
                auto_params = False

        self.write_log("Start train")
        self.should_normalize = normalize
        self.train_data = self.remove_unused_columns(self.train_data)
        X, y = X_y_split(self.train_data)
        if algorithm == ALGORITHM.RANDOM_FOREST:
            self.model = train_random_forest(X, y, auto_params=auto_params, normalize=normalize, cv=self.cv)
        elif algorithm == ALGORITHM.SVC:
            self.model = train_svc(X, y, auto_params=auto_params, normalize=normalize, cv=self.cv)
        elif algorithm == ALGORITHM.KNN:
            self.model = train_knn(X, y, auto_params=auto_params, normalize=normalize, cv=self.cv)
        elif algorithm == ALGORITHM.NAIVE_BAYES:
            self.model = train_naive_bayes(X, y, auto_params=auto_params, normalize=normalize, cv=self.cv)
        elif algorithm == ALGORITHM.LOGISTIC_REGRESSION:
            self.model = train_logistic_regression(X, y, auto_params=auto_params, normalize=normalize, cv=self.cv)
        elif algorithm == ALGORITHM.ADA_BOOST:
            self.model = train_adaboost(X, y, auto_params=auto_params, normalize=normalize, cv=self.cv)
        elif algorithm == ALGORITHM.VOTING_CLASSIFIER:
            self.model = train_voting_classifier(X, y, auto_params=auto_params, normalize=normalize, cv=self.cv)
        self.write_log("End train")

    def predict(self):
        """
        Predicts the predict-data with the trained model.
        If the train-data was normalize, the predict-data also do. Normalization is working with train-data,
        to have the same scale.

        If there are more than one predict-data-entry. Every Entry going to predict 
        and the probabilities are stacked (soft voting) and scaled to 100%.

        :return: Returns the prediction probability
        :rtype: tuple(float, float)
        """
        self.write_log("Start Predict")
        X, y = X_y_split(self.train_data)    # for normalization
        self.predict_data = self.remove_unused_columns(self.predict_data)
        result = predict_proba(self.model, self.predict_data, X, self.should_normalize)
        # If more then one drill -> we would like to add the votes
        self.write_log(f"Predict Result: {result}")
        #print(result)
        votes = np.sum(result, axis=0)
        if len(votes) == 1:
            votes = np.append(votes, 0.0)
        all = votes[0] + votes[1]
        proba_result = [votes[0]/all, votes[1]/all]
        self.write_log(f"Voted: {proba_result}")
        self.write_log("End Predict")
        return proba_result

    def remove_unused_columns(self, data):
        """
        Tries to remove some irrelevant Features, which shouldn't exist anymore.
        It's no problem, if they don't exist.

        :param data: Data, which will be trimmed
        :type data: pd.DataFrame

        :return: Return new trimmed DataFrame
        :rtype: pd.DataFrame
        """
        new_data = data.copy()
        if 'Audio' in data.columns:
            new_data = new_data.drop(columns=['Audio'])
        if 'Current' in data.columns:
            new_data = new_data.drop(columns=['Current'])
        if 'Voltage' in data.columns:
            new_data = new_data.drop(columns=['Voltage'])
        if 'ID' in data.columns:
            new_data = new_data.drop(columns=['ID'])
        return new_data

    def draw_result(self, person1_name, person1_proba, person2_name, person2_proba, save_path):
        """
        Plots the result of probability classification as bar-chart with 2 charts.

        Arguments:
            - person1_name as str (to plot the name)
            - person1_proba as int (to plot the probability)
            - person2_name as str (to plot the name)
            - person2_proba as int (to plot the probability)
            - save_path as str (to know where to save the plot)
        

        :param person1_name: Name of the first person.
        :type person1_name: str
        :param person1_proba: Probability of the first Person. Defines the height of one bar.
        :type person1_proba: float or int
        :param person2_name: Name of the second person.
        :type person2_name: str
        :param person2_proba: Probability of the second Person. Defines the height of one bar.
        :type person2_proba: float or int
        :param save_path: Path, where the plot should be saved.
        :type save_path: str
        """
        plt.style.use('seaborn-whitegrid')
        fig = plt.figure()
        ax = plt.axes()

        ax.bar(x=[person1_name, person2_name], height=[person1_proba, person2_proba])
        ax.set_title("Prediction")
        ax.set_xlabel('Candidates')
        ax.set_ylabel('Probability')

        plt.savefig(save_path, transparent=False)

    def clean_log(self):
        """
        Clears the protocol of the AI-Model.

        Should be called once at the beinning of the program.
        """
        with open(f"{self.dir_path}/output/AI-Model-log.txt", "w") as f:
            f.write("")

    def reset(self):
        """
        Sets the variables (like the train and predict-DataFrame) to initial values.
        (Clears also the protocol)
        """
        self.train_data = pd.DataFrame()
        self.predict_data = pd.DataFrame()
        self.model = None
        self.drill_id = 0
        self.file_path = os.path.abspath(__file__).replace("\\", "/")
        self.dir_path = "/".join(self.file_path.split("/")[:-1])
        self.clean_log()

    def write_log(self, message:str):
        """
        Writes a String in the protocol-file.

        This method should be used to add a entry to the protocoll.

        :param message: Message which will be saved in log.
        :type message: str
        """
        now = datetime.now()
        date_str = f"{now.hour}:{now.minute}:{now.second}"
        with open(f"{self.dir_path}/output/AI-Model-log.txt", "a") as f:
            message = f"\n\n- log entry at {date_str}:: {message}"
            f.write(message)

