import sys
import os
import shutil
import time
from enum import Enum
from queue import Queue, Empty
from threading import Thread
import threading
from datetime import datetime

from .py_exe_interface import Drillcapture_Interface, Drilldriver_Interface, op
from .ai_model import AI_Model, ALGORITHM

# all uppercase variables are globals
# was passiert, wenn man nochmal importiert, werden die gloabls wieder auf standart zurüclgestzt?

process_state = Enum('process_state', 'NOT_STARTED BEFORE_TRAIN TRAIN TRAIN_END PREDICT')

class Terminal(object):
    def __init__(self, user_interface, data_path="data/testdata", drillcapture_path="../BACKUP/drill-soft.exe", 
                                drilldriver_path="../BACKUP/drill-soft.exe", op=op.WINDOWS):
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
            # FIXME
            self.path_to_output = f"/home/mustermann/Projekt1/src/anoog/automation/output"
            #self.path_to_output = f"~/Projekt1/src/anoog/automation/output"
            #self.path_to_output = f"./output"

        self.persons = (None, None)
        self.has_at_least_one_run = False
        self.last_drill_person = None
        self.cur_drill_person = None
        self.visited_out = False
        self.state = process_state.NOT_STARTED
        self.person1_info = None
        self.person2_info = None
        self.is_delete_last_possible = False

        self.model = AI_Model(self)
        self.ai_thread = None    # currently not used
        self.predict_amount = 0
        self.can_delete_last_predict_data = False

        self.should_running = True
        self.events = Queue()
        self.EVENT = {'train-drill':self.init_train_drilling,
                        'start-drilldriver':self.start_drill_driver, 'reset-train':self.reset_train,
                        'exit':self.exit, 'delete-last':self.delete_last,
                        'start':self.start, 'stop':self.stop, 
                        'init-predict':self.init_predict, 'wrote-input':self.wrote_input,
                        'add-amount':self.add_amount, 'predict-load':self.load_predict,
                        'from-predict-to-train':self.from_predict_to_train, 'delete-last-predict-drill':self.delete_last_predict_drill,
                        'reset-predict':self.reset_predict, 'predict':self.predict}

        self.user_interface = user_interface
        now = datetime.now()
        self.date_str = f"{now.year}-{now.month}-{now.day}"

    def run(self):
        self.clean_output()
        while self.should_running:
            # check output
            self.check_output()
            #print("terminal works...")

            # event queue
            if not self.events.empty():
                event = self.events.get()
                if len(event) > 1:
                    self.EVENT[event[0]](*event[1])
                else:
                    self.EVENT[event[0]]()

            threading.Event().wait(0.2)

    def reset_train(self):
        if self.drillcapture != None:
            self.drillcapture.add_event('exit')
            self.drillcapture = None
        self.persons = (None, None)
        self.last_drill_person = None

        if self.drilldriver != None:
            self.drilldriver.add_event('exit')
            self.drilldriver = None

        self.persons = (None, None)
        self.has_at_least_one_run = False
        self.last_drill_person = None
        self.cur_drill_person = None
        self.visited_lines_in_output = 0
        self.state = process_state.NOT_STARTED
        if self.person1_info != None and self.person2_info != None:
            self.person1_info = self.person1_info.clear()
            self.person2_info = self.person2_info.clear()

        self.visited_out = False
        self.clean_output()

        self.model = AI_Model(self)
        self.ai_thread = None    # currently not used
        self.predict_amount = 0
        self.can_delete_last_predict_data = False
        # reset dir and entry-contents? -> or let them exist

    def reset_predict(self):
        self.model.remove_predict_dataset()
        self.ai_thread = None    # currently not used
        self.predict_amount = 0
        self.can_delete_last_predict_data = False

    def from_predict_to_train(self):
        self.state = process_state.TRAIN_END

    def start_drill_driver(self):
        if self.drilldriver != None:
            self.stop_drill_driver()
        self.drilldriver = Drilldriver_Interface(self.drilldriver_path, self)
        self.thread_process_1 = Thread(target=self.drilldriver.run)
        self.thread_process_1.start()

    def stop_drill_driver(self):
        if self.drilldriver != None:
            self.drilldriver.add_event('exit')
            self.drilldriver = None

    def init_drill(self, person1:dict, person2:dict):
        """Creates all Directories and yaml-Files"""
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

        # Create a ground yaml-File -> persons and amounts
        yaml_content = "configurations:\n"
        yaml_content += f"- amount: {person1['amount']}\n"
        yaml_content += f"  template: {person1['operator']}/meta.yaml\n"
        yaml_content += f"- amount: {person2['amount']}\n"
        yaml_content += f"  template: {person2['operator']}/meta.yaml"

        with open(f"{self.data_path}/{date_str}/{date_str}.yaml", "w")as f:
            f.write(yaml_content)

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
        """Creates all Directories and yaml-Files"""
        now = datetime.now()
        date_str = f"{now.year}-{now.month}-{now.day}"
        # Create 1 Directory -> Date -> if still there -> delete
        items = os.listdir(f"{self.data_path}/{date_str}")
        if "unknown" in items:
            shutil.rmtree(f"{self.data_path}/{date_str}/unknown")
            #os.rmdir(f"{self.data_path}/{date_str}")
        os.mkdir(f"{self.data_path}/{date_str}/unknown")

        # Metadaten mit ungültigen Daten füllen
        yaml_content = ""
        basic_infos = ['boreholeSize', 'material', 'gear', 'batteryLevel', 'drillType', 'operator']
        for i in basic_infos:
            yaml_content += f"{i}: -999\n"
        yaml_content += f"anomalyTimestamps:\n- idle"

        with open(f"{self.data_path}/{date_str}/{person['operator']}/meta.yaml", "w")as f:
            f.write(yaml_content)

    def delete_last(self):
        if self.last_drill_person != None and (self.state == process_state.BEFORE_TRAIN or self.state == process_state.TRAIN_END) and self.is_delete_last_possible:
            # delte Folder
            now = datetime.now()
            date_str = f"{now.year}-{now.month}-{now.day}"
            # Create 1 Directory -> Date -> if still there -> delete
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
        
            # increase amount of person
            # get info
            with open(f"{self.data_path}/{date_str}/{date_str}.yaml", "r") as f:
                info = f.read()

            amount = None
            new_info = "configurations:"
            for entry in info.split("-")[1:]:
                if self.last_drill_person in entry:
                    amount = int(entry.split("\n")[0].split(":")[1])
                    amount += 1
                    new_info += f"\n- amount: {amount}\n  template: {self.last_drill_person}/meta.yaml"
                    continue
                new_info += "\n-"+entry
            
            with open(f"{self.data_path}/{date_str}/{date_str}.yaml", "w") as f:
                    f.write(new_info)

            print(f"\nBefore Deleting Amount Person 1: {self.person1_info['amount']} - Amount Person 2: {self.person2_info['amount']}")
            # update digital amount
            if self.last_drill_person == self.person1_info['operator']:
                self.person1_info['amount'] = str(int(self.person1_info['amount']) + 1)
            else:
                self.person2_info['amount'] = str(int(self.person2_info['amount']) + 1)

            print(f"After deleting Amount Person 1: {self.person1_info['amount']} - Amount Person 2: {self.person2_info['amount']}")

            self.user_interface.add_event('drill-amount-change', self.person1_info['amount'], self.person2_info['amount'])

            # update model
            self.model.remove_last_train_dataset()

            # Restart the drillcapture
            if self.drillcapture != None:
                self.drillcapture.add_event('exit')
            if self.state == process_state.TRAIN_END:
                self.user_interface.add_event('start-change', 'enabled')
            self.visited_out = False
            self.init_train_drilling(self.person1_info, self.person2_info)

            # block new delete_last actions
            self.is_delete_last_possible = False
            self.user_interface.add_event('delete-last', ('disabled', ))
        elif self.state == process_state.PREDICT and self.can_delete_last_predict_data:
            self.can_delete_last_predict_data = False
            self.predict_amount += 1
            self.model.remove_last_predict_dataset()
            self.user_interface.add_event('set-amount-predict', self.predict_amount)
            self.user_interface.add_event('delete-last', ('disabled', ))

    def delete_last_predict_drill(self):
        self.model.remove_last_predict_dataset()
        self.user_interface.add_event('delete-last-predict', ('disabled', ))
        self.predict_amount -= 1
        self.can_delete_last_predict_data = False
        self.user_interface.add_event('set-amount-predict', self.predict_amount)

    def init_train_drilling(self, person1:dict, person2:dict):
        if self.state == process_state.NOT_STARTED or not self.has_at_least_one_run:
            if self.drillcapture != None:
                self.drillcapture.add_event('exit')
                threading.Event().wait(0.2)
                self.visited_out = False
            self.init_drill(person1, person2)
        self.drillcapture = Drillcapture_Interface(self.drillcapture_path, self.path_to_output, self, self.op)
        self.thread_process_2 = Thread(target=lambda: self.drillcapture.run("bulk"))
        self.thread_process_2.start()

        self.person1_info = person1
        #print(f"{id(self.person1_info) == id(person1)}")
        self.person2_info = person2
        self.persons = (person1['operator'], person2['operator'])
        self.state = process_state.BEFORE_TRAIN

    def start(self):
        if self.state == process_state.BEFORE_TRAIN:
            self.has_at_least_one_run = True
            self.user_interface.add_event('delete-last', ('disabled', ))
            self.user_interface.add_event('drill-starts')
            self.drillcapture.add_event('input', ('from_start',))
            self.state = process_state.TRAIN
        elif self.state == process_state.PREDICT:
            if self.drillcapture != None:
                self.drillcapture.add_event('exit')
            
            self.drillcapture = Drillcapture_Interface(self.drillcapture_path, self.path_to_output, self, self.op)
            self.thread_process_2 = Thread(target=lambda: self.drillcapture.run("single"))
            self.thread_process_2.start()
            self.user_interface.add_event('predict-drill-starts')

    def stop(self):
        if self.state == process_state.TRAIN:
            self.drillcapture.add_event('input', ('from_stop',))
            self.user_interface.add_event('delete-last', ('enabled', ))
            self.user_interface.add_event('stop-time')
            self.last_drill_person = self.cur_drill_person
            self.drillcapture.add_event('exit')
            self.drillcapture = None
            threading.Event().wait(0.5)
            if self.last_drill_person == self.person1_info['operator']:
                self.person1_info['amount'] = str(int(self.person1_info['amount']) - 1)
                self.model.add_train_dataset(0, self.person1_info['operator'], self.data_path)
            else:
                self.person2_info['amount'] = str(int(self.person2_info['amount']) - 1)
                self.model.add_train_dataset(1, self.person2_info['operator'], self.data_path)

            if self.amount_at_the_end() or (self.person1_info['amount'] == '0' and self.person2_info['amount'] == '0'):
                self.state = process_state.TRAIN_END
                #self.stop_drill_driver()
                self.user_interface.add_event('drill-person', ("Keine Bohrungen mehr!", ))
                self.user_interface.add_event('drill-ends', 0, 0)
            else:
                self.init_train_drilling(self.person1_info, self.person2_info)
                self.state = process_state.BEFORE_TRAIN
                self.user_interface.add_event('drill-ends', self.person1_info['amount'], self.person2_info['amount'])

            self.is_delete_last_possible = True
        elif self.state == process_state.PREDICT:
            self.drillcapture.add_event('input', ('from_stop',))
            self.user_interface.add_event('stop-time')
            #self.user_interface.add_event('predict-delete-last', ('enabled', ))
            self.drillcapture.add_event('exit')
            self.drillcapture = None
            threading.Event().wait(0.5)
            self.model.add_predict_dataset(2, "UNKNOWN", self.data_path)
            self.predict_amount += 1
            self.can_delete_last_predict_data = True
            self.user_interface.add_event('set-amount-predict', self.predict_amount)
            self.user_interface.add_event('delete-last-predict', ('enabled', ))
            self.user_interface.add_event('predict-drill-ends')

    def amount_at_the_end(self) -> bool:
        # noch Bohrgänge übrig?
        with open(f"{self.data_path}/{self.date_str}/{self.date_str}.yaml", "r") as f:
                info = f.read()

        amount_is_there = True
        for line in info.split("\n"):
            if "amount" in line:
                amount = int(line.split(":")[1])
                if amount > 0:
                    amount_is_there = False
                    break
        return amount_is_there 

    def add_amount(self, amount_person_1:str, amount_person_2:str):
        now = datetime.now()
        date_str = f"{now.year}-{now.month}-{now.day}"
        # Check State?

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

        # file update
        with open(f"{self.data_path}/{date_str}/{date_str}.yaml", "r") as f:
            info = f.read()

        amount = None
        new_info = "configurations:"
        for entry in info.split("-")[1:]:
            if self.person1_info['operator'] in entry:
                amount = int(entry.split("\n")[0].split(":")[1])
                amount += amount_person_1
                new_info += f"\n- amount: {amount}\n  template: {self.person1_info['operator']}/meta.yaml"
                continue
            elif self.person2_info['operator'] in entry:
                amount = int(entry.split("\n")[0].split(":")[1])
                amount += amount_person_2
                new_info += f"\n- amount: {amount}\n  template: {self.person2_info['operator']}/meta.yaml"
                continue
            # Should not be reached
            new_info += "\n- "+entry
        
        with open(f"{self.data_path}/{date_str}/{date_str}.yaml", "w") as f:
                f.write(new_info)

        if self.person1_info['amount'] != '0' or self.person2_info['amount'] != '0':
            self.visited_out = False
            self.init_train_drilling(self.person1_info, self.person2_info)
            self.state = process_state.BEFORE_TRAIN

        # write in User-Interface
        self.user_interface.add_event('drill-amount-change', self.person1_info['amount'], self.person2_info['amount'])

    def load_predict(self):
        #self.model.train(algorithm=ALGORITHM.SVC, auto_params=False)
        self.state = process_state.PREDICT

    def exit(self):
        if self.drillcapture != None:
            self.drillcapture.add_event('exit')
            self.drillcapture = None

        if self.drilldriver != None:
            self.drilldriver.add_event('exit')
            self.drilldriver = None

        sys.exit()

    def predict(self, model:str, mode:str, normalize:str):
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

        # predict
        person1_proba, person2_proba = self.model.predict()
        if person1_proba > person2_proba:
            self.user_interface.add_event('predict-result', self.person1_info['operator'], person1_proba*100, model)
        else:
            self.user_interface.add_event('predict-result', self.person2_info['operator'], person2_proba*100, model)

        # Matplotlib zeichnen lassen + GUI bescheid geben
        #file_path = os.path.abspath(__file__).replace("\\", "/")
        #dir_path = "/".join(file_path.split("/")[:-1])
        #self.model.draw_result(self.person1_info['operator'], person1_proba, self.person2_info['operator'], person2_proba, f"{dir_path}/img/result.png")
        #self.user_interface.add_event('draw-result', f"{dir_path}/img/result.png")

    def add_event(self, event_name, *additions):
        print("added event:", event_name)
        event = (event_name, *additions)
        self.events.put(event)

    def to_process(self, message):
        with open(f"{path}/output/stdin.txt","wb") as f:
            f.write(message)

    # new version:
    def check_output(self):
        if self.persons[0] != None and self.persons[1] != None:
            if not self.visited_out:
                output = ""
                # path = "/".join(__file__.split("\\")[:-1])
                # f"{path}/output/stdout.txt"
                with open(f"{self.path_to_output}/stdout.txt","r") as out:
                    output = out.read()

                
                #print(self.visited_lines_in_output)

                #print("Full Output: \n",output)
                print("Output:", output)
                if self.state == process_state.BEFORE_TRAIN:
                    if self.persons[0] in output:
                        self.user_interface.add_event('drill-person', (self.persons[0], ))
                        self.cur_drill_person = self.persons[0]
                    elif self.persons[1] in output:
                        self.user_interface.add_event('drill-person', (self.persons[1], ))
                        self.cur_drill_person = self.persons[1]

                if len(output) > 0:
                    self.visited_out = True

    def clean_output(self):
        with open(f"{self.path_to_output}/stdout.txt","w") as out:
            out.write("")

        with open(f"{self.path_to_output}/stderr.txt","w") as out:
            out.write("")

        with open(f"{self.path_to_output}/stdin.txt","w") as out:
            out.write("")

    def from_ui_to_process(self, message):
        self.user_interface.add_event('output', (message, ))

    def wrote_input(self):
        self.visited_out = False

    def block(self):
        self.user_interface.add_event('block', (True,))

    def unblock(self):
        self.user_interface.add_event('block', (False,))


