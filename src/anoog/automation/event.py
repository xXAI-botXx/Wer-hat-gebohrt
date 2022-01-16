import abc
from queue import Queue, Empty

class Eventsystem_Component():
    """
    A member in the eventsystem should inherite from this class.
    --------
    Funtionality:
    Other objectes/methods can call add_event() to add a new Event. Now the spicific Eventmember
    can process this event in his Thread by calling run_event. The given event in the queue is
    a key in the EVENT HashMap. The value should be a method, which will be called in run_event.

    The Event should be a String (the eventname/key in EVENT) and can add multi-params in a tuple.
    For one param you should call as follow: add_Event(eventname, (param1, ))
    --------
    Notice following points:
    - The variable EVENT (HashMap/dictionary) should be implemented in the specific Eventmember class.
    - Don't forget to call: EventSystem_Component.__init__(self)
    - call run_event (maybe in ja while-loop or in a observer method)
    """
    def __init__(self):
        self.events = Queue()
        self.EVENT = dict()

    def run_event(self):
        """
        Checks the event-queue and runs a event, if there is one.

        The eventname used as key in the EVENT HashMap. 
        The value should be a callable and this function/method is called.
        If there were params (in a tuple) then they will handed over.

        --------
        Returns None
        """
        if not self.events.empty():
            event = self.events.get()
            #print("Got Event: ", event)
            # event = 'eventname' or event = 'eventname', *args
            if len(event) > 1:
                self.EVENT[event[0]](*event[1])
            else:
                self.EVENT[event[0]]()

    def add_event(self, event_name, *additions):
        """
        Add a new event for this specific eventmember.
        Parameters can added as normal Parameters or in a tuple.

        The event_name should be a key in EVENT-HashMap.

        Arguments:
            - event_name as str (key in EVENT-dict)
            - additions as tuple or multi arguments (if the eventfunction needs more args)
        --------
        Returns None
        """
        event = (event_name, *additions)
        self.events.put(event)

