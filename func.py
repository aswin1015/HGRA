import cv2
import numpy as np
import os
import tkinter as tk
import customtkinter as ctk
from matplotlib import pyplot as plt
import time
import mediapipe as mp 
import tensorflow as tf
import threading
import sqlite3
from sys_ops import *

class func:

    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_holistic = mp.solutions.holistic
        self.actions = np.array(['open_palm','fist','none','thumbs_up','Circle','Rock','W','Stop','cheese','tri','forward','double_peace'])
        #'open_palm','fist','none','thumbs_up','Circle','Rock','W','Stop','cheese','tri'
        # 100 videos worth of data
        self.label_map = {label:num for num, label in enumerate(self.actions)}
        self.no_sequences = 100

        # Videos are going to be 30 frames in length
        self.sequence_length = 30

        # Folder start
        self.start_folder = 1
        self.ans = ''
        self.label_text = ''
        self.prev_text = ''

        self.sysop = tasks()

        self.flag = False

    def mediapipe_detection(self,image, model):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
        image.flags.writeable = False                  # Image is no longer writeable
        results = model.process(image)                 # Make prediction
        image.flags.writeable = True                   # Image is now writeable 
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
        return image, results
    
    def draw_landmarks(self,image, results):
        self.mp_drawing.draw_landmarks(image, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS) # Draw left hand connections
        self.mp_drawing.draw_landmarks(image, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS) # Draw right hand connections
    
    def draw_styled_landmarks(self,image, results):
        # Draw left hand connections
        self.mp_drawing.draw_landmarks(image, results.left_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
                                self.mp_drawing.DrawingSpec(color=(121,22,76), thickness=2, circle_radius=4), 
                                self.mp_drawing.DrawingSpec(color=(121,44,250), thickness=2, circle_radius=2)
                                ) 
        # Draw right hand connections  
        self.mp_drawing.draw_landmarks(image, results.right_hand_landmarks, self.mp_holistic.HAND_CONNECTIONS, 
                                self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=4), 
                                self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                ) 
    
    def extract_keypoints(self,results):
        lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
        rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
        return np.concatenate([ lh, rh])
    
    def ui(self):

        ctk.set_appearance_mode('system')
        ctk.set_default_color_theme('blue')

        root = ctk.CTk()
        root.title("")
        root.state('zoomed')
        # root.geometry('1920x1080')

        sidebar = ctk.CTkFrame(
            master=root,
            fg_color='#144870',
            width=200,height=350,
            corner_radius=0)
        sidebar.pack_propagate(0)
        sidebar.pack(fill='y',anchor='w',side='left')

        def totab1():
            tabview.set('tab1')
        def totab2():
            tabview.set('tab2')
        def totab3():
            if self.flag:
                tab3.winfo_children()[0].destroy()
                build_frame()
            else:
                build_frame()
            tabview.set('tab3')

        ctk.CTkButton(
            master=sidebar,
            text="ASSISTANT",
            fg_color="#fff",
            text_color='black', 
            font=("Arial Bold", 14), 
            hover_color="#eee", anchor="center",
            command=totab1,
            ).pack(anchor="center", ipady=5, pady=(130,0))

        ctk.CTkButton(
            master=sidebar, 
            text="SETTINGS", 
            fg_color="#fff",
            text_color='black', 
            font=("Arial Bold", 14),
            hover_color="#eee", anchor="center",
            command=totab2,
            ).pack(anchor="center", ipady=5, pady=(6,0))

        ctk.CTkButton(
            master=sidebar, 
            text="HELP", 
            fg_color="#fff",
            text_color='black', 
            font=("Arial Bold", 14),
            hover_color="#eee", anchor="center",
            command=totab3,
            ).pack(anchor="center", ipady=5, pady=(6,0))

        tabview = ctk.CTkTabview(
            master=root,
            width=600,
            height=350,
            corner_radius=0,
            )
        tabview.pack(anchor="center",fill='both', expand=True,padx=5, pady=5)

        #tabs
        tab1 = tabview.add('tab1')
        tab2 = tabview.add('tab2')
        tab3 = tabview.add('tab3')

        # tabview._segmented_button._buttons_dict["tab1"].grid_forget()
        # tabview._segmented_button._buttons_dict["tab2"].grid_forget()
        def clear():
            self.textbox.delete('1.0', 'end')

        def start():
            threading.Thread(target=self.pred).start()
        
        #tab1
        self.textbox = ctk.CTkTextbox(tab1,font=('Arial Bold',14))
        self.textbox.pack(fill='both', expand=True,padx=20, pady=20)
        ctk.CTkButton(tab1,text='clear',command=clear).pack(side='left',padx=20)
        ctk.CTkButton(tab1,text='start-cam',command=start).pack(side='left')
        ctk.CTkLabel(tab1,text='HGCA',font=('Arial Bold',16)).pack()

        #tab2
        self.framet2 = ctk.CTkFrame(tab2)
        self.framet2.pack(anchor='center',pady=50)

        label_action = ctk.CTkLabel(self.framet2,text='Choose Gesture:',font=('Arial',16))
        label_action.grid(row =0,column=0,padx =10,pady =10,sticky = 'e')
        gest = ['open_palm','fist','thumbs_up','Circle','Rock','W','Stop','cheese','tri','forward','double_peace','noise']
        self.dropdown_action = ctk.CTkComboBox(self.framet2,values=gest)
        self.dropdown_action.grid(row =0,column=1,padx =10,pady =10,sticky = 'w')

        label_action = ctk.CTkLabel(self.framet2,text='Choose Action to Map:',font=('Arial',16))
        label_action.grid(row =1,column=0,padx =10,pady =10,sticky = 'e')
        act = ['select_and_copy','pause_video','close_window','mute','open_notepad','paste','change_window','screenshot','news','fast_forward','play_songs','translate','lock_screen']
        self.dropdown_action2 = ctk.CTkComboBox(self.framet2,values=act)
        self.dropdown_action2.grid(row =1,column=1,padx =10,pady =10,sticky = 'w')

        self.framet3 = ctk.CTkFrame(tab2)
        self.framet3.pack(side='left',anchor='center',pady=50)

        #tab3
        def build_frame():
            self.flag=True
            framet4 = ctk.CTkFrame(tab3)
            framet4.pack(anchor='center',pady=50)
            ctk.CTkLabel(framet4,text='GESTURE',font=('arial bold',16)).grid(row=0,column=0,padx=10,sticky='e')
            ctk.CTkLabel(framet4,text='ACTION',font=('arial bold',16)).grid(row=0,column=1,padx=10,sticky='w')
            conn = sqlite3.connect('gestures.db')
            c = conn.cursor()
            c.execute('select action from gestures')
            acti=c.fetchall()
            acti = [i[0] for i in acti]
            for i,j,k in zip(gest,acti,[0,1,2,3,4,5,6,7,8,9,10,11,12]):
                    ctk.CTkLabel(framet4,text=i,font=('arial',14)).grid(row=k+1,column=0,padx=10,sticky='e')
                    ctk.CTkLabel(framet4,text=j,font=('arial',14)).grid(row=k+1,column=1,padx=10,sticky='w')
        
        
        def sql_op():
            conn = sqlite3.connect('gestures.db')
            c = conn.cursor()
            gest = self.dropdown_action.get()
            act = self.dropdown_action2.get()
            
            c.execute(f"update gestures set action='{act}' where gesture='{gest}'")
            conn.commit()
            conn.close()
        ctk.CTkButton(self.framet2,text='Apply Settings',command=sql_op).grid(row =2,column=0,columnspan=2,pady=10)

        root.mainloop()

    def insert_textbox(self, text,confidence):
        if text != self.prev_text :
            if (text == 'Circle' and confidence >=.995) or \
            (text == 'open_palm' and confidence >=.9999) or \
            (text == 'double_peace' and confidence >=.9999) or \
            (text == 'fist' and confidence >=.9999) or \
            (text == 'forward' and confidence >=.992) or \
            (text == 'Rock' and confidence >=.99) or \
            (text == 'Stop' and confidence >=.999) or \
            (text == 'thumbs_up' and confidence >=.9999) or \
            (text == 'tri' and confidence >=.999) or \
            (text == 'W' and confidence >=.999) or \
            (text == 'cheese' and confidence >=.999) or \
            (text == 'none' and confidence >=.99):
                
                self.textbox.insert('end', f'{text}\n')
                self.prev_text = text 
                if text != 'none':
                    conn = sqlite3.connect('gestures.db')
                    c = conn.cursor()
                    c.execute(f"select action from gestures where gesture='{text}'")
                    act = c.fetchone()
                    print(act)
                    getattr(self.sysop,act[0])()

    def pred(self):
        global ans
        sequence = []
        predictions = []
        threshold = 0.5
        model = tf.keras.models.load_model('action1.h5')
        cap = cv2.VideoCapture(0)
        # Set mediapipe model 
        with self.mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while cap.isOpened():

                # Read feed
                ret, frame = cap.read()

                # Make detections
                image, results = self.mediapipe_detection(frame, holistic)
                
                
                # Draw landmarks
                self.draw_styled_landmarks(image, results)
                
                # 2. Prediction logic
                keypoints = self.extract_keypoints(results)
                sequence.append(keypoints)
                sequence = sequence[-30:]
                
                if len(sequence) == 30:
                    res = model.predict(np.expand_dims(sequence, axis=0))[0]
                    
                    ac = (self.actions[np.argmax(res)])
                    confidence = res[np.argmax(res)]
                    print(ac , confidence)
                    self.insert_textbox(ac,confidence)
                    
                cv2.imshow('OpenCV Feed', image)
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break    
            
            cap.release()
            cv2.destroyAllWindows()
    