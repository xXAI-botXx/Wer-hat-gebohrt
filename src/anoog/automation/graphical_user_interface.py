"""
This module is used to implement a graphical user interface for the application.
It contains all Widget/Screen-Classes for GUI. Only the Gradient-Color-Widget has it own class :module:~anoog.automation.bg_booster.py
-> and implements the start-method of the application

Author: Tobia Ippolito
"""

from queue import Queue
from threading import Thread
import abc
from time import time

from PIL import Image, ImageTk

from .controller import Terminal
from .py_exe_interface import op
from .bg_booster import Color_Gradient_Booster
from .event import Eventsystem_Component

import tkinter as tk
from tkinter import font
from tkinter import ttk
from ttkthemes import ThemedStyle

import webbrowser


THEMES = ['smog', 'ubuntu', 'scidgrey', 'scidblue', 
          'scidmint', 'alt', 'adapta', 'vista', 
          'default', 'classic', 'winxpblue', 'scidpurple', 
          'keramik', 'radiance', 'yaru', 'clam', 
          'winnative', 'scidsand', 'breeze', 'plastik', 
          'scidgreen', 'arc', 'equilux', 'clearlooks', 
          'blue', 'kroc', 'itft1', 'black', 
          'scidpink', 'aquativo', 'xpnative', 'elegance']


class GUI_App(tk.Tk, Eventsystem_Component):
    """
    This is the root-Widget of the GUI.

    All other Windows will call and managed drom this root-point.

    :param kwargs: Key, Value arguments for the Widget (relatively unrelevant)
    :type kwargs: dict
    """
    def __init__(self, **kwargs):
        """
        Constructor method
        """
        super().__init__(**kwargs)
        Eventsystem_Component.__init__(self)
        self.bg_img = None
        self.cur_screen = None

        # Theme
        # breeze, breeze-dark, awlight, awdark, arc, equilux, yaru, aqua, adapta
        self.style = ThemedStyle(self)
        self.set_theme("equilux")

        # alle Main-Widgets erszeugen...
        self.screen_main_menu = Menu(self)
        self.screen_train = Train_Window(self)
        self.screen_predict = Predict_Window(self)
        self.screen_credits = Credits_Window(self)

        # now root.geometry() returns valid size/placement
        self.screen_main_menu.show()
        self.cur_screen = self.screen_main_menu
        self.set_min()
        #self.minsize(self.winfo_width(), self.winfo_height())

        self.width = 600
        self.height= 400
        self.geometry(f"{self.width}x{self.height}")
        self.old_size = (self.winfo_width(), self.winfo_height())
        self.mouse_not_hold = True
        self.title('Drill Prediction')
        #self.attributes('-alpha',0.5)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind('<Escape>', self.close)
        self.bind('<Configure>', self.event_resize_bg)
        self.bind('<space>', self.event_space)

        self.events = Queue()
        self.EVENT = {'drill-person':self.screen_train.change_train_person, 'drill-starts':self.screen_train.drill_starts, 
                        'drill-ends':self.screen_train.drill_ends, 'delete-last':self.screen_train.delete_last_btn_change,
                        'drill-amount-change':self.screen_train.drill_amount_change, 'stop-time':self.stop_time,
                        'start-change':self.start_button,
                        'set-amount-predict':self.screen_predict.set_amount, 'predict-drill-starts':self.screen_predict.drill_starts,
                        'predict-drill-ends':self.screen_predict.drill_ends, 'delete-last-predict':self.screen_predict.delete_last_btn_change,
                        'predict-result':self.screen_predict.show_result, 'draw-result':self.screen_predict.draw_result}
        
    def run(self, data_path, drillcapture_path, drilldriver_path, op, path_to_project):
        """
        The Startmethod of the Application.

        Starts the Terminal and the GUI.

        :param data-path: A path to the location where the data will be stored (there will be created a new folder with the current date)
        :type data-path: str, optional
        :param drillcapture_path: A path to the location where the Drillcapture program executable is stored.
        :type drillcapture_path: str, optional
        :param drilldriver_path: A path to the location where the Drilldriver program executable is stored.
        :type drilldriver_path: str, optional
        :param op: Defines on which operating system the program should run.
        :type op: :class:`~anoog.automation.py_exe_interface.op`, optional
        :param path_to_project: A path to the location to the Project folder.
        :type path_to_project: str, optional
        """
        self.path_to_project = path_to_project
        self.terminal = Terminal(self, data_path=data_path, drillcapture_path=drillcapture_path, drilldriver_path=drilldriver_path, op=op)
        self.thread_terminal = Thread(target=self.terminal.run)
        self.thread_terminal.start()

        self.check_events()
        # GUI starting
        self.mainloop()

    def check_events(self):
        """
        Checks the event-queue and calls to do so after 50ms again.
        """
        self.run_event()
        self.after(50, self.check_events)

    def close(self):
        """
        Close the GUI and send an event to terminal to close it too.
        """
        self.terminal.add_event('exit')
        self.quit()

    def set_theme(self, name:str):
        """
        Set the Theme of the GUI. Standart is a dark-theme ('equilux').

        This method will called by load_theme()-method.

        :param name: Name of the theme.
        :type name: str
        """
        if name in THEMES:
            self.style.theme_use(name)
            self.set_min()

    def load_theme(self, name):
        """
        To load a Theme. Coloring and looking of the Widgets.

        See the THEMES list for some Themes examples.

        :param name: Name of the theme.
        :type name: str
        """
        if name in THEMES:
            self.set_theme(name)

    def load_screen_main_menu(self, from_widget):
        """
        To load the Startmenu-Screen.

        :param from_widget: The current screen, which will be hided.
        :type from_widget: :class:~anoog.automation.graphical_user_interface.Screen
        """
        self.cur_screen = self.screen_main_menu
        from_widget.hide()
        self.screen_main_menu.show()
        # set new minimum
        self.set_min()

    def load_screen_train(self, from_widget):
        """
        To load the Train-Screen.

        :param from_widget: The current screen, which will be hided.
        :type from_widget: :class:~anoog.automation.graphical_user_interface.Screen
        """
        self.cur_screen = self.screen_train
        from_widget.hide()
        self.screen_train.show()
        self.set_min()

    def load_screen_predict(self, from_widget):
        """
        To load the Predict-Screen.

        :param from_widget: The current screen, which will be hided.
        :type from_widget: :class:~anoog.automation.graphical_user_interface.Screen
        """
        self.cur_screen = self.screen_predict
        from_widget.hide()
        self.screen_predict.show()
        self.set_min()

    def load_screen_credits(self, from_widget):
        """
        To load the Credit-Screen.

        :param from_widget: The current screen, which will be hided.
        :type from_widget: :class:~anoog.automation.graphical_user_interface.Screen
        """
        self.cur_screen = self.screen_credits
        from_widget.hide()
        self.screen_credits.show()
        self.set_min()

    def reset_predict(self):
        """
        Resets the Predict-Screen. Uses internaly the :meth:~anoog.automation.graphical_user_interface.Predict_Window.event_reset_button method.

        Clears all drill-data, setted settings and showed results.
        """
        self.screen_predict.event_reset_button()
        
    def set_min(self):
        """
        Sets the minimum height and width off a screen. 
        The minimum is calculated, that all widgets have enough size and are completly showed.

        This calculation is automaticly.
        """
        # only if not in Fullscreen mode
        # Version 1:
        #if not (self.wm_state() == 'zoomed'):
        #    # reset
        #    self.minsize(0, 0)
        #    # set new minimum
        #    width = self.winfo_width()
        #    height = self.winfo_height()
        #    self.geometry('')
        #    self.update()
        #    self.minsize(self.winfo_width(), self.winfo_height())
        #    self.geometry(f"{width}x{height}")
        # Version 2:
        if self.cur_screen != None:
            self.minsize(*self.cur_screen.min)
            self.geometry(f"{self.winfo_width()}x{self.winfo_height()}")

    def set_bg(self, img):
        """
        Can be used to set a background-image. 

        The size will be fitted on the screen. It uses a Label, which every screen owned.

        (Currently not used)

        :param img: A Path to an image to load in Background.
        :type img: str
        """
        self.bg_img = img

        if self.bg_img != "":
            self.image = Image.open(img)
            self.image = self.image.resize((self.winfo_width(), self.winfo_height()), Image.ANTIALIAS)

            self.tk_image = ImageTk.PhotoImage(self.image)

            self.screen_configuration.set_bg(self.tk_image)
            self.screen_main_menu.set_bg(self.tk_image)
            self.screen_train.set_bg(self.tk_image)
            self.screen_predict.set_bg(self.tk_image)
        else:
            self.screen_configuration.set_bg("")
            self.screen_main_menu.set_bg("")
            self.screen_train.set_bg("")
            self.screen_predict.set_bg("")

    def event_resize_bg(self, event):
        """
        An event to fit the background-image to the screen-size.

        Will be called every time, if the screen-size is changing. Only change image-size, if the size has changed.
        (The method also will be called, if the user moves the application.)

        :param event: The event from Tkinter for resizing.
        """
        size_changed = self.old_size[0] != self.winfo_width() or self.old_size[1] != self.winfo_height()
        if self.bg_img != None and self.bg_img != "" and size_changed and self.mouse_not_hold:
            self.old_size = (self.winfo_width(), self.winfo_height())
            self.image = Image.open(self.bg_img)
            self.image = self.image.resize((self.winfo_width(), self.winfo_height()), Image.ANTIALIAS)

            self.tk_image = ImageTk.PhotoImage(self.image)

            self.screen_configuration.resize_bg(self.tk_image)
            self.screen_main_menu.resize_bg(self.tk_image)
            self.screen_train.resize_bg(self.tk_image)

    def event_space(self, event):
        """
        Event handling for pressing Spacebar.
        Used for starting/stopping a new drill-process.

        :param event: The event from Tkinter for Key-Pressed.
        """
        if self.cur_screen == self.screen_train:
            self.screen_train.event_start_button()
        elif self.cur_screen == self.screen_predict:
            self.screen_predict.event_start_button()

    def stop_time(self):
        """
        Event handling for pressing Spacebar.
        Used for starting/stopping a drill-process.
        """
        if self.cur_screen == self.screen_train:
            self.screen_train.stop_time()
        elif self.cur_screen == self.screen_predict:
            self.screen_predict.stop_time()

    def start_button(self, state):
        """
        Method to change the state of the start-button in the current screen.
        If disabled, the button isn't pressable anymore.

        Only in predict-Screen or in Train-Screen available.

        :param state: State in which the start-button should be switch: 'disabled' or 'enabled' available.
        :type state: str
        """
        if self.cur_screen == self.screen_train:
            self.screen_train.start_button_change(state)
        elif self.cur_screen == self.screen_predict:
            self.screen_predict.start_button_change(state)


###############################################
###############    Screen    ##################
###############################################
class Screen(ttk.Frame, abc.ABC):
    """
    Base Class for all Screens. 

    Implements the functionality for setting a background-image.
    For that a label is initialized. And methods to set and resize an image.

    :param root: Root-Widget. Needed for communicate with :class:~anoog.automation.controller.Terminal.
    :param root: tk.Tk
    :param kwargs: Key, Value arguments for the Widget (relatively unrelevant)
    :type kwargs: dict
    """
    def __init__(self, root, **kwargs):
        """
        Constructor method
        """
        super().__init__(root, **kwargs)
        self.root = root

        self.min = (200, 200)

        self.label_bg = ttk.Label(self)
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

    def resize_bg(self, img):
        """
        Method to reset the image of the label.

        :param img: New Backgroundimage
        :type img: PIL.ImageTk
        """
        self.label_bg.configure(image=img)

    def set_bg(self, img):
        """
        Method to reset the image of the label.

        :param img: New Backgroundimage
        :type img: PIL.ImageTk
        """
        self.label_bg.configure(image=img)


###############################################
#############   Menu_Screen    ################
###############################################
class Menu(Screen):
    """
    Contains all widgets from start-screen. 3 Buttons (start, informationen, credits), title-label, Gradientcolor-stripes.

    :param root: Root-Widget. Needed for communicate with :class:~anoog.automation.controller.Terminal.
    :param root: tk.Tk
    :param kwargs: Key, Value arguments for the Widget (relatively unrelevant)
    :type kwargs: dict
    """
    def __init__(self, root, **kwargs):
        """
        Constructor method
        """
        super().__init__(root, **kwargs)
        self.min = (1200, 700)

        self.max_rows = 1+3+1
        self.max_columns = 1+3+1
        self.widget_list = {}
        self.create_widgets()
        self.weighting()
        #self.hide()

    def create_widgets(self):
        """
        Method to create all important Widgets of the Start-Menu.
        """
        # Color Background
        self.color_label = ttk.Label(self)
        self.color_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.color_frame_bg = Color_Gradient_Booster(root=self.root, parent=self.color_label, 
                                                    mode='VERTICAL', should_change_color=True,
                                                    color_chain=('#05ffa1', '#b967ff'))
        self.color_frame_bg.place(relx=0, rely=0, relwidth=1, relheight=1)
        #self.color_frame_bg.set_fav_color()
        # Spacing Frames to hide the color
        self.show_frame_1 = ttk.Frame(self.color_label)
        self.show_frame_1.place(relx=0, rely=0, relwidth=0.3, relheight=0.21)
        self.show_frame_2 = ttk.Frame(self.color_label)
        self.show_frame_2.place(relx=0, rely=0.22, relwidth=0.2, relheight=0.2)
        self.show_frame_3 = ttk.Frame(self.color_label)
        self.show_frame_3.place(relx=0.35, rely=0.0, relwidth=0.55, relheight=0.1)
        self.show_frame_4 = ttk.Frame(self.color_label)
                                            #11
        self.show_frame_4.place(relx=0.35, rely=0.105, relwidth=0.55, relheight=0.2)
        self.show_frame_5 = ttk.Frame(self.color_label)
        self.show_frame_5.place(relx=0.2, rely=0.0, relwidth=0.15, relheight=0.3)
        self.show_frame_6 = ttk.Frame(self.color_label)
        self.show_frame_6.place(relx=0.9, rely=0.0, relwidth=0.5, relheight=0.4)
        self.show_frame_7 = ttk.Frame(self.color_label)
        self.show_frame_7.place(relx=0.0, rely=0.3, relwidth=1.1, relheight=0.2)
        self.show_frame_8 = ttk.Frame(self.color_label)
        self.show_frame_8.place(relx=0.4, rely=0.5, relwidth=0.04, relheight=0.4)
        self.show_frame_9 = ttk.Frame(self.color_label)
        self.show_frame_9.place(relx=0.7, rely=0.5, relwidth=0.4, relheight=0.4)
        self.show_frame_10 = ttk.Frame(self.color_label)
        self.show_frame_10.place(relx=0.4, rely=0.51, relwidth=0.4, relheight=0.4)
        self.show_frame_11 = ttk.Frame(self.color_label)
        self.show_frame_11.place(relx=0, rely=0.5, relwidth=0.4, relheight=0.4)
        self.show_frame_12 = ttk.Frame(self.color_label)
        self.show_frame_12.place(relx=0, rely=0.905, relwidth=0.8, relheight=0.4)
        self.show_frame_13 = ttk.Frame(self.color_label)
        self.show_frame_13.place(relx=0, rely=0.9, relwidth=0.1, relheight=0.4)
        self.show_frame_14 = ttk.Frame(self.color_label)
        self.show_frame_14.place(relx=0.8, rely=0.9, relwidth=0.3, relheight=0.05)
        self.show_frame_15 = ttk.Frame(self.color_label)
                                                #96
        self.show_frame_15.place(relx=0.8, rely=0.955, relwidth=0.3, relheight=0.2)

        # Create Title Label
        self.label_title = ttk.Label(self, text="Wer hat gebohrt?", anchor='center')
        self.label_title.grid(row=1, column=1, columnspan=3, sticky='NESW')
        self.widget_list['lable_title'] = self.label_title
        self.label_title.bind('<Configure>', self.event_resize_label)

        # Create Start Button
        self.button_start = ttk.Button(self, text="Start", command=self.event_button_start, takefocus=0)
        self.button_start.grid(row=3, column=1, sticky='NESW')
        self.widget_list['button_start'] = self.button_start

        # Create Credit Button
        self.button_credits = ttk.Button(self, text="Credits", command=self.event_button_credits, takefocus = 0)
        self.button_credits.grid(row=3, column=3, sticky='NESW')
        self.widget_list['button_credits'] = self.button_credits

        # Create Information Button
        self.button_info= ttk.Button(self, text="Informationen", command=self.event_button_info, takefocus = 0)
        self.button_info.grid(row=3, column=2, sticky='NESW')
        self.widget_list['button_info'] = self.button_info

        self.add_padding()

    def add_padding(self):
        """
        Defines all paddings of the widgets.
        """
        for child in self.winfo_children():
            child.grid_configure(padx=40, pady=10)
        self.label_title.grid_configure(padx=10, pady=10)
        #self.grid_rowconfigure(5, minsize=20)

    def weighting(self):
        """
        Defines all weightings of the widgets.

        The weighting defines, how intensive the grid-entry fit, if the size of the screen is changing.
        """
        for n in range(self.max_rows-1):
            self.grid_rowconfigure(n, weight=1, minsize=50)
        
        for n in range(1, self.max_columns-1):
            self.grid_columnconfigure(n, weight=1, minsize=100)

        #self.grid_rowconfigure(0, weight=1, minsize=50)
        #self.grid_columnconfigure(1, weight=1, minsize=100)

        # spacing
        self.grid_rowconfigure(self.max_rows-1, weight=1, minsize=30)
        self.grid_columnconfigure(0, weight=1, minsize=100)
        self.grid_columnconfigure(self.max_columns-1, weight=1, minsize=100)
    
    def show(self):
        """
        Shows the Start-Menu screen.

        For that the screen will be packed and the gradient-color stripes will be started.
        """
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.color_frame_bg.start()
        self.color_label.place_forget()
        self.color_label.place(relx=0, rely=0, relwidth=1, relheight=1)

    def hide(self):
        """
        Hides the Start-Menu screen.

        For that the screen will be unpacked and the gradient-color stripes will be stopped.
        """
        self.pack_forget()
        self.color_frame_bg.stop()

    def event_button_start(self):
        """
        Loads the train-screen.

        Should be called, if the Start-Button pressed.
        """
        self.root.load_screen_train(self)

    def event_button_credits(self):
        """
        Loads the credits-screen.

        Should be called, if the Credits-Button pressed.
        """
        self.root.load_screen_credits(self)

    def event_button_info(self):
        """
        Opens the README-File of our project.

        Should be called, if the Informationen-Button pressed.
        """
        webbrowser.open_new("https://github.com/xXAI-botXx/Wer-hat-gebohrt/blob/main/README.md")

    def event_resize_label(self, event):
        """
        Change the label-font size of the title, if the screen-size has changed.

        With that method, the title is in a right size.

        :param event: The event from Tkinter for resizing.
        """
        width = event.widget.winfo_width()
        height = event.widget.winfo_height()
        event.widget.configure(font=font.Font(size=height//3))


###############################################
#############   Train_Screen    ###############
###############################################
class Train_Window(Screen):
    """
    Contains the logic and all widgets from train-screen. 

    Included the Meta-Data-Section, the gradient-color hyphen and the train-data-section.

    This Screen used to collect train-data for the prediction.

    :param root: Root-Widget. Needed for communicate with :class:~anoog.automation.controller.Terminal.
    :param root: tk.Tk
    :param kwargs: Key, Value arguments for the Widget (relatively unrelevant)
    :type kwargs: dict
    """
    def __init__(self, root, **kwargs):
        """
        Constructor method
        """
        super().__init__(root, **kwargs)
        self.min = (1200, 700)

        self.max_rows = 1+1+1
        self.max_columns = 1+1+1+2+1    #between the widgets, right has span 2

        self.create_widgets()
        self.weighting()
        self.add_padding()
        self.hide()

        self.start_time = None
        self.is_drilling = False

    def create_widgets(self):
        """
        Method to create all important Widgets of the Train-Screen.
        """
        # Back Button
        self.button_back = ttk.Button(self, text="<", command=self.event_back, takefocus = 0)
        self.button_back.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        # --- Create init part ---
        self.init_frame = ttk.Frame(self)

        self.init_label_title = ttk.Label(self.init_frame, text="Metadaten", anchor='center', font='Helvetica 18 bold')
        self.init_label_title.grid(row=1, column=1, columnspan=3)

        # Person1
        self.init_person_1_label = ttk.Label(self.init_frame, text="Person 1", anchor='center', font='Helvetica 13 bold')
        self.init_person_1_label.grid(row=2, column=1)
        # Name
        self.init_person_1_name_label = ttk.Label(self.init_frame, text="Name", anchor='center')
        self.init_person_1_name_label.grid(row=3, column=1)
        self.var_person1_name = tk.StringVar()
        self.var_person1_name.set("Person1")
        self.var_person1_name.trace_add("write", self.init_changes)
        self.init_person_1_name = ttk.Entry(self.init_frame, textvariable=self.var_person1_name)
        self.init_person_1_name.grid(row=3, column=2, columnspan=2)
        # Drill-Amount
        self.init_person_1_drill_amount_label = ttk.Label(self.init_frame, text="Bohranzahl", anchor='center')
        self.init_person_1_drill_amount_label.grid(row=4, column=1)
        self.var_person1_drill_amount = tk.StringVar()
        self.var_person1_drill_amount.set("10")
        self.var_person1_drill_amount.trace_add("write", self.init_changes)
        self.init_person_1_drill_amount = ttk.Entry(self.init_frame, textvariable=self.var_person1_drill_amount)
        self.init_person_1_drill_amount.grid(row=4, column=2, columnspan=2)
        # Material
        self.init_person_1_material_label = ttk.Label(self.init_frame, text="Material", anchor='center')
        self.init_person_1_material_label.grid(row=5, column=1)
        self.var_person1_material = tk.StringVar()
        self.var_person1_material.set("wood-eiche")
        self.var_person1_material.trace_add("write", self.init_changes)
        self.init_person_1_material = ttk.Entry(self.init_frame, textvariable=self.var_person1_material)
        self.init_person_1_material.grid(row=5, column=2, columnspan=2)
        # Drill-Type
        self.init_person_1_drill_type_label = ttk.Label(self.init_frame, text="Bohraufsatz", anchor='center')
        self.init_person_1_drill_type_label.grid(row=6, column=1)
        self.var_person1_drill_type = tk.StringVar()
        self.var_person1_drill_type.set("universal")
        self.var_person1_drill_type.trace_add("write", self.init_changes)
        self.init_person_1_drill_type = ttk.Entry(self.init_frame, textvariable=self.var_person1_drill_type)
        self.init_person_1_drill_type.grid(row=6, column=2, columnspan=2)
        # Drill-Gear
        self.init_person_1_drill_gear_label = ttk.Label(self.init_frame, text="Bohrgang", anchor='center')
        self.init_person_1_drill_gear_label.grid(row=7, column=1)
        self.var_person1_drill_gear = tk.StringVar()
        self.var_person1_drill_gear.set("2")
        self.var_person1_drill_gear.trace_add("write", self.init_changes)
        self.init_person_1_drill_gear = ttk.Entry(self.init_frame, textvariable=self.var_person1_drill_gear)
        self.init_person_1_drill_gear.grid(row=7, column=2, columnspan=2)
        # Drill-Size
        self.init_person_1_drill_size_label = ttk.Label(self.init_frame, text="Bohrgröße", anchor='center')
        self.init_person_1_drill_size_label.grid(row=8, column=1)
        self.var_person1_drill_size = tk.StringVar()
        self.var_person1_drill_size.set("4")
        self.var_person1_drill_size.trace_add("write", self.init_changes)
        self.init_person_1_drill_size = ttk.Entry(self.init_frame, textvariable=self.var_person1_drill_size)
        self.init_person_1_drill_size.grid(row=8, column=2, columnspan=2)
        # akku
        self.init_person_1_akku_label = ttk.Label(self.init_frame, text="Akku", anchor='center')
        self.init_person_1_akku_label.grid(row=9, column=1)
        self.var_person1_akku = tk.StringVar()
        self.var_person1_akku.set("normal")
        self.var_person1_akku.trace_add("write", self.init_changes)
        self.init_person_1_akku = ttk.Entry(self.init_frame, textvariable=self.var_person1_akku)
        self.init_person_1_akku.grid(row=9, column=2, columnspan=2)
        # samplerate
        #self.init_person_1_samplerate_label = ttk.Label(self.init_frame, text="Wiederholungsrate", anchor='w')
        #self.init_person_1_samplerate_label.grid(row=9, column=0)
        #self.var_person1_samplerate = tk.StringVar()
        #self.var_person1_samplerate.set("96000")
        #self.var_person1_samplerate.trace_add("write", self.init_changes)
        #self.init_person_1_samplerate = ttk.Entry(self.init_frame, textvariable=self.var_person1_samplerate)
        #self.init_person_1_samplerate.grid(row=9, column=1, columnspan=2)

        self.init_spacing = ttk.Frame(self.init_frame)
        self.init_spacing.grid(row=11, column=1, columnspan=3)

        # Person2
        self.init_person_2_label = ttk.Label(self.init_frame, text="Person 2", anchor='center', font='Helvetica 13 bold')
        self.init_person_2_label.grid(row=12, column=1)
        # Name
        self.init_person_2_name_label = ttk.Label(self.init_frame, text="Name", anchor='center')
        self.init_person_2_name_label.grid(row=13, column=1)
        self.var_person2_name = tk.StringVar()
        self.var_person2_name.set("Person2")
        self.var_person2_name.trace_add("write", self.init_changes)
        self.init_person_2_name = ttk.Entry(self.init_frame, textvariable=self.var_person2_name)
        self.init_person_2_name.grid(row=13, column=2, columnspan=2)
        # Drill-Amount
        self.init_person_2_drill_amount_label = ttk.Label(self.init_frame, text="Bohranzahl", anchor='center')
        self.init_person_2_drill_amount_label.grid(row=14, column=1)
        self.var_person2_drill_amount = tk.StringVar()
        self.var_person2_drill_amount.set("10")
        self.var_person2_drill_amount.trace_add("write", self.init_changes)
        self.init_person_2_drill_amount = ttk.Entry(self.init_frame, textvariable=self.var_person2_drill_amount)
        self.init_person_2_drill_amount.grid(row=14, column=2, columnspan=2)
        # Material
        self.init_person_2_material_label = ttk.Label(self.init_frame, text="Material", anchor='center')
        self.init_person_2_material_label.grid(row=15, column=1)
        self.var_person2_material = tk.StringVar()
        self.var_person2_material.set("wood-eiche")
        self.var_person2_material.trace_add("write", self.init_changes)
        self.init_person_2_material = ttk.Entry(self.init_frame, textvariable=self.var_person2_material)
        self.init_person_2_material.grid(row=15, column=2, columnspan=2)
        # Drill-Type
        self.init_person_2_drill_type_label = ttk.Label(self.init_frame, text="Bohraufsatz", anchor='center')
        self.init_person_2_drill_type_label.grid(row=16, column=1)
        self.var_person2_drill_type = tk.StringVar()
        self.var_person2_drill_type.set("universal")
        self.var_person2_drill_type.trace_add("write", self.init_changes)
        self.init_person_2_drill_type = ttk.Entry(self.init_frame, textvariable=self.var_person2_drill_type)
        self.init_person_2_drill_type.grid(row=16, column=2, columnspan=2)
        # Drill-Gear
        self.init_person_2_drill_gear_label = ttk.Label(self.init_frame, text="Bohrgang", anchor='center')
        self.init_person_2_drill_gear_label.grid(row=17, column=1)
        self.var_person2_drill_gear = tk.StringVar()
        self.var_person2_drill_gear.set("2")
        self.var_person2_drill_gear.trace_add("write", self.init_changes)
        self.init_person_2_drill_gear = ttk.Entry(self.init_frame, textvariable=self.var_person2_drill_gear)
        self.init_person_2_drill_gear.grid(row=17, column=2, columnspan=2)
        # Drill-Size
        self.init_person_2_drill_size_label = ttk.Label(self.init_frame, text="Bohrgröße", anchor='center')
        self.init_person_2_drill_size_label.grid(row=18, column=1)
        self.var_person2_drill_size = tk.StringVar()
        self.var_person2_drill_size.set("4")
        self.var_person2_drill_size.trace_add("write", self.init_changes)
        self.init_person_2_drill_size = ttk.Entry(self.init_frame, textvariable=self.var_person2_drill_size)
        self.init_person_2_drill_size.grid(row=18, column=2, columnspan=2)
        # akku
        self.init_person_2_akku_label = ttk.Label(self.init_frame, text="Akku", anchor='center')
        self.init_person_2_akku_label.grid(row=19, column=1)
        self.var_person2_akku = tk.StringVar()
        self.var_person2_akku.set("normal")
        self.var_person2_akku.trace_add("write", self.init_changes)
        self.init_person_2_akku = ttk.Entry(self.init_frame, textvariable=self.var_person2_akku)
        self.init_person_2_akku.grid(row=19, column=2, columnspan=2)
        # samplerate
        #self.init_person_2_samplerate_label = ttk.Label(self.init_frame, text="Wiederholungsrate", anchor='w')
        #self.init_person_2_samplerate_label.grid(row=19, column=0)
        #self.var_person2_samplerate = tk.StringVar()
        #self.var_person2_samplerate.set("96000")
        #self.var_person2_samplerate.trace_add("write", self.init_changes)
        #self.init_person_2_samplerate = ttk.Entry(self.init_frame, textvariable=self.var_person2_samplerate)
        #self.init_person_2_samplerate.grid(row=19, column=1, columnspan=2)

        self.confirm_frame = ttk.Frame(self.init_frame)
        self.confirm_frame.grid(row=21, column=3, sticky="e")
        self.init_confirm = ttk.Button(self.confirm_frame, text="bestätigen", command=self.event_confirm_init_change, takefocus = 0)
        self.init_confirm.grid(row=0, column=0)

        # adding
        self.init_frame.grid(row=1, column=1)

        # --- Create train part ---
        self.train_frame = ttk.Frame(self)

        self.train_label_title = ttk.Label(self.train_frame, text="Training", anchor='center', font='Helvetica 18 bold')
        self.train_label_title.grid(row=1, column=2, columnspan=1)

        self.train_drill_amount_title = ttk.Label(self.train_frame, text="Bohrungen:", anchor='w', font='Helvetica 13 bold')
        self.train_drill_amount_title.grid(row=2, column=1)

        self.train_drill_amount_person1 = ttk.Label(self.train_frame, text=f"{self.var_person1_name.get()}: {self.var_person1_drill_amount.get()}", anchor='w', font='Helvetica 10 bold')
        self.train_drill_amount_person1.grid(row=3, column=1)

        self.train_drill_amount_person2 = ttk.Label(self.train_frame, text=f"{self.var_person2_name.get()}: {self.var_person2_drill_amount.get()}", anchor='w', font='Helvetica 10 bold')
        self.train_drill_amount_person2.grid(row=4, column=1)

        self.train_drill_next = ttk.Label(self.train_frame, text="Nächste Bohrung:", anchor='w', font='Helvetica 13 bold')
        self.train_drill_next.grid(row=2, column=3)

        self.train_drill_next_name = ttk.Label(self.train_frame, text="?", anchor='w')
        self.train_drill_next_name.grid(row=3, column=3)

        self.train_spacing = ttk.Frame(self.train_frame)
        self.train_spacing.grid(row=7, column=1, columnspan=3)

        self.train_drill_start = ttk.Button(self.train_frame, text="Start", command=self.event_start_button, takefocus = 0)
        self.train_drill_start.grid(row=7+1, column=3)
        self.train_drill_start.configure(state='disabled')

        self.train_delete_last = ttk.Button(self.train_frame, text="Lösche letzte Bohraufnahme", command=self.event_delete_last_button, takefocus = 0)
        self.train_delete_last.grid(row=8+1, column=2, columnspan=2, sticky="e")
        self.train_delete_last.configure(state='disabled')

        self.train_reset = ttk.Button(self.train_frame, text="Reset", command=self.event_reset_button, takefocus = 0)
        self.train_reset.grid(row=7+1, column=1)
        self.train_reset.configure(state='disabled')

        self.train_predict = ttk.Button(self.train_frame, text="Predict", command=self.event_predict_button, takefocus = 0)
        self.train_predict.grid(row=7+1, column=2)
        self.train_predict.configure(state='disabled')

        self.train_runtime = ttk.Label(self.train_frame, text="Zeit: -", anchor='center', font='Helvetica 10 bold')
        self.train_runtime.grid(row=6+1, column=3)

        # Drill Amount Adding
        self.drill_amount_adding_frame = ttk.Frame(self.train_frame)
        self.drill_amount_adding_frame.grid(row=6, column=1, columnspan=2, sticky="w")#10

        self.drill_add_amounts_label = ttk.Label(self.drill_amount_adding_frame, text="Weitere Bohrungen:", anchor='w', font='Helvetica 11 bold')
        self.drill_add_amounts_label.grid(row=0, column=0, columnspan=2)

        self.drill_add_amounts_person1_label = ttk.Label(self.drill_amount_adding_frame, text="Person1", anchor='center')
        self.drill_add_amounts_person1_label.grid(row=1, column=0)
        self.var_add_person1_amount = tk.StringVar()
        self.var_add_person1_amount.set("5")
        self.drill_add_person1_entry = ttk.Entry(self.drill_amount_adding_frame, textvariable=self.var_add_person1_amount)
        self.drill_add_person1_entry.grid(row=1, column=1)
        self.drill_add_person1_entry.configure(state='disabled')

        self.drill_add_amounts_person2_label = ttk.Label(self.drill_amount_adding_frame, text="Person2", anchor='center')
        self.drill_add_amounts_person2_label.grid(row=2, column=0)
        self.var_add_person2_amount = tk.StringVar()
        self.var_add_person2_amount.set("5")
        self.drill_add_person2_entry = ttk.Entry(self.drill_amount_adding_frame, textvariable=self.var_add_person2_amount)
        self.drill_add_person2_entry.grid(row=2, column=1)
        self.drill_add_person2_entry.configure(state='disabled')

        self.confirm_add_frame = ttk.Frame(self.drill_amount_adding_frame)
        self.confirm_add_frame.grid(row=3, column=1, sticky="e")
        self.add_confirm = ttk.Button(self.confirm_add_frame, text="bestätigen", command=self.event_confirm_add, takefocus = 0)
        self.add_confirm.grid(row=0, column=0)
        self.add_confirm.configure(state='enabled')

        # adding
        self.train_frame.grid(row=1, column=3, columnspan=2)

        # Spacing between the two areas
        self.frame_spacing = tk.Frame(self, width=4, height=500)#,bg='#ebcf34')
        self.frame_spacing.grid(row=0, column=2, rowspan=3)
        self.cg_booster_borderline = Color_Gradient_Booster(root=self.root, parent=self.frame_spacing,
                                                    mode='HORIZONTAL', should_change_color=True, change_time=0.5, 
                                                    width=None, height=None, shiny_flow_effect=False, color_chain=("#ff4040", "#5757ff"))
        self.cg_booster_borderline.set_on_screen()

    def add_padding(self):
        """
        Defines all paddings of the widgets.
        """
        #self.init_frame.grid_configure(ipady=100, ipadx=100)
        self.init_spacing.grid_configure(pady=20)
        self.init_label_title.grid_configure(pady=30)
        self.confirm_frame.grid_configure(pady=10)

        self.frame_spacing.grid_configure(padx=30)

        #self.train_frame.grid_configure(ipady=100, ipadx=100)
        self.train_label_title.grid_configure(pady=30)
        self.train_drill_next_name.grid_configure(pady=0)
        self.train_drill_start.grid_configure(ipady=15, ipadx=30)
        self.train_predict.grid_configure(ipady=15, ipadx=30)    
        self.train_reset.grid_configure(ipady=15, ipadx=30) 

        self.train_spacing.grid_configure(pady=50)

        # Adding Amounts
        self.drill_add_amounts_label.grid_configure(pady=10)
        self.drill_add_amounts_person1_label.grid_configure(padx=10)

    def weighting(self):
        """
        Defines all weightings of the widgets.

        The weighting defines, how intensive the grid-entry fit, if the size of the screen is changing.
        """
        for n in range(self.max_rows):
            self.grid_rowconfigure(n, weight=1, minsize=20) #20
        
        for n in range(self.max_columns):
            self.grid_columnconfigure(n, weight=1, minsize=50) # 50

        self.init_frame.columnconfigure(0, minsize=50)
        self.init_frame.columnconfigure(4, minsize=50)
        self.init_frame.rowconfigure(22, minsize=50)
        # adding frames cols and rows configs
        for n in range(1, 8):
            self.train_frame.grid_rowconfigure(n, weight=1, minsize=50)
        for n in range(3):
            self.train_frame.grid_columnconfigure(n, weight=1, minsize=50)

        self.train_frame.grid_columnconfigure(0, minsize=50)
        self.train_frame.grid_columnconfigure(5, minsize=50)  #4
        self.train_frame.grid_rowconfigure(7+2, minsize=50)

        # spacing betrween two names
        self.train_frame.grid_rowconfigure(3, weight=1, minsize=20)
        self.train_frame.grid_rowconfigure(4, weight=1, minsize=20)

        self.train_frame.grid_rowconfigure(5, weight=1, minsize=70)

        # spacing from bottom
        self.train_frame.grid_rowconfigure(9, weight=1, minsize=60)
    
    def show(self):
        """
        Shows the Train-Screen.

        For that the screen will be packed and the gradient-color will be started.
        """
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.cg_booster_borderline.start()

    def hide(self):
        """
        Hides the Train-Screen.

        For that the screen will be unpacked and the gradient-color stripes will be stopped.
        """
        self.pack_forget()
        self.cg_booster_borderline.stop()

    def event_back(self):
        """
        Loads the Startmenu and resets the train-screen and the predict-screen.

        Called by clicking the back-button.
        """
        self.root.terminal.add_event('reset-train')
        self.event_reset_button()
        self.root.load_screen_main_menu(self)
        self.train_drill_next_name.configure(text="?")
        self.root.reset_predict()

    # detect changes
    def init_changes(self, var, indx, mode):
        """
        Creates the confitm-button by the meta-data area.

        Called if detected changes.

        Params automatically sets by Tkinter and are not relevant and not used.
        """
        self.init_confirm.grid(row=0, column=0)
        self.root.set_min()

    def delete_last_btn_change(self, state):
        """
        Disabled or enabled the button to delete the last drill.

        :param state: Sets the state of the delete-last-button ('disabled' or 'enabled' available)
        :type state: str
        """
        self.train_delete_last.configure(state=state)

    def change_train_person(self, person):
        """
        Shows the persons-name who should drill at next.

        :param person: The person who should drill at next.
        :type person: str
        """
        self.train_drill_next_name.config(text=person)

    def start_button_change(self, state):
        """
        Disabled or enabled the button to start a drill.

        :param state: Sets the state of the start-drill-button ('disabled' or 'enabled' available)
        :type state: str
        """
        self.train_drill_start.config(state=state)

    def event_confirm_init_change(self):
        """
        Checks if the meta-data are valid and if yes, shows the person who should drill at next.
        """
        enough_amount = int(self.var_person1_drill_amount.get()) > 0 and int(self.var_person2_drill_amount.get()) > 0
        if self.var_person1_name.get() != self.var_person2_name.get() and enough_amount:
            self.root.focus()    # set focus on root
            self.train_drill_amount_person1.configure(text=f"{self.var_person1_name.get()}: {self.var_person1_drill_amount.get()}")
            self.train_drill_amount_person2.configure(text=f"{self.var_person2_name.get()}: {self.var_person2_drill_amount.get()}")
            self.drill_add_amounts_person1_label.configure(text=f"{self.var_person1_name.get()}")
            self.drill_add_amounts_person2_label.configure(text=f"{self.var_person2_name.get()}")
            self.train_drill_start.configure(state='enabled')
            self.init_confirm.grid_forget()
            #self.root.set_min()
            #self.init_confirm.grid_remove()    # memorize the configurations
            # beende Software, falls sie läuft (nur eine)
            # Terminal should create Files and Directories
            person1 = {'operator':self.var_person1_name.get(),
                        'amount':self.var_person1_drill_amount.get(),
                        'drillType':self.var_person1_drill_type.get(),
                        'boreholeSize':self.var_person1_drill_size.get(),
                        'gear':self.var_person1_drill_gear.get(),
                        'material':self.var_person1_material.get(),
                        'batteryLevel':self.var_person1_akku.get()}

            person2 = {'operator':self.var_person2_name.get(),
                        'amount':self.var_person2_drill_amount.get(),
                        'drillType':self.var_person2_drill_type.get(),
                        'boreholeSize':self.var_person2_drill_size.get(),
                        'gear':self.var_person2_drill_gear.get(),
                        'material':self.var_person2_material.get(),
                        'batteryLevel':self.var_person2_akku.get()}
            
            self.root.terminal.add_event("train-drill", (person1, person2))
            # Update Train 
            # Start software -> one Software starts direct by beginning, the other now

    def event_confirm_add(self):
        """
        Add new data-amount. 
        """
        self.root.focus()    # set focus on root
        add_amount_person1 = self.var_add_person1_amount.get()
        add_amount_person2 = self.var_add_person2_amount.get()
        self.root.terminal.add_event('add-amount', (add_amount_person1, add_amount_person2))
        self.train_predict.configure(state='disabled')

    def event_start_button(self):
        """
        Starts or stops a drill.

        The method takes care of the state of the buttons. (While drilling the user should not be able to leave the screen or delete the last drill)
        """
        if self.train_drill_start['text'] == "Start":
            self.root.terminal.add_event("start")
            self.train_reset.configure(state='disabled')
            self.button_back.configure(state='disabled')
            self.drill_add_person1_entry.configure(state='disabled')
            self.drill_add_person2_entry.configure(state='disabled')
            self.add_confirm.configure(state='disabled')
        elif self.train_drill_start['text'] == "Stopp":
            self.root.terminal.add_event("stop")
            self.train_reset.configure(state='enabled')
            self.button_back.configure(state='enabled')
            self.drill_add_person1_entry.configure(state='enabled')
            self.drill_add_person2_entry.configure(state='enabled')
            self.add_confirm.configure(state='enabled')

        self.change_init_state(state='disabled')

    def event_delete_last_button(self):
        """
        Communicates with the Terminal to delete the last data-entry.
        """
        self.root.terminal.add_event('delete-last')
        self.train_predict.configure(state='disabled')

    def event_reset_button(self):
        """
        Sets the screen and all his content to a initialized state.
        """
        self.train_drill_start.configure(state="disabled")
        self.train_reset.configure(state="disabled")
        self.train_delete_last.configure(state="disabled")
        self.root.terminal.add_event('reset-train')
        self.train_drill_next_name.configure(text="?")
        self.change_init_state('enabled')

        self.var_person1_name.set("Person1")
        self.var_person1_drill_amount.set("10")
        self.var_person1_material.set("wood-eiche")
        self.var_person1_drill_type.set("universal")
        self.var_person1_drill_gear.set("2")
        self.var_person1_drill_size.set("4")
        self.var_person1_akku.set("normal")

        self.var_person2_name.set("Person2")
        self.var_person2_drill_amount.set("10")
        self.var_person2_material.set("wood-eiche")
        self.var_person2_drill_type.set("universal")
        self.var_person2_drill_gear.set("2")
        self.var_person2_drill_size.set("4")
        self.var_person2_akku.set("normal")

        self.train_predict.configure(state='disabled')

        self.train_drill_amount_person1.configure(text=f"{self.var_person1_name.get()}: {self.var_person1_drill_amount.get()}")
        self.train_drill_amount_person2.configure(text=f"{self.var_person2_name.get()}: {self.var_person1_drill_amount.get()}")

        self.train_runtime.configure(text="Zeit: -")

        self.var_add_person1_amount.set("5")
        self.var_add_person2_amount.set("5")
        self.drill_add_person1_entry.configure(state='disabled')
        self.drill_add_person2_entry.configure(state='disabled')
        self.add_confirm.configure(state='disabled')

        self.start_time = None
        self.is_drilling = False

    def event_predict_button(self):
        """
        Loads the predict-screen.

        Only apears, if there are no more data-drills left.
        """
        self.root.terminal.add_event("predict-load")
        self.root.load_screen_predict(self)

    def change_init_state(self, state='disabled'):
        """
        Changes the availability of the widgets of the meta-data area.

        :param state: State in which the widgets should be changed ('disabled' or 'enabled' available)
        :type state: str
        """
        self.init_person_1_name.configure(state=state)
        self.init_person_1_drill_amount.configure(state=state)
        self.init_person_1_material.configure(state=state)
        self.init_person_1_drill_type.configure(state=state)
        self.init_person_1_drill_gear.configure(state=state)
        self.init_person_1_drill_size.configure(state=state)
        self.init_person_1_akku.configure(state=state)

        self.init_person_2_name.configure(state=state)
        self.init_person_2_drill_amount.configure(state=state)
        self.init_person_2_material.configure(state=state)
        self.init_person_2_drill_type.configure(state=state)
        self.init_person_2_drill_gear.configure(state=state)
        self.init_person_2_drill_size.configure(state=state)
        self.init_person_2_akku.configure(state=state)

        self.init_confirm.configure(state=state)

    def drill_amount_change(self, amount_person_1, amount_person_2):
        """
        Updates the amount-label.

        :param amount_person_1: Drill-Amount of Person 1 which is left.
        :type amount_person_1: str or int
        :param amount_person_2: Drill-Amount of Person 2 which is left.
        :type amount_person_2: str or int
        """
        self.train_drill_amount_person1.configure(text=f"{self.var_person1_name.get()}: {amount_person_1}")
        self.train_drill_amount_person2.configure(text=f"{self.var_person2_name.get()}: {amount_person_2}")
        if f"{amount_person_1}" != "0" or f"{amount_person_2}" != "0":
            self.train_drill_start.configure(state='enabled')

    def drill_starts(self):
        """
        Changes the start-button text to Stopp and starts the timer.
        """
        self.train_drill_start['text'] = "Stopp"
        self.start_time = time()
        self.root.after(100, self.change_run_time)
        self.is_drilling = True

    def drill_ends(self, amount_person_1:int, amount_person_2:int):
        """
        Changes the start-button text to Start and update the drill-amount of both persons.

        :param amount_person_1: Drill-Amount of Person 1 which is left
        :type amount_person_1: int
        :param amount_person_2: Drill-Amount of Person 2 which is left
        :type amount_person_2: int
        """
        self.train_drill_start['text'] = "Start"
        self.is_drilling = False
        self.train_drill_amount_person1.configure(text=f"{self.var_person1_name.get()}: {amount_person_1}")
        self.train_drill_amount_person2.configure(text=f"{self.var_person2_name.get()}: {amount_person_2}")
        if amount_person_1 == 0 and amount_person_2 == 0:
            self.train_drill_start.configure(state="disabled")
            self.train_predict.configure(state='enabled')

    def stop_time(self):
        """
        Stops the timer.
        """
        self.is_drilling = False

    def change_run_time(self):
        """
        Logic of timer.

        Updates runned time and calls his self in 0.1s.
        """
        if self.is_drilling:
            runtime = time() - self.start_time
            self.train_runtime.configure(text=f"Zeit: {round(runtime, 2)}")
            self.root.after(100, self.change_run_time)


###############################################
############   Predict_Screen    ##############
###############################################
class Predict_Window(Screen):
    """
    Contains the logic and all widgets from predict-screen. 

    Included the show of results, add-drill-amount area and the ml-model-selection area.

    This Screen used to collect predict-data, predict these data and show the results of them.

    :param root: Root-Widget. Needed for communicate with :class:~anoog.automation.controller.Terminal.
    :param root: tk.Tk
    :param kwargs: Key, Value arguments for the Widget (relatively unrelevant)
    :type kwargs: dict
    """
    def __init__(self, root, **kwargs):
        """
        Constructor method
        """
        super().__init__(root, **kwargs)
        self.min = (1200, 700)
        self.root = root

        self.max_rows = 1 + 3 + 1
        self.max_columns = 1 + 1 + 1    #between the widgets, right has span 2

        self.out_block_color = '#c6d7ff'

        self.is_drilling = False
        self.start_time = None
        self.models = ["RandomForest", "Voting Classifier", "Naive Bayes", "KNN", "SVC", "Ada Boost", "Logistic Regression"]
        self.model_params = ["predefined", "auto"]
        self.model_norm = ["normalize", "not normalize"]

        self.create_widgets()
        self.weighting()
        self.add_padding()
        self.hide()

    def create_widgets(self):
        """
        Method to create all important Widgets of the Predict-Screen.
        """
        # Back Button
        self.button_back = ttk.Button(self, text="<", command=self.event_back, takefocus = 0)
        self.button_back.grid(row=0, column=0, sticky="nw")

        # Train Model Selector
        self.model_frame = ttk.Frame(self, borderwidth=0, relief="solid")
        self.model_frame.grid(row=1, column=2)
        self.model_frame_bg = Color_Gradient_Booster(root=self.root, parent=self.model_frame, 
                                                    mode='random', should_change_color=True,
                                                    color_chain='random')
        #self.model_frame_bg.place(relx=0.1, rely=0, relwidth=0.8, relheight=0.8)

            # model selection
        self.var_model = tk.StringVar()
        self.var_model.set(self.models[0])
        self.combobox_model = ttk.Combobox(self.model_frame, textvar=self.var_model, values=self.models, state="readonly", takefocus = 0)
        self.combobox_model.grid(row=1, column=1)
            # model param selection
        self.var_model_param = tk.StringVar()
        self.var_model_param.set(self.model_params[0])
        self.combobox_model_param = ttk.Combobox(self.model_frame, textvar=self.var_model_param, values=self.model_params, state="readonly", takefocus = 0)
        self.combobox_model_param.grid(row=2, column=1)
            # model normalize
        self.var_model_norm = tk.StringVar()
        self.var_model_norm.set(self.model_norm[0])
        self.combobox_model_norm = ttk.Combobox(self.model_frame, textvar=self.var_model_norm, values=self.model_norm, state="readonly", takefocus = 0)
        self.combobox_model_norm.grid(row=3, column=1)

        # Predict Output Block
        self.predict_out_frame_bg = ttk.Frame(self, borderwidth=0, relief="solid")
        self.predict_out_frame_bg.grid(row=1, column=1, sticky="nwse")

        self.cg_booster_border = Color_Gradient_Booster(root=self.root, parent=self.predict_out_frame_bg, 
                                                    mode='random', should_change_color=True,
                                                    color_chain='random')
        self.cg_booster_border.set_on_screen()
        self.cg_booster_border.set_fav_color()

        self.predict_out_frame = ttk.Frame(self.predict_out_frame_bg)
        self.predict_out_frame.place(relx=0.0125, rely=0.025, relwidth=0.975, relheight=0.95)

        self.predict_out_who_drilled = ttk.Label(self.predict_out_frame, text="Es hat gebohrt:", anchor='w', font='Helvetica 14')
        self.predict_out_who_drilled.grid(row=1, column=1, sticky="nwse")
        self.predict_out_who_drilled_answer = ttk.Label(self.predict_out_frame, text="      ?      ", anchor='center', font='Helvetica 16 bold')
        self.predict_out_who_drilled_answer.grid(row=1, column=3, sticky="nwse")

        self.predict_out_how_sure = ttk.Label(self.predict_out_frame, text="Genauigkeit:", anchor='w', font='Helvetica 14')
        self.predict_out_how_sure.grid(row=2, column=1, sticky="nwse")
        self.predict_out_how_sure_answer = ttk.Label(self.predict_out_frame, text="      ?      ", anchor='center', font='Helvetica 16 bold')
        self.predict_out_how_sure_answer.grid(row=2, column=3, sticky="nwse")

        self.predict_out_which_algo = ttk.Label(self.predict_out_frame, text="Verwendeter Algorithmus:", anchor='w', font='Helvetica 14')
        self.predict_out_which_algo.grid(row=3, column=1, sticky="nwse")
        self.predict_out_which_algo_answer = ttk.Label(self.predict_out_frame, text="      ?      ", anchor='center', font='Helvetica 16 bold')
        self.predict_out_which_algo_answer.grid(row=3, column=3, sticky="nwse")

        # Predict Controll Block
        self.predict_in_frame = ttk.Frame(self)
        self.predict_in_frame.grid(row=3, column=1, sticky="nwse")

        self.predict_in_time = ttk.Label(self.predict_in_frame, text="Zeit: -", anchor='n', font='Helvetica 11 bold')
        self.predict_in_time.grid(row=1, column=2, sticky="nwse")
        self.predict_in_amount = ttk.Label(self.predict_in_frame, text="Amount: 0", anchor='n', font='Helvetica 11 bold')
        self.predict_in_amount.grid(row=2, column=2, sticky="nwse")

        self.predict_in_reset = ttk.Button(self.predict_in_frame, text="Neue Person", command=self.event_reset_button, takefocus=0)
        self.predict_in_reset.grid(row=3, column=1, sticky="nwse")
        self.predict_in_reset.configure(state='disabled')
        self.predict_in_start = ttk.Button(self.predict_in_frame, text="Start Bohrung", command=self.event_start_button, takefocus=0)
        self.predict_in_start.grid(row=3, column=2, sticky="nwse")
        self.predict_in_predict = ttk.Button(self.predict_in_frame, text="Predict", command=self.event_predict_button, takefocus=0)
        self.predict_in_predict.grid(row=3, column=3, sticky="nwse")
        self.predict_in_predict.configure(state='disabled')

        self.predict_in_delete_last_frame = ttk.Frame(self.predict_in_frame)
        self.predict_in_delete_last_frame.grid(row=4, column=2, sticky="e")
        self.predict_in_delete_last = ttk.Button(self.predict_in_delete_last_frame, text="Lösche letzte Bohrung", command=self.event_delete_last_button, takefocus=0)
        self.predict_in_delete_last.grid(row=0, column=0)
        self.predict_in_delete_last.configure(state='disabled')

    def add_padding(self):
        """
        Defines all paddings of the widgets.
        """
        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)

        self.combobox_model.grid_configure(pady=10)
        self.combobox_model_norm.grid_configure(pady=10)    

    def weighting(self):
        """
        Defines all weightings of the widgets.

        The weighting defines, how intensive the grid-entry fit, if the size of the screen is changing.
        """
        for n in range(self.max_rows):
            self.grid_rowconfigure(n, weight=1, minsize=20)
        self.grid_rowconfigure(1, weight=1, minsize=250)
        self.grid_rowconfigure(3, weight=1, minsize=100)
        
        for n in range(self.max_columns):
            self.grid_columnconfigure(n, weight=1, minsize=50) 
        self.grid_columnconfigure(1, weight=1, minsize=150) 

        self.grid_columnconfigure(1, weight=1, minsize=int(self.winfo_width()*0.35)+50)

        # Model Selection Block
        for n in range(4):
            self.predict_out_frame.grid_rowconfigure(n, weight=1, minsize=20)
        
        for n in range(3):
            self.predict_out_frame.grid_columnconfigure(n, weight=1, minsize=50)

        # Output Block
        for n in range(5):
            self.predict_out_frame.grid_rowconfigure(n, weight=1, minsize=20)
        
        for n in range(5):
            self.predict_out_frame.grid_columnconfigure(n, weight=1, minsize=50)

        # Control Block
        for n in range(6):
            self.predict_in_frame.grid_rowconfigure(n, weight=1, minsize=20)
        
        for n in range(5):
            self.predict_in_frame.grid_columnconfigure(n, weight=1, minsize=50)
    
    def show(self):
        """
        Shows the Predict-Screen.

        For that the screen will be packed and the gradient-color will be started.
        """
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.cg_booster_border.start()
        self.model_frame_bg.start()

    def hide(self):
        """
        Hides the Predict-Screen.

        For that the screen will be unpacked and the gradient-color will be stopped.
        """
        self.pack_forget()
        self.cg_booster_border.stop()

    def set_amount(self, amount):
        """
        Sets the amount to the given value.

        :param amount: Amount of drills
        :type amount: int or str
        """
        self.predict_in_amount.configure(text=f'Amount: {amount}')

    def event_back(self):
        """
        Loads the Train-Screen.

        Event called by clicking the back-button.
        """
        self.root.load_screen_train(self)
        self.root.terminal.add_event("from-predict-to-train")
        self.cg_booster_border.stop()
        self.model_frame_bg.stop()

    def event_start_button(self):
        """
        Starts or stops a drill.

        The method takes care of the state of the buttons. (While drilling the user should not be able to leave the screen or delete the last drill)
        """
        if self.predict_in_start['text'] == "Start Bohrung":
            self.root.terminal.add_event("start")
            self.predict_in_delete_last.configure(state='disabled')
            self.predict_in_reset.configure(state='disabled')
            self.predict_in_predict.configure(state='disabled')
        elif self.predict_in_start['text'] == "Stopp Bohrung":
            self.root.terminal.add_event("stop")
            self.predict_in_delete_last.configure(state='enabled')
            self.predict_in_reset.configure(state='enabled')
            self.predict_in_predict.configure(state='enabled')

    def event_reset_button(self):
        """
        Prepares for a new person to predict.

        Delets the old predict-data-entries and delets the old results.

        Sends an Event to the Terminal.
        """
        self.root.terminal.add_event('reset-predict')
        self.reset()

    def event_predict_button(self):
        """
        Trains the selected ML-Model with the train-data, predict the new data with the trained model and show the results of that.
        
        Sends an Event to the Terminal.
        """
        self.root.terminal.add_event('predict', (self.var_model.get(), self.var_model_param.get(), self.var_model_norm.get()))
        self.model_changed = False

    def event_delete_last_button(self):
        """
        Deletes the last predict-drill-data-entry.

        Sends an Event to the Terminal.
        """
        self.root.terminal.add_event('delete-last-predict-drill')

    def reset(self):
        """
        Sets all widgets and contents of the initilized value.
        """
        self.predict_out_who_drilled.configure(text="Es hat gebohrt:")
        self.predict_out_who_drilled_answer.configure(text="      ?      ")
        self.predict_out_how_sure.configure(text="Genauigkeit:")
        self.predict_out_how_sure_answer.configure(text="      ?      ")
        self.predict_out_which_algo.configure(text="Verwendeter Algorithmus:")
        self.predict_out_which_algo_answer.configure(text="      ?      ")

        self.predict_in_amount.configure(text=f'Amount: 0')
        self.predict_in_time.configure(text=f"Zeit: -")

        self.predict_in_delete_last.configure(state='disabled')
        self.predict_in_reset.configure(state='disabled')
        self.predict_in_predict.configure(state='disabled')

        self.is_drilling = False
        self.start_time = None
        self.var_model.set(self.models[0])
        self.var_model_param.set(self.model_params[0])
        self.var_model_norm.set(self.model_norm[0])

    def drill_starts(self):
        """
        Changes the text of the start-button to Stopp Bohrung and starts the timer.
        """
        self.predict_in_start['text'] = "Stopp Bohrung"
        self.start_time = time()
        self.root.after(100, self.change_run_time)
        self.is_drilling = True

    def drill_ends(self):
        """
        Changes the text of the start-button to Start Bohrung and stops the timer.
        """
        self.predict_in_start['text'] = "Start Bohrung"
        self.is_drilling = False

    def stop_time(self):
        """
        Stops the timer.
        """
        self.is_drilling = False

    def delete_last_btn_change(self, state):
        """
        Deletes the last predict-data-entry.

        Sends an Event to the Terminal.

        :param state: State in which the delete-last-button should be changed ('disabled' or 'enabled' available)
        :type state: str
        """
        self.predict_in_delete_last.configure(state=state)

    def show_result(self, who, how, what):
        """
        Shows the result of the prediction.

        :param who: Who is the prediction of the 2 persons.
        :type who: str
        :param who: How sure is the model (percentage).
        :type who: int
        :param who: Which algorithm used for this prediction.
        :type who: str
        """
        self.predict_out_who_drilled_answer.configure(text=f"{who}")
        self.predict_out_how_sure_answer.configure(text=f"{round(how, 2)}%")
        self.predict_out_which_algo_answer.configure(text=f"{what}")

    def draw_result(self, img_path):
        """
        Draws a plot of the result.


        (Not in use)

        :param img_path: Path to the image to load.
        :type img_path: str
        """
        self.image = Image.open(img_path)
        self.image = self.image.resize((int(self.winfo_width()*0.35), int(self.winfo_height()*0.45)), Image.ANTIALIAS)

        self.tk_image = ImageTk.PhotoImage(self.image)
        self.predict_out_bar_chart.configure(text='', image=self.tk_image)

    def start_button_change(self, state):
        """
        Changes the state of the start-button.

        :param state: State in which the start-button should be changed ('disabled' or 'enabled' available)
        :type state: str
        """
        self.train_drill_start.config(state=state)

    def change_run_time(self):
        """
        Logic of timer.

        Updates runned time and calls his self in 0.1s.
        """
        if self.is_drilling:
            runtime = time() - self.start_time
            self.predict_in_time.configure(text=f"Zeit: {round(runtime, 2)}")
            self.root.after(100, self.change_run_time)


###############################################
############   Credits_Screen    ##############
###############################################
class Credits_Window(Screen):
    """
    Contains the logic and all widgets from credits-screen. 

    This Screen used to show all contributers of this project.

    :param root: Root-Widget. Needed for communicate with :class:~anoog.automation.controller.Terminal.
    :param root: tk.Tk
    :param kwargs: Key, Value arguments for the Widget (relatively unrelevant)
    :type kwargs: dict
    """
    def __init__(self, root, **kwargs):
        """
        Constructor method
        """
        super().__init__(root, **kwargs)
        self.min = (1200, 700)

        self.max_rows = 3
        self.max_columns = 3
        
        self.startpoint = 1.3
        
        self.create_widgets()
        self.weighting()
        self.add_padding()
        self.hide()

        

    def create_widgets(self):
        """
        Method to create all important Widgets of the Credit-Screen.
        """
        # Back Button
        self.button_back = ttk.Button(self, text="<", command=self.event_back, takefocus = 0)
        self.button_back.grid(row=0, column=0, sticky="nw")

        self.entwickler = ttk.Label(self, text="Entwickler", anchor='n', font='Helvetica 36 bold')
        self.tobia_1 = ttk.Label(self, text="Tobia Ippolito", anchor='n', font='Helvetica 18 bold')
        self.syon_1 = ttk.Label(self, text="Syon Kadkade", anchor='n', font='Helvetica 18 bold')
        self.vadim_1 = ttk.Label(self, text="Vadim Korzev", anchor='n', font='Helvetica 18 bold')

        self.gui = ttk.Label(self, text="GUI", anchor='n', font='Helvetica 36 bold')
        self.tobia_2 = ttk.Label(self, text="Tobia Ippolito", anchor='n', font='Helvetica 18 bold')

        self.automation = ttk.Label(self, text="Automation", anchor='n', font='Helvetica 36 bold')
        self.tobia_3 = ttk.Label(self, text="Tobia Ippolito", anchor='n', font='Helvetica 18 bold')

        self.feature_extraction = ttk.Label(self, text="Feature Extraction", anchor='n', font='Helvetica 36 bold')
        self.vadim_2 = ttk.Label(self, text="Vadim Korzev", anchor='n', font='Helvetica 18 bold')

        self.feature_selection = ttk.Label(self, text="Feature Selection", anchor='n', font='Helvetica 36 bold')
        self.syon_2 = ttk.Label(self, text="Syon Kadkade", anchor='n', font='Helvetica 18 bold')

        self.ai = ttk.Label(self, text="AI-Model Expert", anchor='n', font='Helvetica 36 bold')
        self.tobia_4 = ttk.Label(self, text="Tobia Ippolito", anchor='n', font='Helvetica 18 bold')

        self.schnitt = ttk.Label(self, text="Kamera und Schnitt", anchor='n', font='Helvetica 36 bold')
        self.matteo_1 = ttk.Label(self, text="Matteo Ippolito", anchor='n', font='Helvetica 18 bold')
        self.vadim_3 = ttk.Label(self, text="Vadim Korzev", anchor='n', font='Helvetica 18 bold')

        self.schauspieler = ttk.Label(self, text="Schauspieler", anchor='n', font='Helvetica 36 bold')
        self.tobia_5 = ttk.Label(self, text="Tobia Ippolito", anchor='n', font='Helvetica 18 bold')
        self.syon_3 = ttk.Label(self, text="Syon Kadkade", anchor='n', font='Helvetica 18 bold')

        #self.code_doku = ttk.Label(self, text="Code-Dokumentation", anchor='n', font='Helvetica 36 bold')
        #self.tobia_6 = ttk.Label(self, text="Tobia Ippolito", anchor='n', font='Helvetica 18 bold')

        self.special_thanks = ttk.Label(self, text="Special Thanks", anchor='n', font='Helvetica 36 bold')
        self.daniela_1 = ttk.Label(self, text="Prof. Dr. Daniela Oelke", anchor='n', font='Helvetica 18 bold')
        self.stefan_1 = ttk.Label(self, text="Stefan Glaser", anchor='n', font='Helvetica 18 bold')
        self.matteo_2 = ttk.Label(self, text="Matteo Ippolito", anchor='n', font='Helvetica 18 bold')


    def add_padding(self):
        """
        Defines all paddings of the widgets.
        """
        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)

    def weighting(self):
        """
        Defines all weightings of the widgets.

        The weighting defines, how intensive the grid-entry fit, if the size of the screen is changing.
        """
        for n in range(self.max_rows):
            self.grid_rowconfigure(n, weight=1, minsize=20) #20
        
        for n in range(self.max_columns):
            self.grid_columnconfigure(n, weight=1, minsize=50) # 50
    
    def show(self):
        """
        Shows the Credits-Screen.

        For that the screen will be packed and the animation will be started.
        """
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.should_run = True
        self.startpoint = 4.8
        self.update_show()

    def update_show(self):
        """
        Updates the position of the labels.

        With that method called many times, ended in a flow effect.
        """
        self.moving = 0.00005
        self.startpoint -= self.moving
       
        self.entwickler.place(relx=0.42, rely=self.startpoint-3.97)
        self.tobia_1.place(relx=0.45, rely=self.startpoint-3.8)
        self.syon_1.place(relx=0.45, rely=self.startpoint-3.7)
        self.vadim_1.place(relx=0.45, rely=self.startpoint-3.6)

        self.gui.place(relx=0.47, rely=self.startpoint-3.37)
        self.tobia_2.place(relx=0.45, rely=self.startpoint-3.2)

        self.automation.place(relx=0.41, rely=self.startpoint-2.97)
        self.tobia_3.place(relx=0.45, rely=self.startpoint-2.8)

        self.feature_extraction.place(relx=0.35, rely=self.startpoint-2.57)
        self.vadim_2.place(relx=0.45, rely=self.startpoint-2.4)

        self.feature_selection.place(relx=0.36, rely=self.startpoint-2.17)
        self.syon_2.place(relx=0.45, rely=self.startpoint-2.0)

        self.ai.place(relx=0.37, rely=self.startpoint-1.77)
        self.tobia_4.place(relx=0.45, rely=self.startpoint-1.6)

        self.schnitt.place(relx=0.33, rely=self.startpoint-1.37)
        self.matteo_1.place(relx=0.44, rely=self.startpoint-1.2)
        self.vadim_3.place(relx=0.45, rely=self.startpoint-1.1)
        
        self.schauspieler.place(relx=0.39, rely=self.startpoint-0.87)
        self.tobia_5.place(relx=0.45, rely=self.startpoint-0.7)
        self.syon_3.place(relx=0.45, rely=self.startpoint-0.6)

        self.special_thanks.place(relx=0.37, rely=self.startpoint-0.37)
        self.daniela_1.place(relx=0.4, rely=self.startpoint-0.2)
        self.stefan_1.place(relx=0.45, rely=self.startpoint-0.1)
        self.matteo_2.place(relx=0.44, rely=self.startpoint)

        if self.should_run:
            self.root.after(1, self.update_show)

    def hide(self):
        """
        Hides the Credits-Screen.

        For that the screen will be unpacked and the animation will be stopped.
        """
        self.pack_forget()
        self.should_run = False

    def event_back(self):
        """
        Load the start-menu.
        """
        self.root.load_screen_main_menu(self)


###############################################
#################   Run    ####################
###############################################
def run(data_path="src/DrillDummy/testdata", drillcapture_path="src/DrillDummy/drillcapture.exe", 
                                drilldriver_path="src/DrillDummy/drilldriver.exe", op=op.WINDOWS, 
                                path_to_project="./"):
    """
    Creates the GUI and starts the whole Application.

    :param data-path: A path to the location where the data will be stored (there will be created a new folder with the current date)
    :type data-path: str, optional
    :param drillcapture_path: A path to the location where the Drillcapture program executable is stored.
    :type drillcapture_path: str, optional
    :param drilldriver_path: A path to the location where the Drilldriver program executable is stored.
    :type drilldriver_path: str, optional
    :param op: Defines on which operating system the program should run.
    :type op: :class:`~anoog.automation.py_exe_interface.op`, optional
    :param path_to_project: A path to the location to the Project folder.
    :type path_to_project: str, optional
    """
    GUI_App().run(data_path, drillcapture_path, drilldriver_path, op, path_to_project)


