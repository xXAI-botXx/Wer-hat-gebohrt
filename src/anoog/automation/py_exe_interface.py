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

#from pexpect.popen_spawn import PopenSpawn

# Event = {str:(name, function), str:(name, function), ..} -> str ist die Output Bedingung und name ist das Event, welches dann ausgelöst werden soll
# Funktion wird bei auftreten von str mit Parameter name aufgerufen + Process mit mit übergeben

op = Enum('op', 'WINDOWS LINUX')

class Process_Interface(abc.ABC):
    #id = 0
    def __init__(self, absolut_path_to_exe:str, terminal, operating_system=op.WINDOWS):
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
        self.terminal.add_event('wrote-input')

    # should run in thread, so that you can write input
    def event_listener(self):
        while self.should_run: #and self.is_alive():
            #print("Process_Interface on work...")
            if not self.events.empty():
                event = self.events.get()
                if len(event) > 1:
                    self.EVENT[event[0]](*event[1])
                else:
                    self.EVENT[event[0]]()

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
            self.process.stdin.close()
            #self.process.stdout.close()
            #self.process.stderr.close()
        except OSError:
            pass
        self.process.terminate()
        self.process.wait(timeout=0.2)
        if send_event:
            pass
            #self.terminal.add_event("process-ended")

    
    def save_in_file(self, txt:str, file="log.txt"):
        path = "/".join(self.path_to_exe.split("/")[:-1])
        with open(path+"/"+file, "a") as f:
            f.write(txt)

    def add_event(self, event_name, *additions):
        print("added event in a Process_Interface")
        event = (event_name, *additions)
        self.events.put(event, block=False)


class Drilldriver_Interface(Process_Interface):
    def __init__(self, absolut_path_to_exe:str, terminal, operating_system=op.WINDOWS):
        super().__init__(absolut_path_to_exe, terminal, operating_system)

    def start_program(self):
        if self.operating_system == op.WINDOWS:
            c = ["start", '/b', self.path_to_exe]
        else:
            c = [self.path_to_exe]

        self.process = subp.Popen(c, stdin=subp.PIPE, stdout=subp.PIPE, stderr=subp.PIPE, shell=True)

    #def run(self):
    #    Process_Interface.run(self)

# adding arguments + predict mode
class Drillcapture_Interface(Process_Interface):
    def __init__(self, absolut_path_to_exe:str, path_to_output, terminal, operating_system=op.WINDOWS):
        super().__init__(absolut_path_to_exe, terminal, operating_system)
        self.path_to_output = path_to_output

    # OVERRIDE
    def run(self, mode="bulk"):
        self.should_run = True
        self.start_program(mode)
        self.event_listener()

    def start_program(self, mode="bulk"):
        if mode == 'bulk':
            now = datetime.now()
            if self.operating_system == op.WINDOWS:
                c = ["start", '/b', self.path_to_exe, f"-mode=bulk", f"-description={now.year}-{now.month}-{now.day}.yaml"]
            else:
                c = [self.path_to_exe, f"-mode=bulk", f"-description={now.year}-{now.month}-{now.day}.yaml"]
        elif mode == "single":
            if self.operating_system == op.WINDOWS:
                c = ["start", '/b', self.path_to_exe, f"-mode=single", f"-description=UNKNOWN/meta.yaml"]
            else:
                c = [self.path_to_exe, f"-mode=single", f"-description=UNKNOWN/meta.yaml"]

        #path = "/".join(__file__.split("\\")[:-1])
        with open(f"{self.path_to_output}/stdout.txt","wb") as out, open(f"{self.path_to_output}/stderr.txt","wb") as err:
            self.process = subp.Popen(c, stdin=subp.PIPE, stdout=out, stderr=err,    #subp.PIPE
                                        shell=True)#, env=env, creationflags=subp.CREATE_NEW_CONSOLE)

    #def run(self):
    #    Process_Interface.run(self)


