import pyaudio
import pydub
import threading
import mutagen.mp3
import logging
from PIL import Image, ImageTk
from io import BytesIO


class Song:
    """An Audio Segment from pydub module together with the id3 tags read by mutagen.mp3. If the decoder flag is True the
    the file is decoded and loaded at the initiation. If its false it has to be deocded later by the decode method"""

    def __init__(self, filepath, decoder_flag=False):
        mutagenmp3 = mutagen.mp3.MP3(filepath)
        self.filepath = filepath
        self.info = mutagenmp3.info
        self.tag = mutagenmp3.tags
        if not self.tag is None:
            self.title = str(self.tag.get("TIT2"))
            self.artist = str(self.tag.get("TPE1"))
            self.album = str(self.tag.get("TALB"))
        else:
            self.title = None
            self.artist = None
            self.album = None
        if decoder_flag:
            self.segment = pydub.AudioSegment.from_file(filepath)
            self.album_art = self.find_image()
            self.total_mili = len(self.segment)
        else:
            self.segment = None
            self.total_mili = 0
            self.album_art = None

    def __iter__(self):
        return self.segment

    def find_image(self):
        if self.tag is None:
            return
        if self.tag.getall("APIC"):
            APIC_data = self.tag.getall("APIC")[0].data
            buffer = BytesIO(APIC_data)
            image = Image.open(buffer)
            image.resize((20,20))
            image = ImageTk.PhotoImage(image)
            return image
        return
    def decode(self):
        if self.segment is None:
            self.segment = pydub.AudioSegment.from_mp3(self.filepath)
            self.total_mili = len(self.segment)
            self.album_art = self.find_image()


class Controller:
    def __init__(self, model, view):
        self.is_playing = threading.Event()
        self.model = model
        self.view = view
        self.view.set_controller(self)
        self.c_song = Song("/home/emil/Music/Beyoncé-Halo.mp3", True)     # current song
        self.c_mili = 0     # Current mili second
        self.pyaudioInt = pyaudio.PyAudio()
        self.audio_thread = threading.Thread(target=self.play_song, daemon=True)
        self.view.pack()
        self.view.new_song(self.c_song.title, self.c_song.artist, self.c_song.info.length, self.c_song.total_mili,
                           self.c_song.album_art)
        self.audio_thread.start()
        self.view.bindings()  # apply relavent bindings to Tk widgets

    def play_song(self):
        """target function for the Audio thread.doesn't terminate for the whole session. Can be paused by setting
        self.is_playing event. also commands one second increment on the view"""
        stream = self.pyaudioInt.open(format=self.pyaudioInt.get_format_from_width(self.c_song.segment.sample_width),
                                      output=True, channels=self.c_song.segment.channels,
                                      rate=self.c_song.segment.frame_rate)
        while True:
            for _ in range(1000):       # accounts for one second
                self.is_playing.wait()
                self.c_mili += 1
                stream.write(self.c_song.segment[self.c_mili]._data)
            self.view.second_increment(self.c_mili)

    def playpause(self, event):
        if self.is_playing.is_set():
            self.is_playing.clear()
        else:
            self.is_playing.set()

    def slider_click(self, event):
        if self.is_playing.is_set():
            self.is_playing.clear()
        self.c_mili = int(self.view.slider.get())

    def slider_release(self, event):
        a = self.view.slider.get()
        print(a)
        self.is_playing.set()

    def play_new(self, song: Song):
        self.is_playing.clear()
        self.c_song = song
        self.view.new_song(song.title, song.artist, song.info.length, song.total_mili, song.album_art)
        self.c_mili = 0
        self.is_playing.set()

    def next_button(self, event):
        c_song = self.model.get_next()
        self.play_new(c_song)
