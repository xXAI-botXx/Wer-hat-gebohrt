import sys
import os
import random
import shutil
import time
from enum import Enum
from queue import Queue, Empty
from threading import Thread
import threading
from datetime import datetime

from .py_exe_interface import Drillcapture_Interface, Drilldriver_Interface, op
from .ai_model import AI_Model, ALGORITHM
from .event import Eventsystem_Component

process_state = Enum('process_state', 'NOT_STARTED BEFORE_TRAIN TRAIN TRAIN_END PREDICT')

class Terminal(Eventsystem_Component):
    """
    The Terminal class takes care of the logic of the live-application (who-drills).
    It creates the folders and files, controlls the subprocess (drillcapture and drilldriver),
    owns the data and AI-Model and counts the amounts of drilling.

    This class sends Event-Messages to the GUI and the SubprocessInterface.

    It runs with the run-Method and should run in a Thread.
    (Normally this is the startpoint of the program, but Tkinter has to run in the real program thread, so the GUI is the startpoint)
    
    Arguments:
        - User-Interface for sending events (for example: show next drill-person)
        - data-path as str (to know, where to save the data)
        - drillcapture_path as str (for starting the program)
        - drilldriver_path (for starting the program)
        - op as Operationsystem (Enum) (for knowing the operating system)
    """
    def __init__(self, user_interface, data_path="data/testdata", drillcapture_path="../BACKUP/drill-soft.exe", 
                                drilldriver_path="../BACKUP/drill-soft.exe", op=op.WINDOWS):
        Eventsystem_Component.__init__(self)
        self.data_path = data_path
        self.drilldriver_path = drilldriver_path
        self.drillcapture_path = drillcapture_path
        self.drilldriver = None
        self.drillcapture = None
        self.op = op
        file_path = os.path.abspath(__file__).split('\\')
        if self.op == op.WINDOWS:
            self.path_to_output = f"{'/'.join(file_path[:-1])}/output"
        else:
            self.path_to_output = f"/home/anoog/git/wer/src/anoog/automation/output"

        self.persons = (None, None)
        self.has_at_least_one_run = False
        self.last_drill_person = None
        self.cur_drill_person = None
        self.state = process_state.NOT_STARTED
        self.person1_info = None
        self.person2_info = None
        self.is_delete_last_possible = False

        self.model = AI_Model()
        self.predict_amount = 0
        self.can_delete_last_predict_data = False

        self.should_running = True
        self.events = Queue()
        self.EVENT = {'train-drill':self.init_train_drilling,
                        'reset-train':self.reset_train,
                        'exit':self.exit, 'delete-last':self.delete_last,
                        'start':self.start, 'stop':self.stop, 
                        'init-predict':self.init_predict,
                        'add-amount':self.add_amount, 'predict-load':self.load_predict,
                        'from-predict-to-train':self.from_predict_to_train, 'delete-last-predict-drill':self.delete_last_predict_drill,
                        'reset-predict':self.reset_predict, 'predict':self.predict}

        self.user_interface = user_interface
        now = datetime.now()
        self.date_str = f"{now.year}-{now.month}-{now.day}"

        # start mcc
        self.start_drill_driver()

    def run(self):
        """
        First cleans the Output-Files of the drillcapture file.

        Then check it event-queue for new events and process it, if there is one.
        There is a short waiting buffer.

        --------
        Returns None
        """
        self.clean_output()
        while self.should_running:
            self.run_event()
            threading.Event().wait(0.2)

    def reset_train(self):
        """
        Sets all variables with train-context to the init values.
        Not includes the predict-data (for purpose).

        --------
        Returns None
        """
        if self.drillcapture != None:
            self.drillcapture.add_event('exit')
            self.drillcapture = None
        self.persons = (None, None)
        self.last_drill_person = None

        self.persons = (None, None)
        self.has_at_least_one_run = False
        self.last_drill_person = None
        self.cur_drill_person = None
        self.state = process_state.NOT_STARTED
        if self.person1_info != None and self.person2_info != None:
            self.person1_info = self.person1_info.clear()
            self.person2_info = self.person2_info.clear()

        self.clean_output()

        self.model = AI_Model()
        self.predict_amount = 0
        self.can_delete_last_predict_data = False

    def reset_predict(self):
        """
        Sets all variables with predict-context to the init values.
        Not includes the train-data (for purpose).

        --------
        Returns None
        """
        self.model.remove_predict_dataset()
        self.predict_amount = 0
        self.can_delete_last_predict_data = False

    def from_predict_to_train(self):
        """
        Sets the state, if user goes from predict-screen back to train-screen

        --------
        Returns None
        """
        self.state = process_state.TRAIN_END

    def start_drill_driver(self):
        """
        Starts the Drilldriver-Program.

        Should be started one time by the start of the live-application.

        --------
        Returns None
        """
        if self.drilldriver != None:
            raise ValueError("Drilldriver startet twice. Look at controller 123")
            self.stop_drill_driver()
        self.drilldriver = Drilldriver_Interface(self.drilldriver_path, self, self.op)
        self.thread_process_1 = Thread(target=self.drilldriver.run)
        self.thread_process_1.start()

    def stop_drill_driver(self):
        """
        Stops the Drilldriver-Program by sending a exit-event.

        --------
        Returns None
        """
        if self.drilldriver != None:
            self.drilldriver.add_event('exit')
            self.drilldriver = None

    def init_drill(self, person1:dict, person2:dict):
        """
        Creates the Directories and yaml-Files for UNKNOWN and the two persons.

        The yaml-Files contains basic information about the person who drills. 
        This will be  partly used as label, for the training of the supervised classification models.  
        
        Arguments:
            - 2 Dictionaries which incudes informations about the persons (str:str)
                -> Following entries are needed: 
                        - 'material' 
                        - 'boreholeSize'
                        - 'gear'
                        - 'batteryLevel'
                        - 'drillType'
                        - 'operator'
                        - 'amount'
        --------
        Returns None
        """
        now = datetime.now()
        date_str = f"{now.year}-{now.month}-{now.day}"
        # Create 1 Directory -> Date -> if still there -> delete
        items = os.listdir(self.data_path)
        if date_str in items:
            shutil.rmtree(f"{self.data_path}/{date_str}")
            #os.rmdir(f"{self.data_path}/{date_str}")
        os.mkdir(f"{self.data_path}/{date_str}")
    
        # make persons driectories
        os.mkdir(f"{self.data_path}/{date_str}/{person1['operator']}")
        os.mkdir(f"{self.data_path}/{date_str}/{person2['operator']}")
        # Predict-Data-Folder
        os.mkdir(f"{self.data_path}/{date_str}/UNKNOWN")

        # Create in each of these new dirs a yaml file with basic infos
        for person in [person1, person2]:
            yaml_content = ""
            basic_infos = ['boreholeSize', 'material', 'gear', 'batteryLevel', 'drillType', 'operator']
            for i in basic_infos:
                yaml_content += f"{i}: {person[i]}\n"
            yaml_content += f"anomalyTimestamps:\n- idle"

            with open(f"{self.data_path}/{date_str}/{person['operator']}/meta.yaml", "w")as f:
                f.write(yaml_content)

        # Create Dummy Meta File for UNKNOWN -> Prediction
        unknown_meta_data = "boreholeSize: 4\nmaterial: wood-eiche\ngear: 2\nbatteryLevel: normal\n"
        unknown_meta_data += "drillType: universal\noperator: UNKNOWN\nanomalyTimestamps:\n- idle"

        with open(f"{self.data_path}/{date_str}/UNKNOWN/meta.yaml", "w")as f:
            f.write(unknown_meta_data)

        self.state = process_state.BEFORE_TRAIN

    def init_predict(self, person1:dict, person2:dict):
        """
        Creates the Directories and yaml-Files for UNKNOWN with dummy-informations.
        
        Arguments:
            - 2 Dictionaries which incudes informations about the persons (str:str)
                -> Following entries are needed: 
                        - 'material' 
                        - 'boreholeSize'
                        - 'gear'
                        - 'batteryLevel'
                        - 'drillType'
                        - 'operator'
                        - 'amount'
        --------
        Returns None
        """
        now = datetime.now()
        date_str = f"{now.year}-{now.month}-{now.day}"
        # Create 1 Directory -> Date -> if still there -> delete
        items = os.listdir(f"{self.data_path}/{date_str}")
        if "unknown" in items:
            shutil.rmtree(f"{self.data_path}/{date_str}/unknown")
        os.mkdir(f"{self.data_path}/{date_str}/unknown")

        # Metadaten mit ungültigen Daten füllen
        yaml_content = ""
        basic_infos = ['boreholeSize', 'material', 'gear', 'batteryLevel', 'drillType', 'operator']
        for i in basic_infos:
            yaml_content += f"{i}: -999\n"
        yaml_content += f"anomalyTimestamps:\n- idle"

        with open(f"{self.data_path}/{date_str}/UNKNOWN/meta.yaml", "w")as f:
            f.write(yaml_content)

    def delete_last(self):
        """
        Removes last train-data-entry in DataFrame and the real data (folder).
        Moreover the Amount is resetting by 1.

        --------
        Returns None
        """
        if self.last_drill_person != None and (self.state == process_state.BEFORE_TRAIN or self.state == process_state.TRAIN_END) and self.is_delete_last_possible:
            # delete Folder
            now = datetime.now()
            date_str = f"{now.year}-{now.month}-{now.day}"
            items = os.listdir(f"{self.data_path}/{date_str}/{self.last_drill_person}")
            items.sort()
            i = -1
            latest_drill = items[-1]
            while os.path.isfile(f"{self.data_path}/{date_str}/{self.last_drill_person}/{latest_drill}"):
                if i*-1 > len(items):
                    return None
                i -= 1
                latest_drill = items[i]
            shutil.rmtree(f"{self.data_path}/{date_str}/{self.last_drill_person}/{latest_drill}")
        
            # update digital amount
            if self.last_drill_person == self.person1_info['operator']:
                self.person1_info['amount'] = str(int(self.person1_info['amount']) + 1)
            else:
                self.person2_info['amount'] = str(int(self.person2_info['amount']) + 1)

            self.user_interface.add_event('drill-amount-change', (self.person1_info['amount'], self.person2_info['amount']))

            # update model
            self.model.remove_last_train_dataset()

            # Restart the drillcapture
            if self.drillcapture != None:
                self.drillcapture.add_event('exit')
            self.init_train_drilling(self.person1_info, self.person2_info)

            # block new delete_last actions
            self.is_delete_last_possible = False
            self.user_interface.add_event('delete-last', ('disabled', ))
            self.user_interface.add_event('start-change', ('enabled', ))

    def delete_last_predict_drill(self):
        """
        Removes last predict-data-entry in DataFrame and the real data (folder).
        Moreover the Predict-Amount is decreased by 1.

        --------
        Returns None
        """
        if self.state == process_state.PREDICT and self.can_delete_last_predict_data:
            # update ai-model / dataframe
            self.model.remove_last_predict_dataset()
            # Update digital amount
            self.predict_amount -= 1
            self.can_delete_last_predict_data = False
            # Update GUI
            self.user_interface.add_event('delete-last-predict', ('disabled', ))
            self.user_interface.add_event('set-amount-predict', (self.predict_amount, ))

    def init_train_drilling(self, person1:dict, person2:dict):
        """
        Prepares the Application for a new train-drill.
        Choose a person for drilling. If both have amount left, pseudo-random will choose a person.

        Arguments:
            - 2 Dictionaries which incudes informations about the persons (str:str)
                -> Following entries are needed: 
                        - 'material' 
                        - 'boreholeSize'
                        - 'gear'
                        - 'batteryLevel'
                        - 'drillType'
                        - 'operator'
                        - 'amount'

        --------
        Returns None
        """
        if self.state == process_state.NOT_STARTED or not self.has_at_least_one_run:
            if self.drillcapture != None:
                self.drillcapture.add_event('exit')
                threading.Event().wait(0.2)
            self.init_drill(person1, person2)

        self.person1_info = person1
        self.person2_info = person2
        self.persons = (person1['operator'], person2['operator'])
        self.state = process_state.BEFORE_TRAIN

        # choose random person
        if int(person1['amount']) <= 0 and int(person2['amount']) > 0:
            self.user_interface.add_event('drill-person', (self.persons[1], ))
            self.cur_drill_person = self.persons[1]
        elif int(person2['amount']) <= 0 and int(person1['amount']) > 0:
            self.user_interface.add_event('drill-person', (self.persons[0], ))
            self.cur_drill_person = self.persons[0]
        elif int(person1['amount']) <= 0 and int(person2['amount']) <= 0:
            self.user_interface.add_event('drill-person', ('Keine Bohrung mehr!', ))
            self.cur_drill_person = None
        else:
            if random.randint(0, 1) == 0:
                self.user_interface.add_event('drill-person', (self.persons[0], ))
                self.cur_drill_person = self.persons[0]
            else:
                self.user_interface.add_event('drill-person', (self.persons[1], ))
                self.cur_drill_person = self.persons[1]

    def start(self):
        """
        Starts a drill (train or predict) with Drillcapture in single-mode.

        --------
        Return None
        """
        if self.state == process_state.BEFORE_TRAIN:
            self.has_at_least_one_run = True
            self.user_interface.add_event('delete-last', ('disabled', ))
            self.user_interface.add_event('drill-starts')
            self.drillcapture = Drillcapture_Interface(self.drillcapture_path, self.path_to_output, self, self.op, self.cur_drill_person)
            self.thread_process_2 = Thread(target=lambda: self.drillcapture.run("single"))
            self.thread_process_2.start()
            self.state = process_state.TRAIN
        elif self.state == process_state.PREDICT:
            if self.drillcapture != None:
                self.drillcapture.add_event('exit')
            
            self.drillcapture = Drillcapture_Interface(self.drillcapture_path, self.path_to_output, self, self.op, "UNKNOWN")
            self.thread_process_2 = Thread(target=lambda: self.drillcapture.run("single"))
            self.thread_process_2.start()
            self.user_interface.add_event('predict-drill-starts')

    def stop(self):
        """
        Stops a drill (train or predict). Will check by train, if there is amount left and if not, it activates the predict area.
        Prepares next drill, if there is amount left.

        --------
        Returns None
        """
        if self.state == process_state.TRAIN:
            self.drillcapture.add_event('input', ('from_stop',))
            self.user_interface.add_event('delete-last', ('enabled', ))
            self.user_interface.add_event('stop-time')
            self.last_drill_person = self.cur_drill_person
            self.drillcapture.add_event('exit')
            self.drillcapture = None
            threading.Event().wait(0.5)
            # Update amount
            if self.last_drill_person == self.person1_info['operator']:
                self.person1_info['amount'] = str(int(self.person1_info['amount']) - 1)
                self.model.add_train_dataset(0, self.person1_info['operator'], self.data_path)
            else:
                self.person2_info['amount'] = str(int(self.person2_info['amount']) - 1)
                self.model.add_train_dataset(1, self.person2_info['operator'], self.data_path)

            if self.person1_info['amount'] == '0' and self.person2_info['amount'] == '0':
                self.state = process_state.TRAIN_END
                self.user_interface.add_event('drill-person', ("Keine Bohrungen mehr!", ))
                self.user_interface.add_event('drill-ends', (0, 0))
            else:
                self.init_train_drilling(self.person1_info, self.person2_info)
                self.state = process_state.BEFORE_TRAIN
                self.user_interface.add_event('drill-ends', (self.person1_info['amount'], self.person2_info['amount']))

            self.is_delete_last_possible = True
        elif self.state == process_state.PREDICT:
            self.drillcapture.add_event('input', ('from_stop',))
            self.user_interface.add_event('stop-time')
            self.drillcapture.add_event('exit')
            self.drillcapture = None
            threading.Event().wait(0.5)
            self.model.add_predict_dataset(2, "UNKNOWN", self.data_path)
            self.predict_amount += 1
            self.can_delete_last_predict_data = True
            self.user_interface.add_event('set-amount-predict', (self.predict_amount, ))
            self.user_interface.add_event('delete-last-predict', ('enabled', ))
            self.user_interface.add_event('predict-drill-ends')

    def add_amount(self, amount_person_1:str, amount_person_2:str):
        """
        Increased Amount by 1. Prepares for new train-drill, if amounts over 0.

        --------
        Returns None
        """
        # transfer to int
        try:
            amount_person_1 = int(amount_person_1)
            amount_person_2 = int(amount_person_2)
        except ValueError:
            # break
            return None

        # digital update
        self.person1_info['amount'] = str(int(self.person1_info['amount']) + amount_person_1)
        self.person2_info['amount'] = str(int(self.person2_info['amount']) + amount_person_2)

        if self.person1_info['amount'] != '0' or self.person2_info['amount'] != '0':
            self.init_train_drilling(self.person1_info, self.person2_info)
            self.state = process_state.BEFORE_TRAIN

        # write in User-Interface
        self.user_interface.add_event('drill-amount-change', (self.person1_info['amount'], self.person2_info['amount']))

    def load_predict(self):
        """
        Change the internal state to predict. Important for some methods.

        --------
        Returns None
        """
        self.state = process_state.PREDICT

    def exit(self):
        """
        Stops the drilldriver and the drillcapture. Stable against None.

        --------
        Returns None
        """
        if self.drillcapture != None:
            self.drillcapture.add_event('exit')
            self.drillcapture = None

        if self.drilldriver != None:
            self.drilldriver.add_event('exit')
            self.drilldriver = None

        sys.exit()

    def predict(self, model:str, mode:str, normalize:str):
        """
        Train a given model with given parameters with the collected data.
        After that, the model will predict the predict-data (every entry).
        Get Soft Voting and update GUI with Results.

        Arguments:
            - model as str -> 'RandomForest', 'SVC', 'Naive Bayes', 'KNN', 'Ada Boost', 'Logistic Regression'
            - mode as str -> 'auto' or not (decided if predefined Hyperparameters or with GridSearchCV)
            - normalize as str -> 'normalize' or not (decided if the data should be normalize)
        -------
        Returns None
        """
        # train
        if normalize == 'normalize':
            normalize = True
        else:
            normalize = False

        if mode == 'auto':
            auto_params = True
        else:
            auto_params = False

        if model != None:
            if model.lower() == "svc":
                self.model.train(ALGORITHM.SVC, auto_params, normalize)
            elif model.lower() == "randomforest":
                self.model.train(ALGORITHM.RANDOM_FOREST, auto_params, normalize)
            elif model.lower() == "knn":
                self.model.train(ALGORITHM.KNN, auto_params, normalize)
            elif model.lower() == "naive bayes":
                self.model.train(ALGORITHM.NAIVE_BAYES, auto_params, normalize)
            elif model.lower() == "ada boost":
                self.model.train(ALGORITHM.ADA_BOOST, auto_params, normalize)
            elif model.lower() == "logistic regression":
                self.model.train(ALGORITHM.LOGISTIC_REGRESSION, auto_params, normalize)
            elif model.lower() == "voting classifier":
                self.model.train(ALGORITHM.VOTING_CLASSIFIER, auto_params, normalize)

        # predict
        person1_proba, person2_proba = self.model.predict()
        if person1_proba > person2_proba:
            self.user_interface.add_event('predict-result', (self.person1_info['operator'], person1_proba*100, model))
        else:
            self.user_interface.add_event('predict-result', (self.person2_info['operator'], person2_proba*100, model))

    def clean_output(self):
        """
        Clear Output Files of Subprocess. 
        
        Should be called by start of the application.
        """
        with open(f"{self.path_to_output}/stdout.txt","w") as out:
            out.write("")

        with open(f"{self.path_to_output}/stderr.txt","w") as out:
            out.write("")

        with open(f"{self.path_to_output}/stdin.txt","w") as out:
            out.write("")


