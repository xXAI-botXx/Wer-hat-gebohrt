"""
This module is used to start and control the drillcapture and drilldriver programs.

Author: Tobia Ippolito
"""

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

op = Enum('op', 'WINDOWS LINUX')

class Process_Interface(abc.ABC, Eventsystem_Component):
    """
    Basic class for starting and controlling a process. 
    Uses the strategy-pattern. What means, that the specific start-method can be implemented by every startegy.

    :param absolut_path_to_exe: Describes the path to the location of the executable file, which will be run in Popen.
    :type absolut_path_to_exe: str
    :param terminal: Control object, to send event messages back.
    :type terminal: :class:`~anoog.automation.controller.Terminal`
    :param operating_system: Defines the current operating system. Impoartant for internal decisions (how to run commands).
    :type operating_system: :class:`~anoog.automation.py_exe_interface.op`, optional
    """
    def __init__(self, absolut_path_to_exe:str, terminal, operating_system=op.WINDOWS):
        """
        Constructor method
        """
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
        """
        Method to implement the specific strategy.
        """
        pass

    def run(self):
        """
        Starts the program (with specified strategy) and listen to incomming events.
        """
        self.should_run = True

        self.start_program()
        
        #os.system("start cmd /K dir")

        self.event_listener()


    def read(self):
        """
        Reads the incomming Stream in Output Stream.
        Saves it in a File.

        :return: The content in the Outputstream
        :rtype: str
        """
        out = self.process.stdout.readline().decode().strip()
        self.save_in_file(out+"\n")
        return out

    def read_err(self):
        """
        Reads the incomming Stream in Error Stream.
        Saves it in a File.

        :return: The content in the Errorstream
        :rtype: str
        """
        out = self.process.stderr.readline().decode().strip()
        self.save_in_file(out+"\n", "err_log.txt")
        return out

    def write(self, reaction:str):
        """
        Writes something in the inputstream of the started program.
        With that, the :class:`~anoog.automation.controller.Terminal` can communicate with the program.
        Started not by :class:`~anoog.automation.controller.Terminal`, instead of indirect start with a event.

        :param reaction: The Message, which the programm will gets.
        :type reaction: str
        """
        self.process.stdin.write(f"{reaction}\n".encode())
        try:
            self.process.stdin.flush()
        except OSError as e:
            pass

    # should run in thread, so that you can write input
    def event_listener(self):
        """
        Checks the events, what the :class:`~anoog.automation.controller.Terminal` communicate which this interface about.
        """
        while self.should_run: #and self.is_alive():
            #print("Process_Interface on work...")
            self.run_event()

            threading.Event().wait(0.2)

    def check_input(self):
        """
        Checks the stdin.txt, if there is a message for the interface/program.
        (Currently not used)
        """
        input = ""
        path = "/".join(__file__.split("\\")[:-1])
        with open(f"{path}/output/stdin.txt","r") as f:
            input = f.read()

    # dont works!!!
    def is_alive(self) -> bool:
        """
        Checks if the program is already running.
        Don't works at all.

        :return: If the program works
        :rtype: bool
        """
        if self.process.poll() == None:
            return True
        else:
            return False

    def process_status(self):
        """
        Should give a feedback of the status of the program.

        :return: Status of Program ( `running`, `paused`, `start_pending`, `pause_pending`, `continue_pending`, `stop_pending`, `stopped` or `not_existing`)
        :rtype: str
        """
        pid = self.process.pid
        process_status = None
        try:
            process_status = psutil.Process(pid).status()
        except psutil.NoSuchProcess as no_proc_exc:
            return 'not_existing'

        return process_status

    def stop(self, send_event=False):
        """
        Stops the started program.

        :param send_event: If a event should be sended as reaction.
        :type send_event: bool, optional
        """
        self.should_run = False
        try:
            if self.process != None and self.process.stdin != None:
                self.process.stdin.close()
        except OSError:
            pass
        if self.process != None:
            self.process.terminate()

    
    def save_in_file(self, txt:str, file="log.txt"):
        """
        Saves a given message in a log file (doeasn't ovveride something)

        :param txt: Message which will be write in the file.
        :type txt: str
        :param txt: Name of the log file.
        :type txt: str, optional
        """
        path = "/".join(self.path_to_exe.split("/")[:-1])
        with open(path+"/"+file, "a") as f:
            f.write(txt)


class Drilldriver_Interface(Process_Interface):
    """
    Class to start a drilldriver and communicate with it.

    :param absolut_path_to_exe: Describes the path to the location of the executable file, which will be run in Popen.
    :type absolut_path_to_exe: str
    :param terminal: Control object, to send event messages back.
    :type terminal: :class:`~anoog.automation.controller.Terminal`
    :param operating_system: Defines the current operating system. Impoartant for internal decisions (how to run commands).
    :type operating_system: :class:`~anoog.automation.py_exe_interface.op`, optional
    """
    def __init__(self, absolut_path_to_exe:str, terminal, operating_system=op.WINDOWS):
        """
        Constructor method
        """
        super().__init__(absolut_path_to_exe, terminal, operating_system)

    def start_program(self):
        """
        Specific stratetgy, which will be called in :meth:`~anoog.automation.py_exe_interface.Process_Interface.run`.

        Starts the Drilldriver.
        """
        if self.operating_system == op.WINDOWS:
            c = ["start", '/b', self.path_to_exe]
        else:
            c = [self.path_to_exe]

        self.process = subp.Popen(c,  shell=True)    #  stdin=subp.PIPE, stdout=subp.PIPE, stderr=subp.PIPE,


class Drillcapture_Interface(Process_Interface):
    """
    Class to start a drillcapture and communicate with it.

    :param absolut_path_to_exe: Describes the path to the location of the executable file, which will be run in Popen.
    :type absolut_path_to_exe: str
    :param terminal: Control object, to send event messages back.
    :type terminal: :class:`~anoog.automation.controller.Terminal`
    :param operating_system: Defines the current operating system. Impoartant for internal decisions (how to run commands).
    :type operating_system: :class:`~anoog.automation.py_exe_interface.op`, optional
    :param name: Name of the person, who want to start a drill.
    :type name: str, optional
    """
    def __init__(self, absolut_path_to_exe:str, path_to_output, terminal, operating_system=op.WINDOWS, name=None):
        """
        Constructor method
        """
        super().__init__(absolut_path_to_exe, terminal, operating_system)
        self.path_to_output = path_to_output
        self.name = name

    # OVERRIDE
    def run(self, mode="bulk"):
        """
        Starts the program and start listing to incoming events.

        Overides :meth:`~anoog.automation.py_exe_interface.Process_Interface.run` for a new argument.

        :param mode: Defines the mode, in which the drillcapture-program will be started.
        :type mode: str, optional
        """
        self.should_run = True
        self.start_program(mode)
        self.event_listener()

    def start_program(self, mode="bulk"):
        """
        Specific stratetgy, which will be called in :meth:`~anoog.automation.py_exe_interface.Drillcapture_Interface.run`.

        Starts the Drilldriver.

        :param mode: Defines the mode, in which the drillcapture-program will be started.
        :type mode: str, optional
        """
        now = datetime.now()
        if mode == 'bulk':
            if self.operating_system == op.WINDOWS:
                c = ["start", '/b', self.path_to_exe, f"-mode=bulk", f"-description={now.year}-{now.month}-{now.day}.yaml"]
            else:
                c = [f"{self.path_to_exe} -interface=cli -module=drill -mode=bulk -description=/home/anoog/rec/thema1/{now.year}-{now.month}-{now.day}/{now.year}-{now.month}-{now.day}.yaml"]
        elif mode == "single":
            if self.operating_system == op.WINDOWS:
                c = ["start", '/b', self.path_to_exe, f"-mode=single", f"-description={self.name}/meta.yaml"]
            else:
                c = [f"{self.path_to_exe} -interface=cli -module=drill -mode=single -description=/home/anoog/rec/thema1/{now.year}-{now.month}-{now.day}/{self.name}/meta.yaml"]

        with open(f"{self.path_to_output}/stdout.txt","wb") as out, open(f"{self.path_to_output}/stderr.txt","wb") as err:
            self.process = subp.Popen(c, stdin=subp.PIPE, stdout=out, stderr=err,    
                                        shell=True)#, env=env, creationflags=subp.CREATE_NEW_CONSOLE)


