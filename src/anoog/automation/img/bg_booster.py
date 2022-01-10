import abc

import tkinter as tk
from tkinter import ttk

# the Subject with 1 change -> saving with Hashmap for more performance
class Subject(abc.ABC):
    def __init__(self):
        self.observers = dict()

    def attach(self, obj, name):
        if name in self.observers.keys():
            print("Warning, you overwrite an observer by attaching  an observer with same name")
        self.observers[name] = obj

    def dettach(self, new_color):
        del self.observers[name]

    def notify(self, **arguments):
        for name, observer in self.observers.items():
            observer.update(**arguments)


class Color_Gradient_Booster(Subject):
    def __init__(self):
        self.light_observer = []
        self.dark_observer = []

        self.color = []

    def run_in_thread(self):
        threading(command=self.run).start()

    def run(self):
        pass

    def stop(self):
        pass

    def change(self):
        pass


# Simulates an interface -> abstract class works like an interface with 1 negative point
class Observer(abc.ABC):
    @abc.abstractclassmethod
    def update(self, **arguments):    #is a hashmap of arguments
        pass


# XXX Testing XXX
class Test_Canvas(Observer):
    def __init__(self, root):
        super().__init__(root)
        self.root = root

    def update(self, **args):
        self.draw_rectangle((args['x0'], args['y0'], args['x1'], args['y1']), fill=(args['r'], args['g'], args['b']))


if __name__ == "__main__":
    root = Tk()

    main_window = ttk.Frame(root)
    main_window.pack(expand=True, fill='both')

    cg_booster = Color_Gradient_Booster()

    my_widget = Test_Canvas(main_window)
    my_widget.grid(row=1, column=1)

    cg_booster.attach(my_widget, 'canvas_bar')
    cg_booster.run_in_thread()

    #Label(root, text="Gradient 1:").pack(anchor=W)
    #GradientFrame(root, from_color="#000000", to_color="#E74C3C", height=100).pack(fill=X)
    
    #Label(root, text="Gradient 2 (GTK gradient):").pack(anchor=W, pady=(20,0))
    #GradientFrame(root, from_color="#FCFCFC", to_color="#E2E2E2", height=30, width=50, orient='VERTICAL').pack(fill=X, pady=(0,10))
     

    root.mainloop()
