from queue import Queue
from threading import Thread
import abc
from time import time

from PIL import Image, ImageTk

from .controller import Terminal
from .py_exe_interface import op
from .bg_booster import Color_Gradient_Booster

import tkinter as tk
from tkinter import font
from tkinter import ttk
from ttkthemes import ThemedStyle


THEMES = ['smog', 'ubuntu', 'scidgrey', 'scidblue', 
          'scidmint', 'alt', 'adapta', 'vista', 
          'default', 'classic', 'winxpblue', 'scidpurple', 
          'keramik', 'radiance', 'yaru', 'clam', 
          'winnative', 'scidsand', 'breeze', 'plastik', 
          'scidgreen', 'arc', 'equilux', 'clearlooks', 
          'blue', 'kroc', 'itft1', 'black', 
          'scidpink', 'aquativo', 'xpnative', 'elegance']

# ladet die verschiedenen Widgets
# ein Main-Wudget = Zustand
class GUI_App(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_img = None
        self.cur_screen = None

        # Theme
        # breeze, breeze-dark, awlight, awdark, arc, equilux, yaru, aqua, adapta
        self.style = ThemedStyle(self)
        self.set_theme("equilux")

        # alle Main-Widgets erszeugen...
        self.screen_main_menu = Menu(self)
        self.screen_configuration = Configuration(self)
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
        self.bind('<Button-1>', self.event_left_mouse_pressed)
        self.bind('<Button-1>', self.event_left_mouse_released)

        self.events = Queue()
        self.EVENT = {'drill-person':self.screen_train.change_train_person, 'drill-starts':self.screen_train.drill_starts, 
                        'drill-ends':self.screen_train.drill_ends, 'delete-last':self.screen_train.delete_last_btn_change,
                        'drill-amount-change':self.screen_train.drill_amount_change, 'block':self.block, 'stop-time':self.stop_time,
                        'start-change':self.start_button,
                        'set-amount-predict':self.screen_predict.set_amount, 'predict-drill-starts':self.screen_predict.drill_starts,
                        'predict-drill-ends':self.screen_predict.drill_ends, 'delete-last-predict':self.screen_predict.delete_last_btn_change,
                        'predict-result':self.screen_predict.show_result, 'draw-result':self.screen_predict.draw_result}

    def set_theme(self, name):
        if name in THEMES:
            self.style.theme_use(name)
            self.set_min()
        
    def run(self, data_path, drillcapture_path, drilldriver_path, op):
        self.terminal = Terminal(self, data_path=data_path, drillcapture_path=drillcapture_path, drilldriver_path=drilldriver_path, op=op)
        self.thread_terminal = Thread(target=self.terminal.run)
        self.thread_terminal.start()

        # GUI starting
        self.mainloop()

    def close(self):
        self.terminal.add_event('exit', '')
        self.quit()

    # kann hierbei direkt ausgeführt werden!
    def add_event(self, event_name, *additions):
        print("Event is by GUI")
        #event = (event_name, *additions)
        #self.events.put(event)
        if len(additions) > 0:
            self.EVENT[event_name](*additions)
        else:
            self.EVENT[event_name]()

    def load_theme(self, name):
        if name in THEMES:
            self.set_theme(name)

    def load_screen_main_menu(self, from_widget):
        self.cur_screen = self.screen_main_menu
        from_widget.hide()
        self.screen_main_menu.show()
        # set new minimum
        self.set_min()

    def load_screen_configuration(self, from_widget):
        self.cur_screen = self.screen_configuration
        from_widget.hide()
        self.screen_configuration.show()
        self.set_min()

    def load_screen_train(self, from_widget):
        self.cur_screen = self.screen_train
        from_widget.hide()
        self.screen_train.show()
        self.set_min()
        self.terminal.add_event('start-drilldriver')

    def load_screen_predict(self, from_widget):
        self.cur_screen = self.screen_predict
        from_widget.hide()
        self.screen_predict.show()
        self.set_min()

    def reset_predict(self):
        self.screen_predict.event_reset_button()

    def load_screen_credits(self, from_widget):
        self.cur_screen = self.screen_credits
        from_widget.hide()
        self.screen_credits.show()
        self.set_min()
        
    def set_min(self):
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
        size_changed = self.old_size[0] != self.winfo_width() or self.old_size[1] != self.winfo_height()
        if self.bg_img != None and self.bg_img != "" and size_changed and self.mouse_not_hold:
            print("HOOOOOOOHOOO")
            self.old_size = (self.winfo_width(), self.winfo_height())
            self.image = Image.open(self.bg_img)
            self.image = self.image.resize((self.winfo_width(), self.winfo_height()), Image.ANTIALIAS)

            self.tk_image = ImageTk.PhotoImage(self.image)

            self.screen_configuration.resize_bg(self.tk_image)
            self.screen_main_menu.resize_bg(self.tk_image)
            self.screen_train.resize_bg(self.tk_image)

    # dont works -> when resize the window this event dont call
    def event_left_mouse_pressed(self, event):
        self.mouse_not_hold = False

    # dont works -> when resize the window this event dont call
    def event_left_mouse_released(self, event):
        self.mouse_not_hold = True

    def event_space(self):
        if self.cur_screen == self.screen_train:
            self.screen_train.event_start_button()
        elif self.cur_screen == self.screen_predict:
            self.screen_predict.event_start_button()

    def stop_time(self):
        if self.cur_screen == self.screen_train:
            self.screen_train.stop_time()
        elif self.cur_screen == self.screen_predict:
            self.screen_predict.stop_time()

    def start_button(self, state):
        if self.cur_screen == self.screen_train:
            self.screen_train.start_button_change(state)
        elif self.cur_screen == self.screen_predict:
            self.screen_predict.start_button_change(state)

    def block(self, state:bool):
        # not implemented yet
        if self.cur_screen == self.screen_train:
            pass
            #self.screen_train.block(state)
        elif self.cur_screen == self.screen_predict:
            pass
            #self.screen_predict.block(state)


###############################################
###############    Screen    ##################
###############################################
class Screen(ttk.Frame, abc.ABC):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.root = root

        self.min = (200, 200)

        self.label_bg = ttk.Label(self)
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

    def resize_bg(self, img):
        #self.label_bg.place_forget()
        self.label_bg.configure(image=img)
        #self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

    def set_bg(self, img):
        #self.label_bg.place_forget()
        self.label_bg.configure(image=img)
        #self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)


###############################################
#############   Menu_Screen    ################
###############################################
class Menu(Screen):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.min = (500, 400)

        self.max_rows = 4+1
        self.max_columns = 1+2
        self.widget_list = {}
        self.create_widgets()
        self.weighting()
        #self.hide()

    def create_widgets(self):
        # Create Title Label
        self.label_title = ttk.Label(self, text="Wer hat gebohrt?", anchor='center')
        self.label_title.grid(row=0, column=1, sticky='NESW')
        self.widget_list['lable_title'] = self.label_title
        self.label_title.bind('<Configure>', self.event_resize_label)

        # Create Start Button
        self.button_start = ttk.Button(self, text="Start", command=self.event_button_start, takefocus = 0)
        self.button_start.grid(row=1, column=1, sticky='NESW')
        self.widget_list['button_start'] = self.button_start

        # Create Information Button
        self.button_credits = ttk.Button(self, text="Credits", command=self.event_button_credits, takefocus = 0)
        self.button_credits.grid(row=2, column=1, sticky='NESW')
        self.widget_list['button_credits'] = self.button_credits

        # Create Credit Button
        self.button_config = ttk.Button(self, text="Einstellungen", command=self.event_button_config, takefocus = 0)
        self.button_config.grid(row=3, column=1, sticky='NESW')
        self.widget_list['button_config'] = self.button_config

        self.add_padding()

    def add_padding(self):
        for child in self.winfo_children():
            child.grid_configure(padx=70, pady=10)
        self.label_title.grid_configure(padx=10, pady=10)
        #self.grid_rowconfigure(5, minsize=20)

    def weighting(self):
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
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

    def hide(self):
        self.pack_forget()

    def event_button_start(self):
        self.root.load_screen_train(self)

    def event_button_credits(self):
        #self.hide()
        self.root.load_screen_credits(self)

    def event_button_config(self):
        self.root.load_screen_configuration(self)

    def event_resize_label(self, event):
        width = event.widget.winfo_width()
        height = event.widget.winfo_height()
        event.widget.configure(font=font.Font(size=height//5))


###############################################
#############   Train_Screen    ###############
###############################################
class Train_Window(Screen):
    def __init__(self, root, **kwargs):
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
        self.train_spacing.grid(row=6, column=1, columnspan=3)

        self.train_drill_start = ttk.Button(self.train_frame, text="Start", command=self.event_start_button, takefocus = 0)
        self.train_drill_start.grid(row=7, column=3)
        self.train_drill_start.configure(state='disabled')

        self.train_delete_last = ttk.Button(self.train_frame, text="Lösche letzte Bohraufnahme", command=self.event_delete_last_button, takefocus = 0)
        self.train_delete_last.grid(row=8, column=2, columnspan=2, sticky="e")
        self.train_delete_last.configure(state='disabled')

        self.train_reset = ttk.Button(self.train_frame, text="Reset", command=self.event_reset_button, takefocus = 0)
        self.train_reset.grid(row=7, column=1)
        self.train_reset.configure(state='disabled')

        self.train_predict = ttk.Button(self.train_frame, text="Predict", command=self.event_predict_button, takefocus = 0)
        self.train_predict.grid(row=7, column=2)
        self.train_predict.configure(state='disabled')

        self.train_runtime = ttk.Label(self.train_frame, text="Zeit: -", anchor='center', font='Helvetica 10 bold')
        self.train_runtime.grid(row=6, column=3)

        # Drill Amount Adding
        self.drill_amount_adding_frame = ttk.Frame(self.train_frame)
        self.drill_amount_adding_frame.grid(row=10, column=1, columnspan=2)

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
        self.add_confirm.configure(state='disabled')

        # adding
        self.train_frame.grid(row=1, column=3, columnspan=2)

        # Spacing between the two areas
        self.frame_spacing = tk.Frame(self, width=4, height=500)#,bg='#ebcf34')
        self.frame_spacing.grid(row=0, column=2, rowspan=3)
        self.cg_booster_borderline = Color_Gradient_Booster(root=self.root, parent=self.frame_spacing,
                                                    mode='HORIZONTAL', should_change_color=True, change_time=0.5, 
                                                    width=None, height=None, shiny_flow_effect=False, color_chain=("#ff4040", "#5757ff"))
        self.cg_booster_borderline.set_on_screen()
        # FIXME
        #self.cg_booster_borderline.set_fav_colors()

    def add_padding(self):
        #for child in self.winfo_children():
        #    child.grid_configure(padx=10, pady=10)
     
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

        #self.train_spacing.grid_configure(pady=50)

        # Adding Amounts
        self.drill_add_amounts_label.grid_configure(pady=10)
        self.drill_add_amounts_person1_label.grid_configure(padx=10)

    def weighting(self):
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
        self.train_frame.grid_rowconfigure(7, minsize=50)

        # spacing betrween two names
        self.train_frame.grid_rowconfigure(3, weight=1, minsize=20)
        self.train_frame.grid_rowconfigure(4, weight=1, minsize=20)

        self.train_frame.grid_rowconfigure(5, weight=1, minsize=70)

        # spacing from bottom
        self.train_frame.grid_rowconfigure(9, weight=1, minsize=60)
    
    def show(self):
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.cg_booster_borderline.start()

    def hide(self):
        self.pack_forget()
        self.cg_booster_borderline.stop()

    def event_back(self):
        self.root.terminal.add_event('reset-train')
        self.event_reset_button()
        self.root.load_screen_main_menu(self)
        self.train_drill_next_name.configure(text="?")
        self.root.reset_predict()

    # detect changes
    def init_changes(self, var, indx, mode):
        #self.init_confirm.grid(row=20, column=2)
        self.init_confirm.grid(row=0, column=0)
        self.root.set_min()

    def delete_last_btn_change(self, state):
        self.train_delete_last.configure(state=state)

    def change_train_person(self, person):
        self.train_drill_next_name.config(text=person)

    def start_button_change(self, state):
        self.train_drill_start.config(state=state)

    def event_confirm_init_change(self):
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
        self.root.focus()    # set focus on root
        add_amount_person1 = self.var_add_person1_amount.get()
        add_amount_person2 = self.var_add_person2_amount.get()
        self.root.terminal.add_event('add-amount', (add_amount_person1, add_amount_person2))
        self.train_predict.configure(state='disabled')

    def event_start_button(self):
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
        self.root.terminal.add_event('delete-last')
        self.train_predict.configure(state='disabled')

    def event_reset_button(self):
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
        self.root.terminal.add_event("predict-load")
        self.root.load_screen_predict(self)

    def change_init_state(self, state='disabled'):
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
        self.train_drill_amount_person1.configure(text=f"{self.var_person1_name.get()}: {amount_person_1}")
        self.train_drill_amount_person2.configure(text=f"{self.var_person2_name.get()}: {amount_person_2}")
        if f"{amount_person_1}" != "0" and f"{amount_person_2}" != "0":
            self.train_drill_start.configure(state='enabled')

    def drill_starts(self):
        self.train_drill_start['text'] = "Stopp"
        self.start_time = time()
        self.root.after(100, self.change_run_time)
        self.is_drilling = True

    def drill_ends(self, amount_person_1:int, amount_person_2:int):
        self.train_drill_start['text'] = "Start"
        self.is_drilling = False
        self.train_drill_amount_person1.configure(text=f"{self.var_person1_name.get()}: {amount_person_1}")
        self.train_drill_amount_person2.configure(text=f"{self.var_person2_name.get()}: {amount_person_2}")
        if amount_person_1 == 0 and amount_person_2 == 0:
            self.train_drill_start.configure(state="disabled")
            self.train_predict.configure(state='enabled')

    def stop_time(self):
        self.is_drilling = False

    def change_run_time(self):
        if self.is_drilling:
            runtime = time() - self.start_time
            self.train_runtime.configure(text=f"Zeit: {round(runtime, 2)}")
            self.root.after(100, self.change_run_time)

    def change_frame_color(self):
        color = self.frame_spacing['bg']
        self.root.after(1000, self.change_frame_color)

    def block(self, state:bool):
        if state:
            state = "disabled"
        else:
            state = "enabled"

        #self.train_drill_start.configure(state=state)
        #self.train_predict.configure(state=state)
        self.train_delete_last.configure(state=state)
        self.button_back.configure(state=state)


###############################################
############   Predict_Screen    ##############
###############################################
class Predict_Window(Screen):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.min = (1200, 700)
        self.root = root

        self.max_rows = 1 + 3 + 1
        self.max_columns = 1 + 1 + 1    #between the widgets, right has span 2

        self.out_block_color = '#c6d7ff'

        self.is_drilling = False
        self.start_time = None
        self.models = ["SVC", "RandomForest", "KNN"]
        self.model_params = ["predefined", "auto"]
        self.model_norm = ["normalize", "not normalize"]

        self.create_widgets()
        self.weighting()
        self.add_padding()
        self.hide()

    def create_widgets(self):
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
        #self.var_model.trace('w', self.model_changed)
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
        self.predict_out_frame.place(relx=0.025, rely=0.05, relwidth=0.95, relheight=0.9)

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

        #self.predict_out_bar_chart = ttk.Label(self.predict_out_frame, text="?", anchor='w', font='Helvetica 16 bold')
        #self.predict_out_bar_chart.grid(row=1, rowspan=3, column=3, sticky="nwse")

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
        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)

        self.combobox_model.grid_configure(pady=10)
        self.combobox_model_norm.grid_configure(pady=10)

        #self.predict_in_reset.grid_configure()   
        #self.predict_in_start.grid_configure(pady=20, padx=35)  
        #self.predict_in_predict.grid_configure()       

    def weighting(self):
        for n in range(self.max_rows):
            self.grid_rowconfigure(n, weight=1, minsize=20)
        self.grid_rowconfigure(1, weight=1, minsize=250)
        self.grid_rowconfigure(3, weight=1, minsize=100)
        
        for n in range(self.max_columns):
            self.grid_columnconfigure(n, weight=1, minsize=50) 
        self.grid_columnconfigure(1, weight=1, minsize=150) 

        # (int(self.winfo_width()*0.35), int(self.winfo_height()*0.45)
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
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.cg_booster_border.start()
        self.model_frame_bg.start()

    def hide(self):
        self.pack_forget()

    def set_amount(self, amount):
        self.predict_in_amount.configure(text=f'Amount: {amount}')

    def model_changed(self):
        pass

    def event_back(self):
        self.root.load_screen_train(self)
        self.root.terminal.add_event("from-predict-to-train")
        self.cg_booster_border.stop()
        self.model_frame_bg.stop()

    def event_start_button(self):
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
        self.root.terminal.add_event('reset-predict')
        self.reset()

    def event_predict_button(self):
        self.root.terminal.add_event('predict', (self.var_model.get(), self.var_model_param.get(), self.var_model_norm.get()))
        #if self.model_changed:
        #    self.root.terminal.add_event('predict', (self.var_model.get(),))
        #else:
        #    self.root.terminal.add_event('predict', (None,))
        self.model_changed = False

    def event_delete_last_button(self):
        self.root.terminal.add_event('delete-last-predict-drill')

    def reset(self):
        self.predict_out_who_drilled.configure(text="Es hat gebohrt:")
        self.predict_out_who_drilled_answer.configure(text="      ?      ")
        self.predict_out_how_sure.configure(text="Genauigkeit:")
        self.predict_out_how_sure_answer.configure(text="      ?      ")
        self.predict_out_which_algo.configure(text="Verwendeter Algorithmus:")
        self.predict_out_which_algo_answer.configure(text="      ?      ")
        #self.predict_out_bar_chart.configure(text="", image='')

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
        self.predict_in_start['text'] = "Stopp Bohrung"
        self.start_time = time()
        self.root.after(100, self.change_run_time)
        self.is_drilling = True

    def drill_ends(self):
        self.predict_in_start['text'] = "Start Bohrung"
        self.is_drilling = False

    def stop_time(self):
        self.is_drilling = False

    def delete_last_btn_change(self, state):
        self.predict_in_delete_last.configure(state=state)

    def show_result(self, who, how, what):
        self.predict_out_who_drilled_answer.configure(text=f"{who}")
        self.predict_out_how_sure_answer.configure(text=f"{round(how, 2)}%")
        self.predict_out_which_algo_answer.configure(text=f"{what}")
        #self.predict_out_bar_chart.configure(text="?")

    # OLD Method
    def draw_result(self, img_path):
        self.image = Image.open(img_path)
        self.image = self.image.resize((int(self.winfo_width()*0.35), int(self.winfo_height()*0.45)), Image.ANTIALIAS)

        self.tk_image = ImageTk.PhotoImage(self.image)
        self.predict_out_bar_chart.configure(text='', image=self.tk_image)

    def start_button_change(self, state):
        self.train_drill_start.config(state=state)

    def change_run_time(self):
        if self.is_drilling:
            runtime = time() - self.start_time
            self.predict_in_time.configure(text=f"Zeit: {round(runtime, 2)}")
            self.root.after(100, self.change_run_time)


###############################################
############   Credits_Screen    ##############
###############################################
class Credits_Window(Screen):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.min = (1200, 700)

        self.max_rows = 3
        self.max_columns = 3

        self.create_widgets()
        self.weighting()
        self.add_padding()
        self.hide()

    def create_widgets(self):
        # Back Button
        self.button_back = ttk.Button(self, text="<", command=self.event_back, takefocus = 0)
        self.button_back.grid(row=0, column=0, sticky="nw")

    def add_padding(self):
        for child in self.winfo_children():
            child.grid_configure(padx=10, pady=10)

    def weighting(self):
        for n in range(self.max_rows):
            self.grid_rowconfigure(n, weight=1, minsize=20) #20
        
        for n in range(self.max_columns):
            self.grid_columnconfigure(n, weight=1, minsize=50) # 50
    
    def show(self):
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

    def hide(self):
        self.pack_forget()

    def event_back(self):
        self.root.load_screen_main_menu(self)

    def event_start_button(self):
        pass


###############################################
#########   Configuration_Screen    ###########
###############################################
class Configuration(Screen):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.min = (800, 600)

        self.max_rows = 2+2+1
        self.max_columns = 1+2+1

        self.cur_theme = "equilux"
        self.cur_screen = "configure_menu"
        self.buttons = {}
        self.bg_rbuttons = []

        self.create_widgets()
        self.configure_menu_wighting() 
        self.add_configure_padding()

    def create_widgets(self):
        # --- Configure MENU ---
        # Back Button
        self.button_back = ttk.Button(self, text="<", command=self.event_back, takefocus = 0)
        self.button_back.grid(row=0, column=0, sticky="nesw")

        # Create Start Button
        self.button_theme = ttk.Button(self, text="Thema", command=self.switch_to_theme, takefocus = 0)
        self.button_theme.grid(row=2, column=2, sticky='NESW')

        # Create Information Button
        self.button_bg = ttk.Button(self, text="Hintergrund", command=self.switch_to_bg, takefocus = 0)
        self.button_bg.grid(row=3, column=2, sticky='NESW')

        # --- Theme ---
        # First row
        self.buttons[THEMES[0]] = ttk.Button(self, text=THEMES[0], command=lambda:self.event_button(THEMES[0]), takefocus = 0)

        self.buttons[THEMES[1]] = ttk.Button(self, text=THEMES[1], command=lambda:self.event_button(THEMES[1]), takefocus = 0)

        self.buttons[THEMES[2]] = ttk.Button(self, text=THEMES[2], command=lambda:self.event_button(THEMES[2]), takefocus = 0)

        self.buttons[THEMES[3]] = ttk.Button(self, text=THEMES[3], command=lambda:self.event_button(THEMES[3]), takefocus = 0)

        # Second Row
        self.buttons[THEMES[4]] = ttk.Button(self, text=THEMES[4], command=lambda:self.event_button(THEMES[4]), takefocus = 0)

        self.buttons[THEMES[5]] = ttk.Button(self, text=THEMES[5], command=lambda:self.event_button(THEMES[5]), takefocus = 0)

        self.buttons[THEMES[6]] = ttk.Button(self, text=THEMES[6], command=lambda:self.event_button(THEMES[6]), takefocus = 0)

        self.buttons[THEMES[7]] = ttk.Button(self, text=THEMES[7], command=lambda:self.event_button(THEMES[7]), takefocus = 0)

        # Third Row
        self.buttons[THEMES[8]] = ttk.Button(self, text=THEMES[8], command=lambda:self.event_button(THEMES[8]), takefocus = 0)

        self.buttons[THEMES[9]] = ttk.Button(self, text=THEMES[9], command=lambda:self.event_button(THEMES[9]), takefocus = 0)

        self.buttons[THEMES[10]] = ttk.Button(self, text=THEMES[10], command=lambda:self.event_button(THEMES[10]), takefocus = 0)

        self.buttons[THEMES[11]] = ttk.Button(self, text=THEMES[11], command=lambda:self.event_button(THEMES[11]), takefocus = 0)

        # Fourth Row
        self.buttons[THEMES[12]] = ttk.Button(self, text=THEMES[12], command=lambda:self.event_button(THEMES[12]), takefocus = 0)

        self.buttons[THEMES[13]] = ttk.Button(self, text=THEMES[13], command=lambda:self.event_button(THEMES[13]), takefocus = 0)

        self.buttons[THEMES[14]] = ttk.Button(self, text=THEMES[14], command=lambda:self.event_button(THEMES[14]), takefocus = 0)

        self.buttons[THEMES[15]] = ttk.Button(self, text=THEMES[15], command=lambda:self.event_button(THEMES[15]), takefocus = 0)

        # Fifth Row
        self.buttons[THEMES[16]] = ttk.Button(self, text=THEMES[16], command=lambda:self.event_button(THEMES[16]), takefocus = 0)

        self.buttons[THEMES[17]] = ttk.Button(self, text=THEMES[17], command=lambda:self.event_button(THEMES[17]), takefocus = 0)

        self.buttons[THEMES[18]] = ttk.Button(self, text=THEMES[18], command=lambda:self.event_button(THEMES[18]), takefocus = 0)

        self.buttons[THEMES[19]] = ttk.Button(self, text=THEMES[19], command=lambda:self.event_button(THEMES[19]), takefocus = 0)
        
        # Sixth Row
        self.buttons[THEMES[20]] = ttk.Button(self, text=THEMES[20], command=lambda:self.event_button(THEMES[20]), takefocus = 0)

        self.buttons[THEMES[21]] = ttk.Button(self, text=THEMES[21], command=lambda:self.event_button(THEMES[21]), takefocus = 0)

        self.buttons[THEMES[22]] = ttk.Button(self, text=THEMES[22], command=lambda:self.event_button(THEMES[22]), takefocus = 0)

        self.buttons[THEMES[23]] = ttk.Button(self, text=THEMES[23], command=lambda:self.event_button(THEMES[23]), takefocus = 0)

        # Seventh Row
        self.buttons[THEMES[24]] = ttk.Button(self, text=THEMES[24], command=lambda:self.event_button(THEMES[24]), takefocus = 0)

        self.buttons[THEMES[25]] = ttk.Button(self, text=THEMES[25], command=lambda:self.event_button(THEMES[25]), takefocus = 0)

        self.buttons[THEMES[26]] = ttk.Button(self, text=THEMES[26], command=lambda:self.event_button(THEMES[26]), takefocus = 0)

        self.buttons[THEMES[27]] = ttk.Button(self, text=THEMES[27], command=lambda:self.event_button(THEMES[27]), takefocus = 0)

        # Eighth Row
        self.buttons[THEMES[28]] = ttk.Button(self, text=THEMES[28], command=lambda:self.event_button(THEMES[28]), takefocus = 0)

        self.buttons[THEMES[29]] = ttk.Button(self, text=THEMES[29], command=lambda:self.event_button(THEMES[29]), takefocus = 0)

        self.buttons[THEMES[30]] = ttk.Button(self, text=THEMES[30], command=lambda:self.event_button(THEMES[30]), takefocus = 0)

        self.buttons[THEMES[31]] = ttk.Button(self, text=THEMES[31], command=lambda:self.event_button(THEMES[31]), takefocus = 0)

        

        # --- Background ---
        self.bg_nr = tk.IntVar()
        self.bg_nr.set(0)

        self.bg_rbuttons += [ttk.Radiobutton(self, text="Kein Hintergrund", variable=self.bg_nr, command=self.change_bg, value=0, takefocus = 0)]
        self.bg_rbuttons += [ttk.Radiobutton(self, text="Herbst Hintergrund", variable=self.bg_nr, command=self.change_bg, value=1, takefocus = 0)]
        self.bg_rbuttons += [ttk.Radiobutton(self, text="Oktopus Hintergrund", variable=self.bg_nr, command=self.change_bg, value=2, takefocus = 0)]
        self.bg_rbuttons += [ttk.Radiobutton(self, text="Galaxie Hintergrund", variable=self.bg_nr, command=self.change_bg, value=3, takefocus = 0)]
        

    def configure_menu_wighting(self):
        for n in range(self.max_rows):
            self.grid_rowconfigure(n, weight=1, minsize=50)
        
        for n in range(self.max_columns):
            self.grid_columnconfigure(n, weight=1, minsize=100)

        self.grid_rowconfigure(0, weight=0, minsize=50)
        self.grid_columnconfigure(0, weight=0, minsize=50)
        self.grid_rowconfigure(1, weight=1, minsize=10)
        self.grid_columnconfigure(1, weight=1, minsize=10)

    def theme_weighting(self):
        self.grid_columnconfigure(0, weight=1, minsize=100)
        self.grid_columnconfigure(5, weight=1, minsize=100)
        self.grid_rowconfigure(0, weight=1, minsize=50)
        self.grid_rowconfigure(9, weight=1, minsize=50)

        for n in range(1, self.max_rows-1):
            self.grid_rowconfigure(n, weight=1, minsize=50)
        
        for n in range(1, self.max_columns-1):
            self.grid_columnconfigure(n, weight=1, minsize=100)

    def bg_weighting(self):
        for n in range(self.max_rows):
            self.grid_rowconfigure(n, weight=1, minsize=50)
        
        for n in range(self.max_columns):
            self.grid_columnconfigure(n, weight=1, minsize=100)

        self.grid_rowconfigure(0, weight=0, minsize=50)
        self.grid_columnconfigure(0, weight=0, minsize=50)

    def reset_weighting(self):
        for n in range(0, self.max_rows):
            self.grid_rowconfigure(n, weight=0, minsize=0)
        
        for n in range(0, self.max_columns):
            self.grid_columnconfigure(n, weight=0, minsize=0)

    def switch_to_theme(self):
        self.reset_weighting()
        self.max_rows = 1 + 8 + 1
        self.max_columns = 4 + 2
        self.cur_screen = "theme_screen"

        self.hide_configure_menu()
        self.show_theme_screen()
        self.add_theme_padding()
        self.theme_weighting()
        self.root.set_min()

    def switch_to_configure_menu(self, from_screen):
        self.reset_weighting()
        self.max_rows = 2 + 2 + 1
        self.max_columns = 1 + 2 + 1

        if from_screen == "theme_screen":
            self.hide_theme_screen()
        elif from_screen == "bg_screen":
            self.hide_bg_screen()

        self.show_configure_menu()
        self.configure_menu_wighting()
        self.add_configure_padding()
        self.root.set_min()

    def switch_to_bg(self):
        self.reset_weighting()
        self.max_rows = 4+2+1
        self.max_columns = 1+2+1
        self.cur_screen = "bg_screen"

        self.hide_configure_menu()
        self.show_bg_screen()
        self.add_bg_padding()
        self.bg_weighting()
        self.root.set_min()

    def add_configure_padding(self):
        self.button_bg.grid_configure(padx=20, pady=20)
        self.button_back.grid_configure(padx=20, pady=20)
        self.button_theme.grid_configure(padx=20, pady=20)

    def add_theme_padding(self):
        for button in self.buttons.values():
            button.grid_configure(padx=10, pady=10)
        
    def add_bg_padding(self):
        for rbutton in self.bg_rbuttons:
            rbutton.grid_configure(padx=10, pady=10)
        #self.button_back.grid_configure(ipady=30)

    def show_configure_menu(self):
        self.button_theme.grid(row=2, column=2, sticky='NESW')
        self.button_bg.grid(row=3, column=2, sticky='NESW')

    def hide_configure_menu(self):
        self.button_bg.grid_forget()
        self.button_theme.grid_forget()

    def show_theme_screen(self):
        # First row
        self.buttons[THEMES[0]].grid(row=1, column=1, sticky="nesw")
        self.buttons[THEMES[1]].grid(row=1, column=2, sticky="nesw")
        self.buttons[THEMES[2]].grid(row=1, column=3, sticky="nesw")
        self.buttons[THEMES[3]].grid(row=1, column=4, sticky="nesw")

        # Second Row
        self.buttons[THEMES[4]].grid(row=2, column=1, sticky="nesw")
        self.buttons[THEMES[5]].grid(row=2, column=2, sticky="nesw")
        self.buttons[THEMES[6]].grid(row=2, column=3, sticky="nesw")
        self.buttons[THEMES[7]].grid(row=2, column=4, sticky="nesw")

        # Third Row
        self.buttons[THEMES[8]].grid(row=3, column=1, sticky="nesw")
        self.buttons[THEMES[9]].grid(row=3, column=2, sticky="nesw")
        self.buttons[THEMES[10]].grid(row=3, column=3, sticky="nesw")
        self.buttons[THEMES[11]].grid(row=3, column=4, sticky="nesw")

        # Fourth Row
        self.buttons[THEMES[12]].grid(row=4, column=1, sticky="nesw")
        self.buttons[THEMES[13]].grid(row=4, column=2, sticky="nesw")
        self.buttons[THEMES[14]].grid(row=4, column=3, sticky="nesw")
        self.buttons[THEMES[15]].grid(row=4, column=4, sticky="nesw")

        # Fifth Row
        self.buttons[THEMES[16]].grid(row=5, column=1, sticky="nesw")
        self.buttons[THEMES[17]].grid(row=5, column=2, sticky="nesw")
        self.buttons[THEMES[18]].grid(row=5, column=3, sticky="nesw")
        self.buttons[THEMES[19]].grid(row=5, column=4, sticky="nesw")

        # Sixth Row
        self.buttons[THEMES[20]].grid(row=6, column=1, sticky="nesw")
        self.buttons[THEMES[21]].grid(row=6, column=2, sticky="nesw")
        self.buttons[THEMES[22]].grid(row=6, column=3, sticky="nesw")
        self.buttons[THEMES[23]].grid(row=6, column=4, sticky="nesw")
        
        # Seventh Row
        self.buttons[THEMES[24]].grid(row=7, column=1, sticky="nesw")
        self.buttons[THEMES[25]].grid(row=7, column=2, sticky="nesw")
        self.buttons[THEMES[26]].grid(row=7, column=3, sticky="nesw")
        self.buttons[THEMES[27]].grid(row=7, column=4, sticky="nesw")

        # Eigth Row
        self.buttons[THEMES[28]].grid(row=8, column=1, sticky="nesw")
        self.buttons[THEMES[29]].grid(row=8, column=2, sticky="nesw")
        self.buttons[THEMES[30]].grid(row=8, column=3, sticky="nesw")
        self.buttons[THEMES[31]].grid(row=8, column=4, sticky="nesw")

    def hide_theme_screen(self):
        for theme in THEMES:
            self.buttons[theme].grid_forget()

    def show_bg_screen(self):
        for i, rbutton in enumerate(self.bg_rbuttons):
            rbutton.grid(row=i+2, column=2, sticky="w")

    def hide_bg_screen(self):
        for rbutton in self.bg_rbuttons:
            rbutton.grid_forget()

    def show(self):
        self.pack(expand=True, fill='both', side='top')
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.reset_weighting()
        self.max_rows = 2 + 2 +1
        self.max_columns = 1 + 2 + 1

        self.show_configure_menu()
        self.configure_menu_wighting()
        self.add_configure_padding()
        self.root.set_min()

    def hide(self):
        self.pack_forget()

    def event_back(self):
        if self.cur_screen == "configure_menu":
            self.root.load_screen_main_menu(self)
        else:
            old_screen = self.cur_screen
            self.cur_screen = "configure_menu"
            self.switch_to_configure_menu(old_screen)

    def event_button(self, theme_name):
        self.cur_theme = theme_name
        self.root.load_theme(theme_name)

    def change_bg(self):
        if self.bg_nr.get() == 0:
            self.root.set_bg('')
        elif self.bg_nr.get() == 1:
            #pil_button_image = Image.open("src/anoog/automation/img/01dodw.jpg")
            #self.bg_image = ImageTk.PhotoImage(pil_button_image)
            #self.bg_image=tk.PhotoImage(file="src/anoog/automation/img/01dodw.jpg")
            self.root.set_bg("src/anoog/automation/img/01dodw.jpg")
        elif self.bg_nr.get() == 2:
            #pil_button_image = Image.open("src/anoog/automation/img/zxg21w.jpg")
            #self.bg_image = ImageTk.PhotoImage(pil_button_image)
            #self.bg_image=tk.PhotoImage(file="src/anoog/automation/img/zxg21w.jpg")
            self.root.set_bg("src/anoog/automation/img/zxg21w.jpg")
        elif self.bg_nr.get() == 3:
            #pil_button_image = Image.open("src/anoog/automation/img/1jole3.jpg")
            #self.bg_image = ImageTk.PhotoImage(pil_button_image)
            #self.bg_image=tk.PhotoImage(file="src/anoog/automation/img/1jole3.jpg")
            self.root.set_bg("src/anoog/automation/img/1jole3.jpg")


###############################################
#################   Run    ####################
###############################################
def run(data_path="src/DrillDummy/testdata", drillcapture_path="src/DrillDummy/drillcapture.exe", 
                                drilldriver_path="src/DrillDummy/drilldriver.exe", op=op.WINDOWS):
    GUI_App().run(data_path, drillcapture_path, drilldriver_path, op)


