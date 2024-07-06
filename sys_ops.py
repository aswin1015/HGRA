import psutil
import time
from random import randint
import subprocess
from pynput.keyboard import Key, Controller
from PIL import ImageGrab
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import os
import threading

import pygame
import requests
import pyttsx3
from bs4 import BeautifulSoup

from googletrans import Translator
import pyperclip

class tasks:
    def __init__(self):
        self.machine = pyttsx3.init()
        self.save_directory = "C:/Users/Hp/Desktop/mini project/100%/assets/pic"
        self.song_directory = "C:\\Users\\Hp\\Desktop\\mini project/100%\\assets\\songs"
        self.sysfun = SystemTasks()
        self.winfun = WindowOpt()

    def talk(self,text):
        self.machine.say(text)
        self.machine.runAndWait()

    def open_notepad(self):
        try:
            subprocess.Popen('C:/Program Files/WindowsApps/Microsoft.WindowsNotepad_11.2401.26.0_x64__8wekyb3d8bbwe/Notepad/Notepad.exe')
        except Exception as e:
            print("An error occurred:", e)
        
    def close_window(self):
        self.winfun.closeWindow()

    def select_and_copy(self):
        self.sysfun.copy()
    
    def paste(self):
        if not self.pause_pot():
            self.sysfun.pastee()
    
    def change_window(self):
        self.winfun.switchWindow()

    def pause_pot(self,player_name="PotPlayerMini.exe"):
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Check if the process name matches the media player
                    if player_name.lower() in proc.info['name'].lower():
                        print(f"{player_name} is running (PID: {proc.info['pid']})")
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            print(f"{player_name} is not running.")
            return False
    
    def pause_video(self): 
        # if self.pause_pot:
        self.sysfun.pause()
    
    def fast_forward(self):
        # if self.pause_pot:
        self.sysfun.fast()
    
    def news(self):
        url = 'https://www.bbc.com/news/world'
        response = requests.get(url)
        html_content = response.content
        soup = BeautifulSoup(html_content,'html.parser')
        divs = soup.find_all('h2',class_='sc-4fedabc7-3' )
        new=""
        for div in divs[:5]:
            new = new +f'{div.text}.\n'
        self.talk(new)
        self.machine.stop()
            
    def screenshot(self):
        im = ImageGrab.grab()
        im.save(f'{self.save_directory}/ss_{randint(1, 100)}.jpg')

    def mute(self):
        # Get the default audio renderer (speaker)
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

        # Cast interface to IAudioEndpointVolume
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        current_mute_state = volume.GetMute()

        if current_mute_state:
            # System is muted, unmute it
            volume.SetMute(False, None)
            print("System audio unmuted.")
        else:
            # System is not muted, mute it
            volume.SetMute(True, None)
            print("System audio muted.")

    def play_songs(self):
        def play():
            pygame.init()
            pygame.mixer.init()
            files = os.listdir(self.song_directory)
            songs = [file for file in files if file.endswith('.mp3')]
            
            song_file = os.path.join(self.song_directory, songs[0])
            pygame.mixer.music.load(song_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.delay(100)
            pygame.mixer.quit()
            pygame.quit()
        threading.Thread(target=play).start()

    def translate(self):
        
        line=pyperclip.paste()
        translator = Translator()
        # Translate a text from English to Malayalam
        translated_text = translator.translate(line, src="en", dest="ml")
        pyperclip.copy(translated_text.text)
        
    def lock_screen(self):
        # Define constants for WinAPI functions
        user32 = ctypes.windll.user32
        # Lock the screen
        user32.LockWorkStation()

class SystemTasks:
    def __init__(self):
        self.keyboard = Controller()


    def select(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('a')
        self.keyboard.release('a')
        self.keyboard.release(Key.ctrl)

    def copy(self):
        self.select()
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('c')
        self.keyboard.release('c')
        self.keyboard.release(Key.ctrl)

    def pastee(self):
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('v')
        self.keyboard.release('v')
        self.keyboard.release(Key.ctrl)
    

    def pause(self):
        self.keyboard.tap(Key.space)

    def fast(self):
        self.keyboard.press(Key.right)
        self.keyboard.release(Key.right)

class WindowOpt:
    def __init__(self):
        self.keyboard = Controller()

    def closeWindow(self):
        self.keyboard.press(Key.alt_l)
        self.keyboard.press(Key.f4)
        self.keyboard.release(Key.f4)
        self.keyboard.release(Key.alt_l)

    def switchWindow(self):
        self.keyboard.press(Key.alt_l)
        self.keyboard.press(Key.tab)
        self.keyboard.release(Key.tab)
        self.keyboard.release(Key.alt_l)

    