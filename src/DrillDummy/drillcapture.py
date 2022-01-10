import time
from datetime import datetime
import sys
import random
import os
from threading import Thread
import yaml

###############################################
###########    Drill Generator    #############
###############################################
# class for generate dummy-data
class Drill_Data_Generator(object):
    def __init__(self):
        self.data = []
        self.should_run = True

    def generate_num(self):
        return round((random.random()*(10+10))-10, 2)

    def run(self):
        while self.should_run:
            self.data += [(self.generate_num(), self.generate_num(), self.generate_num())]
            time.sleep(0.2)

    def stop(self):
        self.should_run = False

    def save_data(self, data_path, folder, operator, dir_name):
        # transform data in str
        txt = ""
        for data in self.data:
            for i, data_point in enumerate(data):
                txt += f"{data_point}"
                if i < len(data)-1:
                    txt += ","
            txt += "\n"

        # generate directory
        items = os.listdir(f"{data_path}/{folder}/{operator}")
        if dir_name in items:
            shutil.rmtree(f"{data_path}/{folder}/{operator}/{dir_name}")
        os.mkdir(f"{data_path}/{folder}/{operator}/{dir_name}")

        with open(f"{data_path}/{folder}/{operator}/{dir_name}/capture.csv", "w") as f:
            f.write(txt)


###############################################
#########    Dummy Drill Capture    ###########
###############################################
now = datetime.now()

# load datapath with call argument
if len(sys.argv) == 3 and sys.argv[1].startswith("-mode=") and sys.argv[2].startswith("-description="):
    #print(">>>>>>>>>>>>>>>>>>>>>>>> MOINNSCHEN")
    mode = sys.argv[1].split("=")[1]
    description = sys.argv[2].split("=")[1]
elif len(sys.argv) == 1:
    #print(">>>>>>>>>>>>>>>>>>>>>>>> BÖÖÖSE")
    mode = "bulk"
    description = f"{now.year}-{now.month}-{now.day}.yaml"
else:
    print("ERROR OCCUR BY LOADING")
    mode = "NONE"

if mode == 'bulk':
    yaml_path = description
    file_path = os.path.abspath(__file__).replace("\\", "/")
    #data_path = f"{'/'.join(file_path.split('/')[:-1])}/testdata"    # don't works in program, but why?
    data_path = 'D:/Karriere/Studium/3. Semester/Module/Projekt_1/wer/src/DrillDummy/testdata'
    #data_path = "/home/mustermann/rec/thema1"


    # old:
    #if len(sys.argv) >= 2:
    #    data_path = sys.argv[1]
    #else:
    #    #data_path = "C:/Users/tobia/Karriere/Studium/3. Semester/Module/Projekt_1/data/testdata"
    #    data_path = "D:/Karriere/Studium/3. Semester/Module/Projekt_1/wer/data/testdata"

    # load Metadata
    folder = f"{now.year}-{now.month}-{now.day}"
    with open(f"{data_path}/{folder}/{yaml_path}", "r") as file:
        content = file.read()

    metadata = yaml.safe_load(content)['configurations']

    # get all drills as list
    drills = []
    for person_data in metadata:
        amount = person_data['amount']
        name = person_data['template'].split("/")[0]
        drills += [name]*amount

    # --- FIXME ---
    if len(drills) == 0:
        print("No amounts!")
        sys.exit()
    # --- FIXME ---

    # choose one operator/drill
    choice = random.choice(drills)

    # call operator and take input to start
    user_input = input(f"{choice} have to drill as next one. Press Enter to start:")

    # start drilling with dummy-data in Thread
    data_generator = Drill_Data_Generator()
    thread = Thread(target=data_generator.run)
    thread.start()

    # get Enter input and then stop generate dummy-data
    user_input =  input("\nEnter:")
    data_generator.stop()
    thread.join()

    now = datetime.now()
    dir_name = f"{now.year}_{now.month}_{now.day}_{now.hour}-{now.minute}-{now.second}"
    data_generator.save_data(data_path, folder, choice, dir_name)

    # reduce amount
    new_metadata = yaml.safe_load(content)
    new_configurations = new_metadata['configurations']

        # Funktioniert das Ändern, oder wird es nur lokal geändert?
    for person_data in new_configurations:
        amount = person_data['amount']
        name = person_data['template'].split("/")[0]
        if name == choice:
            person_data['amount'] = amount-1

        # save new metadata
    yaml_file = yaml.dump(new_metadata)
    with open(f"{data_path}/{folder}/{yaml_path}", "w") as file:
        file.write(yaml_file)

    # -finfish-
elif mode == 'single':
    person_folder = description.split("/")[0]
    file_path = os.path.abspath(__file__).replace("\\", "/")
    #data_path = f"{'/'.join(file_path.split('/')[:-1])}/testdata"    # don't works in program, but why?
    data_path = 'D:/Karriere/Studium/3. Semester/Module/Projekt_1/wer/src/DrillDummy/testdata'

    folder = f"{now.year}-{now.month}-{now.day}"

    # No wait of Enter for starting

    # start drilling with dummy-data in Thread
    data_generator = Drill_Data_Generator()
    thread = Thread(target=data_generator.run)
    thread.start()

    # get Enter input and then stop generate dummy-data
    user_input =  input("\nEnter:")
    data_generator.stop()
    thread.join()

    now = datetime.now()
    dir_name = f"{now.year}_{now.month}_{now.day}_{now.hour}-{now.minute}-{now.second}"
    data_generator.save_data(data_path, folder, person_folder, dir_name)

    # -finfish-
