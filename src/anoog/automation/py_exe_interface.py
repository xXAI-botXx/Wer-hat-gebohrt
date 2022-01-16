import sys
import os
import time
from datetime import datetime
import psutil
import subprocess as subp
import threading
import abc

from enum import Enum
from queue import Queue

from .event import Eventsystem_Component

#from pexpect.popen_spawn import PopenSpawn

# Event = {str:(name, function), str:(name, function), ..} -> str ist die Output Bedingung und name ist das Event, welches dann ausgelöst werden soll
# Funktion wird bei auftreten von str mit Parameter name aufgerufen + Process mit mit übergeben

op = Enum('op', 'WINDOWS LINUX')

class Process_Interface(abc.ABC, Eventsystem_Component):
    #id = 0
    def __init__(self, absolut_path_to_exe:str, terminal, operating_system=op.WINDOWS):
        Eventsystem_Component.__init__(self)
        self.path_to_exe = absolut_path_to_exe
        self.terminal = terminal
        self.should_run = False
        self.operating_system = operating_system
        self.events = Queue()
        self.EVENT = {'input':self.write, 'exit':self.stop}

        #self.id = Process_Interface.id
        #print("Process_Interface created...", self.id)
        #Process_Interface.id += 1

    @abc.abstractclassmethod
    def start_program(self):
        pass

    #@abc.abstractclassmethod
    def run(self):
        self.should_run = True

        self.start_program()
        
        #os.system("start cmd /K dir")

        self.event_listener()


    def read(self):
        out = self.process.stdout.readline().decode().strip()
        self.save_in_file(out+"\n")
        return out

    def read_err(self):
        out = self.process.stderr.readline().decode().strip()
        self.save_in_file(out+"\n", "err_log.txt")
        return out

    def write(self, reaction:str):
        self.process.stdin.write(f"{reaction}\n".encode())
        try:
            self.process.stdin.flush()
        except OSError as e:
            pass

    # should run in thread, so that you can write input
    def event_listener(self):
        while self.should_run: #and self.is_alive():
            #print("Process_Interface on work...")
            self.run_event()

            threading.Event().wait(0.2)

    def check_input(self):
        input = ""
        path = "/".join(__file__.split("\\")[:-1])
        with open(f"{path}/output/stdin.txt","r") as f:
            input = f.read()

    # dont works!!!
    def is_alive(self) -> bool:
        if self.process.poll() == None:
            return True
        else:
            return False

    def process_status(self):
        pid = self.process.pid
        process_status = None
        try:
            process_status = psutil.Process(pid).status()
        except psutil.NoSuchProcess as no_proc_exc:
            pass
            #print(no_proc_exc)

        return process_status

    def stop(self, send_event=False) -> str:
        #if self.is_alive():
        self.should_run = False
        try:
            if self.process != None and self.process.stdin != None:
                self.process.stdin.close()
            #self.process.stdout.close()
            #self.process.stderr.close()
        except OSError:
            pass
        #self.process.wait(timeout=1)
        if self.process != None:
            self.process.terminate()

    
    def save_in_file(self, txt:str, file="log.txt"):
        path = "/".join(self.path_to_exe.split("/")[:-1])
        with open(path+"/"+file, "a") as f:
            f.write(txt)


class Drilldriver_Interface(Process_Interface):
    def __init__(self, absolut_path_to_exe:str, terminal, operating_system=op.WINDOWS):
        super().__init__(absolut_path_to_exe, terminal, operating_system)

    def start_program(self):
        if self.operating_system == op.WINDOWS:
            c = ["start", '/b', self.path_to_exe]
        else:
            c = [self.path_to_exe]

        self.process = subp.Popen(c,  shell=True)    #  stdin=subp.PIPE, stdout=subp.PIPE, stderr=subp.PIPE,


# adding arguments + predict mode
class Drillcapture_Interface(Process_Interface):
    def __init__(self, absolut_path_to_exe:str, path_to_output, terminal, operating_system=op.WINDOWS, name=None):
        super().__init__(absolut_path_to_exe, terminal, operating_system)
        self.path_to_output = path_to_output
        self.name = name

    # OVERRIDE
    def run(self, mode="bulk"):
        self.should_run = True
        self.start_program(mode)
        self.event_listener()

    def start_program(self, mode="bulk"):
        now = datetime.now()
        if mode == 'bulk':
            if self.operating_system == op.WINDOWS:
                c = ["start", '/b', self.path_to_exe, f"-mode=bulk", f"-description={now.year}-{now.month}-{now.day}.yaml"]
            else:
                #c = [self.path_to_exe, "-interface=cli", "-module=drill", f"-mode=bulk", f"-description={now.year}-{now.month}-{now.day}.yaml"]
                #print(__file__)
                c = [f"{self.path_to_exe} -interface=cli -module=drill -mode=bulk -description=/home/anoog/rec/thema1/{now.year}-{now.month}-{now.day}/{now.year}-{now.month}-{now.day}.yaml"]
                #print(c)
        elif mode == "single":
            if self.operating_system == op.WINDOWS:
                c = ["start", '/b', self.path_to_exe, f"-mode=single", f"-description={self.name}/meta.yaml"]
            else:
                #c = [self.path_to_exe, f"-mode=single", f"-description=UNKNOWN/meta.yaml"]
                c = [f"{self.path_to_exe} -interface=cli -module=drill -mode=single -description=/home/anoog/rec/thema1/{now.year}-{now.month}-{now.day}/{self.name}/meta.yaml"]

        #path = "/".join(__file__.split("\\")[:-1])
        with open(f"{self.path_to_output}/stdout.txt","wb") as out, open(f"{self.path_to_output}/stderr.txt","wb") as err:
            self.process = subp.Popen(c, stdin=subp.PIPE, stdout=out, stderr=err,    
                                        shell=True)#, env=env, creationflags=subp.CREATE_NEW_CONSOLE)


