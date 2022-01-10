import os
from enum import Enum
from datetime import datetime
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

from ..model import train_random_forest, train_svc, train_knn
from ..model import predict, predict_proba 
from ..io import load_single_data, extraction_mode, selection_mode, X_y_split

ALGORITHM = Enum('ALGORITHM', 'RANDOM_FOREST SVC KNN')

class AI_Model(object):
    def __init__(self, terminal):
        self.train_data = pd.DataFrame()
        self.predict_data = pd.DataFrame()
        self.model = None
        self.drill_id = 0
        self.terminal = terminal
        self.file_path = os.path.abspath(__file__).replace("\\", "/")
        self.dir_path = "/".join(self.file_path.split("/")[:-1])
        self.clean_log()

    # blocking GUI for some time -> blocking the logic?
    def block(self):
        self.write_log("Block parts of the GUI")
        self.terminal.block()

    def unblock(self):
        self.write_log("Unblock parts of the GUI")
        self.terminal.unblock()

    # should run in Thread or not? -> if fast enough = then no + blocking not really required when not in thread, because in stop -method these elements are blocked already
    
    def add_train_dataset(self, person_id, person, data_path:str):
        now = datetime.now()
        date = f"{now.year}-{now.month}-{now.day}"
        data_path = f"{data_path}/{date}"
        #self.block()
        self.write_log("Load a single train_data")
        # load new dataset
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

        if type(new_data) != None:
            # add new dataset
            self.train_data = self.train_data.append(new_data)
            self.drill_id += 1
        self.write_log("Loading a single train_data is finished")
        #self.unblock()

    # FIXME
    def add_predict_dataset(self, person_id, person, data_path:str):
        now = datetime.now()
        date = f"{now.year}-{now.month}-{now.day}"
        data_path = f"{data_path}/{date}"
        #self.block()
        self.write_log("Load a single predict_data")
        # load new dataset
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

        if type(new_data) != None:
            # add new dataset
            self.predict_data = self.predict_data.append(new_data.drop(columns=['y']))
            self.drill_id += 1
        self.write_log("Loading a single predict_data is finished")
        #self.unblock()

    # FIXME
    def remove_last_train_dataset(self):
        #self.train_data.drop(self.train_data.tail(1).index, inplace=True)
        self.train_data = self.train_data.head(self.train_data.shape[0]-1)
        self.write_log("Removed Last Train Dataset")
        print(self.train_data)

    def remove_last_predict_dataset(self):
        #self.predict_data.drop(self.predict_data.tail(1).index, inplace=True)
        self.predict_data = self.predict_data.head(self.predict_data.shape[0]-1)
        self.write_log("Removed Last Predict Dataset")

    def remove_predict_dataset(self):
        self.predict_data = pd.DataFrame()
        self.write_log("Removed Complete Predict Dataset")

    # oder fit
    def train(self, algorithm=ALGORITHM.RANDOM_FOREST, auto_params=False, normalize=True):
        self.write_log("Start train")
        X, y = X_y_split(self.train_data)
        if algorithm == ALGORITHM.RANDOM_FOREST:
            self.model = train_random_forest(X, y, auto_params=auto_params, normalize=False)
        elif algorithm == ALGORITHM.SVC:
            self.model = train_svc(X, y, auto_params=auto_params, normalize=True)
        elif algorithm == ALGORITHM.KNN:
            self.model = train_knn(X, y, auto_params=auto_params, normalize=True)
        self.write_log("End train")

    def predict(self):
        self.write_log("Start Predict")
        result = predict_proba(self.model, self.predict_data)
        # If more then one drill -> we would like to add the votes
        self.write_log(f"Predict Result: {result}")
        votes = np.sum(result, axis=0)    # right? or axis=1?
        if len(votes) == 1:
            votes = np.append(votes, 0.0)
        all = votes[0] + votes[1]
        proba_result = [votes[0]/all, votes[1]/all]
        self.write_log(f"Voted: {proba_result}")
        self.write_log("End Predict")
        return proba_result

    def draw_result(self, person1_name, person1_proba, person2_name, person2_proba, save_path):
        plt.style.use('seaborn-whitegrid')
        fig = plt.figure()
        ax = plt.axes()

        ax.bar(x=[person1_name, person2_name], height=[person1_proba, person2_proba])
        ax.set_title("Prediction")
        ax.set_xlabel('Candidates')
        ax.set_ylabel('Probability')

        plt.savefig(save_path, transparent=False)

    def clean_log(self):
        with open(f"{self.dir_path}/output/AI-Model-log.txt", "w") as f:
            f.write("")

    def reset(self):
        self.train_data = pd.DataFrame()
        self.predict_data = pd.DataFrame()
        self.model = None
        self.drill_id = 0
        self.terminal = terminal
        self.file_path = os.path.abspath(__file__).replace("\\", "/")
        self.dir_path = "/".join(self.file_path.split("/")[:-1])
        self.clean_log()

    def write_log(self, message:str):
        now = datetime.now()
        date_str = f"{now.hour}:{now.minute}:{now.second}"
        with open(f"{self.dir_path}/output/AI-Model-log.txt", "a") as f:
            message = f"\n\n- log entry at {date_str}:: {message}"
            f.write(message)

