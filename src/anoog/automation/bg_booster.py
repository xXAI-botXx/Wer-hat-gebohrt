"""
This module contains a Tkinter-Widget for gradient-color.

Its runnable to test the Gradient-Color-Widget.

Author: Tobia Ippolito
"""

import abc
import random
import threading
from enum import Enum

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageDraw, ImageTk

COLOR_CHAINS = {'pastel':('#ffb3ba', '#bae1ff'),
                'deep_sea':('#b2d8d8', '#008080'),
                'old_times':('#96ceb4', '#ffeead', '#ff6f69', '#ffcc5c', '#88d8b0'),
                'sunset':('#ff6f69', '#ffcc5c'),
                'blue_eyes':('#011f4b', '#03396c', '#005b96', '#6497b1', '#b3cde0'),
                'dune':('#8d5524', '#c68642', '#e0ac69', '#f1c27d', '#ffdbac'),
                'evening_past':('#66545e', '#a39193', '#aa6f73', '#eea990', '#f6e0b5'),
                'light_rain':('#e1f7d5', '#ffbdbd', '#c9c9ff', '#ffffff', '#f1cbff'),
                'generation_zero':('#ff71ce', '#01cdfe', '#05ffa1', '#b967ff', '#fffb96'),
                'dark_times':('#6e7f80', '#536872', '#708090', '#536878', '#36454f'),
                'discord':('#7289da', '#424549', '#36393e', '#282b30', '#1e2124'),
                'lucifer':('#ff0000', '#bf0000', '#800000', '#400000', '#000000'),
                'freeze_nature':('#a3c1ad', '#a0d6b4', '#5f9ea0', '#317873', '#49796b'),
                'sommer_dream':('#a8e6cf', '#dcedc1', '#ffd3b6', '#ffaaa5', '#ff8b94'),
                'sommer':('#ee4035', '#f37736', '#fdf498', '#7bc043', '#0392cf'),
                'cyber_shot':('#00076f', '#44008b', '#9f45b0', '#e54ed0', '#ffe4f2'),
                'from_future':('#ff00c1', '#9600ff', '#4900ff', '#00b8ff', '#00fff9'),
                'cyberpunk':('#711c91', '#ea00d9', '#0abdc6', '#133e7c', '#091833'),
                'sky':('#f7cac9', '#dec2cb', '#c5b9cd', '#abb1cf', '#92a8d1'),
                'gentle_breath':('#b8dbd3', '#f7e7b4', '#68c4af', '#96ead7', '#f2f6c3')}

FAV_COLOR_MIX = (('#ff4040','#5757ff'), ('#ffb3ba', '#bae1ff'), ('#ff6f69', '#ffcc5c'), ('#005b96', '#6497b1'), ('#8d5524', '#f1c27d'),
                 ('#66545e', '#eea990'), ('#ff71ce', '#01cdfe'), ('#05ffa1', '#b967ff'), ('#a3c1ad', '#5f9ea0'), ('#ee4035', '#0392cf'),
                 ('#ee4035', '#7bc043'), ('#9f45b0', '#ff801a'))

# flow-direction:
#    - pos = nach oben  bzw. links bei Vertikal
#    - neg = nach unten bzw. rechts bei vertikal

# Color-Chains works not very good
class Color_Gradient_Booster(tk.Canvas):
    """
    Tkinter-Widget filled out with a gradient color.

    The gradient-color can be static or dynamic (with a flow).

    :param root: The basic widget of the gui-application.
    :type root: tk.TK()
    :param parent: The parent of this widget (which contains this widget).
    :type parent: tk.Widget
    :param mode: Defines the direction of the gradient-color. ('HORIZONTAL', 'random', 'VERTICAL')
    :type mode: str, optional
    :param should_change_color: Defines whether or not the color changes (dynamic).
    :type should_change_color: bool, optional
    :param change_time: Defines how fast the colors should be changed in dynamic mode. In seconds.
    :type change_time: float, optional
    :param width: The width of the widget (by most of the LayoutManager it's not relevant)
    :type width: int, optional
    :param height: The height of the widget (by most of the LayoutManager it's not relevant)
    :type height: int, optional
    :param height: Activates/Deactivates a small variation of the color-values, should ended in a shiny-glimmer-effect.
    :type height: bool, optional
    :param color_chain: Defines the used colors.
    :type color_chain: list of str, optional
    :param gradient_size_tendency: Defines the direction of the flow (dynamic). ('neg' or 'pos' or 'random')
    :type gradient_size_tendency: str, optional
    """
    def __init__(self, root, parent, mode='HORIZONTAL', should_change_color=False, change_time=0.1, 
                 width=None, height=None, shiny_flow_effect=False, color_chain=None, gradient_size_tendency='neg'):
        """
        Constructor method
        """
        super().__init__(parent, highlightthickness=0)
        self.root = root
        self.parent = parent

        self.width = width
        self.height = height

        # set height/width of widget and image
        if width != None and height != None:
            self.configure(width=width, height=height)

        # transform hex color to rgb
        #self.from_color = self.hex2rgb(from_color)
        #self.to_color = self.hex2rgb(to_color)

        self.from_color_increasing = (0, 0, 0)

        if type(color_chain) in [list, tuple]:
            self.color_chain = color_chain
        elif color_chain in COLOR_CHAINS.keys():
            self.color_chain = COLOR_CHAINS[color_chain]
        elif color_chain == 'random':
            #self.color_chain = random.choice(list(COLOR_CHAINS.values()))
            self.color_chain = random.choice(FAV_COLOR_MIX)
        else:
            self.color_chain = ('#ff4040', '#5757ff')

        if mode == 'random':
            self.mode = random.choice(('HORIZONTAL', 'VERTICAL'))
        else:
            self.mode = mode

        if gradient_size_tendency == 'random':
            self.gradient_size_tendency = random.choice(('pos', 'neg'))
        else:
            self.gradient_size_tendency = gradient_size_tendency

        self.should_change_color = should_change_color
        self.change_time = change_time
        # for changing the gradient size
        self.gradient_size = 1.0
        self.gradient_size_vario = 0.0001
        self.gradient_size_vario_factor = (-0.0001, 0.0001)
        # for variate the show every time
        if shiny_flow_effect:
            self.shiny_flow = (-0.1, 0.1)
        else:
            self.shiny_flow = (0.0, 0.0)

        if self.color_chain != None:
            self.from_color = self.hex2rgb(self.color_chain[0])
            self.to_color = self.hex2rgb(self.color_chain[1])
            self.chain_pointer = 2
        self.color = [self.from_color, self.to_color]

        # maybe call on some later point (?)
        self.update()

    def run(self):
        """
        Calls the update method and set itself to be called in some time (change_time defines that waiting time).
        """
        if self.should_change_color:
            self.variate_gradient_size()
            self.update()
            self.root.after(int(self.change_time*1000), self.run)

    def update(self):
        """
        Creates and draws the gradient color.
        """
        # get height and width
        width = self.winfo_width()
        height = self.winfo_height()

        img_width = width
        img_height = height

        image = Image.new("RGB", (img_width, img_height), "#FFFFFF")
        draw = ImageDraw.Draw(image)

        if self.mode == 'HORIZONTAL':
            steps = height
        else:
            steps = width

        # calc color-stepsize
        gradient_r = float(self.color[1][0] - self.color[0][0])/steps*self.gradient_size
        gradient_g = float(self.color[1][1] - self.color[0][1])/steps*self.gradient_size
        gradient_b = float(self.color[1][2] - self.color[0][2])/steps*self.gradient_size

        # update adding
        self.from_color_increasing = (gradient_r*self.gradient_size*100, gradient_g*self.gradient_size*100, gradient_b*self.gradient_size*100)
        # adding color for complete show of to_color
        add = self.from_color_increasing
        r, g, b = self.color[0][0]+add[0], self.color[0][1]+add[1], self.color[0][2]+add[2]
        for i in range(steps):
            # increase color
            random.random()
            r += gradient_r + self.calc_shiny_flow_effect()
            g += gradient_g + self.calc_shiny_flow_effect()
            b += gradient_b + self.calc_shiny_flow_effect()
            #print("\n",i)
            #print(gradient_r, gradient_g, gradient_b)
            #print(int(self.color[0][0]), int(self.color[0][1]), int(self.color[0][2]))

            if self.mode == 'HORIZONTAL':
                y0 = int(float(img_height * i)/steps)
                y1 = int(float(img_height * (i+1))/steps)
                draw.rectangle((0, y0, img_width, y1), fill=(int(r), int(g), int(b)))
            else:
                x0 = int(float(img_width * i)/steps)
                x1 = int(float(img_width * (i+1))/steps)
                draw.rectangle((x0, 0, x1, img_height), fill=(int(r), int(g), int(b)))

        self.gradient_image = ImageTk.PhotoImage(image)
        self.create_image(0, 0, anchor="nw", image=self.gradient_image)

    def start(self):
        """
        Starts the flow-effect.

        So that the gradient-color moves.
        """
        self.should_change_color = True
        self.run()

    def stop(self):
        """
        Stops the flow-effect.

        So that the gradient-color not moves anymore.
        """
        self.should_change_color = False

    # variate colors
    def variate_color(self):
        """
        Brings a little variation of the colors.
        """
        for i, color in enumerate(self.color):
            for j, value in enumerate(color):
                self.color[i][j] = (value + random.randint(-2, 2))%255

    def variate_gradient_size(self):
        """
        Variates the size of the 2 colors. 
        
        This creates a flow-effect.
        """
        if self.gradient_size_tendency == 'pos':
            self.gradient_size += self.gradient_size_vario
            if self.gradient_size >= 3.0:
                self.color_chain_change()
                self.gradient_size_tendency = 'neg'
        elif self.gradient_size_tendency == 'neg':
            self.gradient_size -= self.gradient_size_vario
            if self.gradient_size <= 0.0:
                self.color_chain_change()
                self.gradient_size_tendency = 'pos'

        # Variate variation speed -> but not every time
        if random.randint(0,1) == 1:
            self.variate_gradient_size_speed()

    # desto kleiner desto unwahrscheinlicher
    def variate_gradient_size_speed(self) -> float:
        """
        Variate the speed of the gradient-color change time.
        """
        min, max = self.gradient_size_vario_factor
        self.gradient_size_vario += (random.random()*(max-min))+min
        # reset, if value to low or to high
        if self.gradient_size_vario <= 0.0 or self.gradient_size_vario >= 0.1:
            self.gradient_size_vario = 0.02

    def calc_shiny_flow_effect(self) -> float:
        """
        Calculates the variation of the color-value for the shiny-effect.

        :return: Number of the variation of the normal color-point.
        :rtype: float
        """
        min, max = self.shiny_flow
        return (random.random()*(max-min))+min

    def color_chain_change(self):
        """
        Changes the current 2 colors using the color-chain.

        With that, there can be many color used, but at one time can only 2 colors be activate.
        """
        # change only its over 2
        if len(self.color_chain) > 2:
            # update pointer
            if self.chain_pointer >= len(self.color_chain)-1:
                self.chain_pointer = 0
            else:
                self.chain_pointer += 1
                
            if self.gradient_size_tendency == 'pos':
                self.color[0] = self.hex2rgb(self.color_chain[self.chain_pointer])
            elif self.gradient_size_tendency == 'neg':
                self.color[1] = self.hex2rgb(self.color_chain[self.chain_pointer])

    def set_random_colors(self, n_colors=2):
        """
        Calculates random colors.

        Sets the new colors as color_chain inplace.

        :param n_colors: Defines how many random colors should be calculated.
        :type n_colors: int, optional
        """
        hex_codes = ('f', 'e', 'd', 'c', 'b', 'a', '9', '8', '7', '6', '5', '4', '3', '2', '1', '0')
     
        colors = []
        for i in range(n_colors):
            colors += [f"#{''.join(list(random.choice(hex_codes) for i in range(6)))}"]
        self.color_chain = colors
        self.from_color = self.hex2rgb(self.color_chain[0])
        self.to_color = self.hex2rgb(self.color_chain[1])
        self.chain_pointer = 2
        self.color = [self.from_color, self.to_color]

    def set_fav_color(self):
        """
        Picks a random color-chain from a selection.

        Sets the new colors as color_chain inplace.
        """
        color = random.choice(FAV_COLOR_MIX)    #+tuple(COLOR_CHAINS.values())
        self.from_color = self.hex2rgb(self.color_chain[0])
        self.to_color = self.hex2rgb(self.color_chain[1])
        self.chain_pointer = 2
        self.color = [self.from_color, self.to_color]

    def hex2rgb(self, str_hex):
        """
        Calculate a hex color to an rgb color.

        :param str_hex: A color in hex-format with # or not at the beginning.
        :type str_hex: str
        """
        if str_hex.startswith("#"):
            str_hex = str_hex[1:]
        r, g, b = str_hex[0:2], str_hex[2:4], str_hex[4:6]

        # transform hex in decimal with int(x, 16)
        return list(int(hex_num, 16) for hex_num in (r, g, b))

    def set_on_screen(self):
        """
        Place the Gradient-color-widget on his parent. 

        Will outfull the whole parent-widget.
        """
        self.place(relx=0, rely=0, relwidth=1, relheight=1)

    def set_off_screen(self):
        """
        Unplace the Gradient-color-widget on his parent. 
        """
        self.place_forget()


# XXX Testing XXX

if __name__ == "__main__":
    def event_btn_clicked(booster):
        """
        Event for GUI-Button for stop/start the flow.
        """
        global change_color_activated, start_stop_btn
        if change_color_activated:
            booster.stop()
            change_color_activated = False
            start_stop_btn['text'] = 'Start'
        else:
            booster.start()
            change_color_activated = True
            start_stop_btn.configure(text='Stop')


    root = tk.Tk()
    root.geometry('600x400')

    change_color_activated = False

    main_window = ttk.Frame(root)
    main_window.pack(expand=True, fill='both')

    design = ('#05ffa1', '#b967ff')#'old_times'#['#ff6f69', '#ffeead']#'random'    # None, 'cyber_shot', 'dune', 'light_rain'
    cg_booster = Color_Gradient_Booster(root=root, parent=main_window,  mode='random', 
                                        should_change_color=change_color_activated, change_time=0.5, 
                                        color_chain=design, gradient_size_tendency='neg')
    #cg_booster.grid(row=1, column=1, sticky="nesw")
    cg_booster.place(x=0, y=0, relwidth=1, relheight=1)
    #cg_booster.set_random_colors()
    #cg_booster.set_fav_color()

    start_stop_btn = ttk.Button(main_window, text="Start", command=lambda:event_btn_clicked(cg_booster))
    start_stop_btn.grid(row=1, column=1)

    for i in range(3):
        main_window.grid_rowconfigure(i, weight=1)
    #main_window.grid_rowconfigure(2, weight=1)
    for i in range(3):
        main_window.grid_columnconfigure(i, weight=1)

    root.mainloop()
