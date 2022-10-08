import tkinter as tk
from tkinter import ttk

class View(ttk.Frame):
    def __init__(self, master):
        super(View, self).__init__(master)
        self.controller = None
        # Top Frame Configuration
        self.top_frame = ttk.Frame(self, height=400, width= 500, padding=3)
        self. top_frame.grid(row=1, column=2)
        self.total_mili = 0

        # Side Frame Configuration
        self.side_frame = ttk.Frame(self, height=400, width=100, padding=3)
        self.side_frame.grid(row=1, column=1)

        # set song variables
        self.song_name_var = tk.StringVar()     # have to set these at the initiation
        self.artist_var =tk.StringVar()
        self.total_time = tk.StringVar(value="0")
        self.current_time = tk.StringVar(value='0')


        # Bottom Frame COnfiguration
        self.bottom_frame = ttk.Frame(self, height=100, width=600, padding=3)
        self.bottom_frame.grid(row=2,column=1, columnspan=2)

        #   Bottom Frame label elements
        ttk.Label(self.bottom_frame, textvariable=self.song_name_var).grid(row=1, column=2)
        ttk.Label(self.bottom_frame, textvariable=self.artist_var).grid(row=2, column=2)
        ttk.Label(self.bottom_frame, textvariable=self.total_time).grid(row=1, column=6)
        ttk.Label(self.bottom_frame, textvariable=self.current_time).grid(row=1, column=3)
        self.slider = ttk.Scale(self.bottom_frame, orient=tk.HORIZONTAL, from_=0)
        self.slider.grid(row=1, column=4, columnspan=2)
        self.album_art = ttk.Label(self.bottom_frame)
        self.album_art.grid(rowspan=2, columnspan=1, row=1)
        #   Bottom Frame Buttons
        self.pause_button = ttk.Button(self)
        self.pause_button.grid(row=2, column=4)
        self.next_button = ttk.Button(self)
        self.next_button.grid(row=2, column=5)

    def bindings(self):
        self.pause_button.bind('<Button-1>', self.controller.playpause)
        self.slider.bind("<Button-1>", self.slider_click)
        self.slider.bind("<ButtonRelease-1>", self.controller.slider_release)
        self.next_button.bind("<Button-1>", self.controller.next_button)

    def slider_click(self, event):
        self.slider.event_generate("<Button-3>",x=event.x, y=event.y)
        self.controller.slider_click(event)

    def new_song(self, name, artist, t_time, total_mili, image):
        self.song_name_var.set(name)
        self.artist_var.set(artist)
        self.total_time.set(t_time)
        self.current_time.set("0:00")
        self.total_mili = total_mili
        self.slider.config(to=self.total_mili)
        self.slider.set(0)
        self.album_art.configure(image=image)

    def set_controller(self, controller):
        self.controller = controller

    def second_increment(self, c_mili):
        self.slider.set(c_mili)
        secs = c_mili //1000
        self.current_time.set(f"{secs//60}:{secs%60}")