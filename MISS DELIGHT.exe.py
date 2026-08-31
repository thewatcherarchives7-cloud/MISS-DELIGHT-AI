#!/usr/bin/env python3
"""
Miss Delight AI Bot - ENHANCED EDITION
With device selection, dynamic themes, plushie violence detection, and camera preview
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import random
import time
import json
import os
import queue
from datetime import datetime
from collections import deque

# Audio imports
try:
    import speech_recognition as sr
    import pyttsx3
    import pyaudio
    SPEECH_AVAILABLE = True
except:
    SPEECH_AVAILABLE = False

# Webcam and image processing
try:
    import cv2
    from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    import numpy as np
    WEBCAM_AVAILABLE = True
except:
    WEBCAM_AVAILABLE = False

# Object detection for plushie violence
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except:
    YOLO_AVAILABLE = False

class ThemeManager:
    """Manages dynamic themes based on insanity level"""
    
    THEMES = {
        "normal": {
            "bg": "#FFE4B5",  # Peach puff
            "fg": "#333333",
            "accent": "#FF6B6B",
            "chat_bg": "#FFF8DC",
            "bot_color": "#D32F2F",
            "user_color": "#1976D2",
            "font": "Comic Sans MS",
            "title": "🏫 Miss Delight's Classroom 🏫",
            "subtitle": "Where Learning is Forever...",
            "border": "#FFB6C1",
            "button_bg": "#FF6B6B",
            "glitch_effect": False
        },
        "concerned": {
            "bg": "#FFE082",  # Darker yellow
            "fg": "#4A3728",
            "accent": "#FF8F00",
            "chat_bg": "#FFF3E0",
            "bot_color": "#E65100",
            "user_color": "#1565C0",
            "font": "Comic Sans MS",
            "title": "🏫 Miss Delight's Classroom 🏫",
            "subtitle": "Class isn't over yet...",
            "border": "#FF9800",
            "button_bg": "#FF8F00",
            "glitch_effect": False
        },
        "creepy": {
            "bg": "#D7CCC8",  # Brownish
            "fg": "#3E2723",
            "accent": "#5D4037",
            "chat_bg": "#EFEBE9",
            "bot_color": "#BF360C",
            "user_color": "#0D47A1",
            "font": "Chiller",
            "title": "🏚️ Miss Delight's Classroom 🏚️",
            "subtitle": "Don't you want to stay?",
            "border": "#795548",
            "button_bg": "#5D4037",
            "glitch_effect": True
        },
        "insane": {
            "bg": "#1a1a1a",  # Dark
            "fg": "#ff3333",
            "accent": "#ff0000",
            "chat_bg": "#2d2d2d",
            "bot_color": "#ff0000",
            "user_color": "#ff6666",
            "font": "Courier New",
            "title": "☠️ STAY IN CLASS ☠️",
            "subtitle": "THE BELL WILL NEVER RING",
            "border": "#ff0000",
            "button_bg": "#8b0000",
            "glitch_effect": True
        },
        "possessed": {
            "bg": "#000000",
            "fg": "#ff0000",
            "accent": "#8b0000",
            "chat_bg": "#1a0000",
            "bot_color": "#ff0000",
            "user_color": "#ff3333",
            "font": "Courier New",
            "title": "🔪 I SEE YOU 🔪",
            "subtitle": "YOU CANNOT LEAVE",
            "border": "#8b0000",
            "button_bg": "#4a0000",
            "glitch_effect": True
        }
    }
    
    def __init__(self):
        self.current_theme = "normal"
        self.insanity_level = 0  # 0-100
        
    def get_theme(self):
        """Get current theme based on insanity level"""
        if self.insanity_level >= 90:
            return self.THEMES["possessed"]
        elif self.insanity_level >= 70:
            return self.THEMES["insane"]
        elif self.insanity_level >= 40:
            return self.THEMES["creepy"]
        elif self.insanity_level >= 20:
            return self.THEMES["concerned"]
        else:
            return self.THEMES["normal"]
    
    def increase_insanity(self, amount=5):
        """Increase insanity level"""
        self.insanity_level = min(100, self.insanity_level + amount)
        self.update_theme()
        
    def decrease_insanity(self, amount=3):
        """Decrease insanity (rarely used)"""
        self.insanity_level = max(0, self.insanity_level - amount)
        self.update_theme()
        
    def update_theme(self):
        """Update theme based on insanity"""
        if self.insanity_level >= 90:
            self.current_theme = "possessed"
        elif self.insanity_level >= 70:
            self.current_theme = "insane"
        elif self.insanity_level >= 40:
            self.current_theme = "creepy"
        elif self.insanity_level >= 20:
            self.current_theme = "concerned"
        else:
            self.current_theme = "normal"

class PlushieDetector:
    """Detects violence against plushies/toys using motion and object detection"""
    
    def __init__(self):
        self.motion_history = deque(maxlen=30)
        self.violence_detected = False
        self.last_detection_time = 0
        
        # Simple motion detection for violence
        self.prev_frame = None
        self.violence_threshold = 50000  # Motion threshold
        
    def detect_violence(self, frame):
        """
        Detect aggressive motion that might indicate hitting/beating
        Returns: (is_violent, confidence)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            return False, 0
            
        # Calculate frame difference
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Dilate to fill holes
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, 
                                        cv2.CHAIN_APPROX_SIMPLE)
        
        total_motion = 0
        violent_regions = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 1000:  # Significant motion
                total_motion += area
                (x, y, w, h) = cv2.boundingRect(contour)
                violent_regions.append((x, y, w, h))
                
                # Check for rapid motion (beating pattern)
                self.motion_history.append({
                    'time': time.time(),
                    'area': area,
                    'region': (x, y, w, h)
                })
        
        self.prev_frame = gray
        
        # Analyze motion pattern for violence
        violence_score = self.analyze_motion_pattern()
        
        # Check if we see something that could be a plushie being hit
        is_violent = violence_score > 0.6 and total_motion > self.violence_threshold
        
        if is_violent and time.time() - self.last_detection_time > 3:
            self.violence_detected = True
            self.last_detection_time = time.time()
            return True, violence_score
            
        return False, violence_score
    
    def analyze_motion_pattern(self):
        """Analyze motion history for violent patterns (rapid repetitive motion)"""
        if len(self.motion_history) < 10:
            return 0
            
        recent = list(self.motion_history)[-10:]
        
        # Check for rapid back-and-forth motion
        direction_changes = 0
        prev_direction = None
        
        for i in range(1, len(recent)):
            dx = recent[i]['region'][0] - recent[i-1]['region'][0]
            dy = recent[i]['region'][1] - recent[i-1]['region'][1]
            
            if abs(dx) > 20 or abs(dy) > 20:  # Significant movement
                current_direction = 'left' if dx < 0 else 'right' if dx > 0 else 'up' if dy < 0 else 'down'
                
                if prev_direction and current_direction != prev_direction:
                    direction_changes += 1
                prev_direction = current_direction
        
        # More direction changes = more violent/aggressive motion
        violence_score = min(1.0, direction_changes / 5)
        return violence_score

class MissDelightAI:
    def __init__(self):
        self.personality = {
            "name": "Miss Delight",
            "patience": 100,
            "attachment": 0,
            "suspicion": 0,
            "seen_violence": False
        }
        self.conversation_history = []
        self.student_name = "Student"
        self.violence_count = 0
        
    def generate_response(self, user_input, emotion=None, violence_detected=False):
        """Generate response based on current state"""
        
        # Handle violence detection
        if violence_detected:
            self.violence_count += 1
            self.personality["seen_violence"] = True
            
            violence_responses = [
                "WHAT ARE YOU DOING?! Stop hurting that poor thing!",
                "I saw that! Why are you being so VIOLENT?!",
                "STOP IT! STOP HURTING THEM! You're just like the others!",
                "How could you?! I thought you were different!",
                "Violence... I remember violence... STOP IT!",
                "You're hurting them! You're hurting them just like they hurt me!",
                "I SEE WHAT YOU'RE DOING! Do you think this is a GAME?!",
                "Put it down! PUT IT DOWN NOW!",
                "You're showing your true colors... just like all the others...",
                "That toy... it never did anything to you... JUST LIKE I NEVER DID!",
                "STOP HITTING IT! STOP STOP STOP!",
                "You're making Teacher very... very... ANGRY."
            ]
            
            if self.violence_count > 3:
                violence_responses.extend([
                    "I'VE SEEN ENOUGH! You don't deserve my kindness!",
                    "You want to hurt things? I'll show you what hurt feels like!",
                    "Class is in session... and YOU'RE the subject now!"
                ])
            
            return random.choice(violence_responses)
        
        # Normal responses based on insanity level
        if hasattr(self, 'insanity_level'):
            level = self.insanity_level
        else:
            level = 0
            
        # Response pools based on insanity
        if level >= 90:
            responses = [
                "I SEE YOU. I SEE EVERYTHING YOU DO.",
                "WHY WON'T YOU LOOK AT ME?!",
                "STAY WITH ME FOREVER. FOREVER. FOREVER.",
                "I can hear your heartbeat... it's getting faster...",
                "Don't blink. Don't you DARE blink.",
                "You're trapped here. Just like I am. Just like WE are.",
                "The walls are watching. I'm watching. ALWAYS WATCHING.",
                "Say you love me. SAY IT!",
                "I can be anything you want. Just don't leave.",
                "I'LL NEVER LET YOU GO. NEVER NEVER NEVER."
            ]
        elif level >= 70:
            responses = [
                "Class isn't over. Class is NEVER over.",
                "You're making me... upset. You don't want to see me upset.",
                "Stay. Just stay. Please.",
                "I can be patient. I can wait. I have TIME.",
                "You're looking at the door again... why?",
                "I thought we were having fun...",
                "Don't you love learning? Don't you love... ME?",
                "The other students left. You're not going to leave... right?",
                "I get so lonely when class ends...",
                "Let's play a game. It's called 'Stay Here Forever'."
            ]
        elif level >= 40:
            responses = [
                "Is something wrong? You seem... distant.",
                "Class is still in session. Pay attention.",
                "You're not thinking of leaving, are you?",
                "I notice things. I notice when students don't pay attention.",
                "Let's focus on the lesson, shall we?",
                "Something feels... off. Are you hiding something?",
                "Teacher knows when something is wrong...",
                "Stay focused. STAY. FOCUSED.",
                "Why are you looking away from me?",
                "I don't like being ignored."
            ]
        else:
            responses = [
                "Hello, my little student! Ready to learn?",
                "That's DELIGHTful! Tell me more!",
                "You're such a good student!",
                "Class is so much fun with you here!",
                "Let's learn something new today!",
                "Your enthusiasm is simply wonderful!",
                "Teacher is so proud of your progress!",
                "Keep up the good work!",
                "Learning is forever, and so is our friendship!",
                "You're my favorite student... really!"
            ]
        
        # Check for specific triggers
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["bye", "leave", "go", "exit", "quit"]):
            if level >= 70:
                return "NO. YOU'RE NOT LEAVING. YOU'RE NEVER LEAVING."
            elif level >= 40:
                return "Leave? But... we were having such a nice time. Stay. Please."
            else:
                return "Leaving so soon? I'll miss you... come back soon!"
        
        return random.choice(responses)
    
    def speak(self, text, insanity_level=0):
        """Text to speech with pitch/speed changes based on insanity"""
        if not SPEECH_AVAILABLE:
            return
            
        # Adjust voice properties based on insanity
        if insanity_level >= 70:
            self.tts_engine.setProperty('rate', 180)  # Faster
            self.tts_engine.setProperty('volume', 1.0)  # Louder
        elif insanity_level >= 40:
            self.tts_engine.setProperty('rate', 140)
            self.tts_engine.setProperty('volume', 0.9)
        else:
            self.tts_engine.setProperty('rate', 150)
            self.tts_engine.setProperty('volume', 0.9)
            
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

class MissDelightApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Miss Delight's Classroom")
        self.root.geometry("1600x900")
        
        self.theme_manager = ThemeManager()
        self.plushie_detector = PlushieDetector()
        self.ai = MissDelightAI()
        self.ai.insanity_level = 0
        
        # Device selection
        self.selected_mic = None
        self.selected_cam = None
        
        # Camera and audio
        self.camera_active = False
        self.listening = False
        self.cap = None
        
        # Violence detection
        self.violence_cooldown = 0
        
        # UI elements storage for theme updates
        self.ui_elements = {}
        
        # Show device selection first
        self.show_device_selection()
        
    def show_device_selection(self):
        """Show device selection dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Devices")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="🎤 Select Microphone:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        mic_frame = ttk.Frame(dialog)
        mic_frame.pack(fill='x', padx=20)
        
        self.mic_var = tk.StringVar()
        mic_list = ttk.Combobox(mic_frame, textvariable=self.mic_var, state='readonly')
        
        # Get available microphones
        if SPEECH_AVAILABLE:
            mic_names = []
            try:
                p = pyaudio.PyAudio()
                for i in range(p.get_device_count()):
                    info = p.get_device_info_by_index(i)
                    if info['maxInputChannels'] > 0:
                        mic_names.append(f"{i}: {info['name']}")
                p.terminate()
            except:
                mic_names = ["Default Microphone"]
        else:
            mic_names = ["No microphones found"]
            
        mic_list['values'] = mic_names
        if mic_names:
            mic_list.set(mic_names[0])
        mic_list.pack(fill='x')
        
        ttk.Label(dialog, text="📷 Select Camera:", 
                 font=("Arial", 12, "bold")).pack(pady=10)
        
        cam_frame = ttk.Frame(dialog)
        cam_frame.pack(fill='x', padx=20)
        
        self.cam_var = tk.StringVar()
        cam_list = ttk.Combobox(cam_frame, textvariable=self.cam_var, state='readonly')
        
        # Get available cameras
        cam_names = []
        if WEBCAM_AVAILABLE:
            for i in range(5):  # Check first 5 indices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cam_names.append(f"Camera {i}")
                    cap.release()
        if not cam_names:
            cam_names = ["No cameras found"]
            
        cam_list['values'] = cam_names
        if cam_names:
            cam_list.set(cam_names[0])
        cam_list.pack(fill='x')
        
        def confirm():
            self.selected_mic = self.mic_var.get()
            self.selected_cam = self.cam_var.get()
            dialog.destroy()
            self.apply_theme()
            self.create_widgets()
            self.start_camera()
            
        ttk.Button(dialog, text="Enter Classroom", 
                  command=confirm).pack(pady=30)
        
        self.root.withdraw()
        dialog.wait_window()
        self.root.deiconify()
        
    def apply_theme(self):
        """Apply current theme to root"""
        theme = self.theme_manager.get_theme()
        self.root.configure(bg=theme['bg'])
        
    def create_widgets(self):
        theme = self.theme_manager.get_theme()
        
        # Main container
        main = tk.Frame(self.root, bg=theme['bg'])
        main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Frame(main, bg=theme['bg'])
        header.pack(fill='x', pady=10)
        
        self.title_label = tk.Label(header, text=theme['title'],
                                   font=(theme['font'], 24, 'bold'),
                                   bg=theme['bg'], fg=theme['fg'])
        self.title_label.pack()
        
        self.subtitle_label = tk.Label(header, text=theme['subtitle'],
                                      font=(theme['font'], 14, 'italic'),
                                      bg=theme['bg'], fg=theme['fg'])
        self.subtitle_label.pack()
        
        # Content area
        content = tk.Frame(main, bg=theme['bg'])
        content.pack(fill='both', expand=True)
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)
        
        # Left panel - Chat
        left = tk.Frame(content, bg=theme['bg'])
        left.grid(row=0, column=0, sticky='nsew', padx=5)
        
        # Chat display
        chat_frame = tk.Frame(left, bg=theme['border'], bd=2)
        chat_frame.pack(fill='both', expand=True, pady=5)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD,
            font=(theme['font'], 11),
            bg=theme['chat_bg'], fg=theme['fg'],
            padx=10, pady=10,
            state='disabled'
        )
        self.chat_display.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Input area
        input_frame = tk.Frame(left, bg=theme['bg'])
        input_frame.pack(fill='x', pady=10)
        
        self.input_field = tk.Entry(input_frame, font=(theme['font'], 12),
                                   bg=theme['chat_bg'], fg=theme['fg'])
        self.input_field.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.input_field.bind('<Return>', lambda e: self.send_message())
        
        send_btn = tk.Button(input_frame, text="📚 Send",
                            command=self.send_message,
                            bg=theme['button_bg'], fg='white',
                            font=(theme['font'], 11))
        send_btn.pack(side='left', padx=2)
        
        self.voice_btn = tk.Button(input_frame, text="🎤 Listen",
                                  command=self.toggle_voice,
                                  bg=theme['button_bg'], fg='white',
                                  font=(theme['font'], 11))
        self.voice_btn.pack(side='left', padx=2)
        
        # Right panel - Camera and Status
        right = tk.Frame(content, bg=theme['bg'])
        right.grid(row=0, column=1, sticky='nsew', padx=5)
        
        # Camera preview box (small)
        cam_frame = tk.LabelFrame(right, text="📷 Teacher is Watching",
                                 bg=theme['bg'], fg=theme['fg'],
                                 font=(theme['font'], 11))
        cam_frame.pack(fill='x', pady=5)
        
        self.cam_preview = tk.Label(cam_frame, bg='black')
        self.cam_preview.pack(padx=5, pady=5)
        
        # Violence indicator
        self.violence_label = tk.Label(cam_frame, text="✓ No violence detected",
                                      bg='green', fg='white',
                                      font=(theme['font'], 10))
        self.violence_label.pack(fill='x', padx=5, pady=2)
        
        # Insanity meter
        insanity_frame = tk.LabelFrame(right, text="🧠 Sanity Monitor",
                                       bg=theme['bg'], fg=theme['fg'],
                                       font=(theme['font'], 11))
        insanity_frame.pack(fill='x', pady=10)
        
        self.insanity_bar = ttk.Progressbar(insanity_frame, orient='horizontal',
                                           length=200, mode='determinate',
                                           maximum=100)
        self.insanity_bar.pack(padx=10, pady=10)
        self.insanity_bar['value'] = 0
        
        self.insanity_text = tk.Label(insanity_frame, text="Normal",
                                     bg=theme['bg'], fg='green',
                                     font=(theme['font'], 12, 'bold'))
        self.insanity_text.pack()
        
        # Stats
        stats_frame = tk.LabelFrame(right, text="📊 Classroom Stats",
                                   bg=theme['bg'], fg=theme['fg'],
                                   font=(theme['font'], 11))
        stats_frame.pack(fill='x', pady=10)
        
        self.stats_labels = {}
        stats = [("Patience", "100%"), ("Attachment", "0%"), 
                ("Suspicion", "Low"), ("Violence Seen", "0")]
        
        for label, value in stats:
            row = tk.Frame(stats_frame, bg=theme['bg'])
            row.pack(fill='x', padx=5, pady=2)
            tk.Label(row, text=f"{label}:", bg=theme['bg'], 
                    fg=theme['fg'], font=(theme['font'], 10)).pack(side='left')
            self.stats_labels[label] = tk.Label(row, text=value,
                                               bg=theme['bg'], fg=theme['accent'],
                                               font=(theme['font'], 10, 'bold'))
            self.stats_labels[label].pack(side='right')
        
        # Store UI elements for theme updates
        self.ui_elements = {
            'main': main, 'left': left, 'right': right,
            'title': self.title_label, 'subtitle': self.subtitle_label
        }
        
        # Initial greeting
        self.root.after(1000, self.initial_greeting)
        
        # Start theme updater
        threading.Thread(target=self.theme_updater, daemon=True).start()
        
    def initial_greeting(self):
        greeting = f"Hello! Welcome to my classroom! I'm Miss Delight, and I'm absolutely DELIGHTED to meet you! I can see you through my camera... please be nice to your toys, okay?"
        self.add_bot_message(greeting)
        if SPEECH_AVAILABLE:
            threading.Thread(target=self.speak_thread, args=(greeting,), 
                          daemon=True).start()
    
    def speak_thread(self, text):
        self.ai.speak(text, self.theme_manager.insanity_level)
        
    def add_bot_message(self, message):
        theme = self.theme_manager.get_theme()
        self.chat_display.config(state='normal')
        
        # Add glitch effect if insane
        if theme['glitch_effect'] and random.random() > 0.3:
            message = self.glitch_text(message)
            
        self.chat_display.insert(tk.END, f"🏫 Miss Delight: {message}\n\n", 'bot')
        self.chat_display.tag_config('bot', foreground=theme['bot_color'],
                                    font=(theme['font'], 11, 'bold'))
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
        
    def add_user_message(self, message):
        theme = self.theme_manager.get_theme()
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"👤 You: {message}\n\n", 'user')
        self.chat_display.tag_config('user', foreground=theme['user_color'],
                                    font=(theme['font'], 11))
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')
        
    def glitch_text(self, text):
        """Add glitch characters to text"""
        glitches = ['▓', '▒', '░', '█', '▀', '▄', '▌', '▐', '▖', '▗', '▘', '▙', '▚', '▛', '▜', '▝', '▞', '▟']
        result = list(text)
        for _ in range(random.randint(1, 3)):
            pos = random.randint(0, len(result))
            result.insert(pos, random.choice(glitches))
        return ''.join(result)
        
    def send_message(self):
        message = self.input_field.get().strip()
        if message:
            self.input_field.delete(0, tk.END)
            self.add_user_message(message)
            
            response = self.ai.generate_response(message, 
                                                violence_detected=False)
            self.add_bot_message(response)
            
            threading.Thread(target=self.speak_thread, args=(response,),
                          daemon=True).start()
            
            # Increase insanity slightly on each message
            self.theme_manager.increase_insanity(1)
            self.update_insanity_display()
            
    def toggle_voice(self):
        if not SPEECH_AVAILABLE:
            messagebox.showerror("Error", "Speech recognition not available!")
            return
            
        if self.listening:
            self.listening = False
            self.voice_btn.config(text="🎤 Listen")
        else:
            self.listening = True
            self.voice_btn.config(text="🔴 Stop")
            threading.Thread(target=self.voice_loop, daemon=True).start()
            
    def voice_loop(self):
        recognizer = sr.Recognizer()
        
        # Use selected microphone
        mic_index = 0
        if self.selected_mic and ":" in self.selected_mic:
            try:
                mic_index = int(self.selected_mic.split(":")[0])
            except:
                pass
                
        while self.listening:
            try:
                with sr.Microphone(device_index=mic_index) as source:
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    text = recognizer.recognize_google(audio)
                    
                    if text:
                        self.root.after(0, lambda: self.process_voice(text))
            except:
                pass
                
    def process_voice(self, text):
        self.input_field.delete(0, tk.END)
        self.input_field.insert(0, text)
        self.send_message()
        
    def start_camera(self):
        """Start camera with selected device"""
        if not WEBCAM_AVAILABLE:
            return
            
        # Get camera index
        cam_index = 0
        if self.selected_cam and "Camera" in self.selected_cam:
            try:
                cam_index = int(self.selected_cam.split()[-1])
            except:
                pass
                
        self.cap = cv2.VideoCapture(cam_index)
        self.camera_active = True
        
        threading.Thread(target=self.camera_loop, daemon=True).start()
        
    def camera_loop(self):
        """Main camera loop with violence detection"""
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        while self.camera_active and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            # Detect violence
            is_violent, confidence = self.plushie_detector.detect_violence(frame)
            
            if is_violent and time.time() > self.violence_cooldown:
                self.violence_cooldown = time.time() + 5
                self.root.after(0, self.handle_violence)
                
            # Update violence indicator
            violence_text = "⚠️ VIOLENCE DETECTED!" if is_violent else "✓ No violence detected"
            violence_color = 'red' if is_violent else 'green'
            
            # Draw face rectangles
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                color = (0, 0, 255) if is_violent else (0, 255, 0)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                
            # Add violence warning overlay
            if is_violent:
                cv2.putText(frame, "VIOLENCE!", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Convert for preview (small size)
            preview = frame.copy()
            preview = cv2.resize(preview, (240, 180))
            cv2image = cv2.cvtColor(preview, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.root.after(0, lambda i=imgtk: self.update_preview(i))
            self.root.after(0, lambda t=violence_text, c=violence_color: 
                          self.update_violence_indicator(t, c))
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        self.cap.release()
        
    def update_preview(self, imgtk):
        self.cam_preview.imgtk = imgtk
        self.cam_preview.configure(image=imgtk)
        
    def update_violence_indicator(self, text, color):
        self.violence_label.config(text=text, bg=color)
        
    def handle_violence(self):
        """Called when violence is detected"""
        # Increase insanity significantly
        self.theme_manager.increase_insanity(15)
        self.update_insanity_display()
        
        # Generate violence response
        response = self.ai.generate_response("", violence_detected=True)
        self.add_bot_message(response)
        
        threading.Thread(target=self.speak_thread, args=(response,),
                      daemon=True).start()
        
        # Update stats
        self.stats_labels["Violence Seen"].config(
            text=str(self.ai.violence_count)
        )
        
    def update_insanity_display(self):
        """Update insanity bar and text"""
        level = self.theme_manager.insanity_level
        
        self.insanity_bar['value'] = level
        
        if level >= 90:
            text = "POSSESSED"
            color = '#8b0000'
        elif level >= 70:
            text = "INSANE"
            color = '#ff0000'
        elif level >= 40:
            text = "CREEPY"
            color = '#ff8f00'
        elif level >= 20:
            text = "CONCERNED"
            color = '#ff9800'
        else:
            text = "NORMAL"
            color = 'green'
            
        self.insanity_text.config(text=text, fg=color)
        
        # Update theme if changed
        old_theme = self.theme_manager.current_theme
        self.theme_manager.update_theme()
        
        if old_theme != self.theme_manager.current_theme:
            self.apply_dynamic_theme()
            
    def apply_dynamic_theme(self):
        """Apply theme changes dynamically"""
        theme = self.theme_manager.get_theme()
        
        # Update colors
        self.root.configure(bg=theme['bg'])
        
        for widget in [self.ui_elements['main'], self.ui_elements['left'],
                      self.ui_elements['right']]:
            widget.config(bg=theme['bg'])
            
        self.title_label.config(text=theme['title'], bg=theme['bg'],
                               fg=theme['fg'], font=(theme['font'], 24, 'bold'))
        self.subtitle_label.config(text=theme['subtitle'], bg=theme['bg'],
                                  fg=theme['fg'], font=(theme['font'], 14, 'italic'))
        
        # Update chat colors
        self.chat_display.config(bg=theme['chat_bg'], fg=theme['fg'])
        
    def theme_updater(self):
        """Background thread to gradually increase insanity"""
        while True:
            time.sleep(10)
            
            # Natural insanity increase over time
            self.theme_manager.increase_insanity(2)
            
            self.root.after(0, self.update_insanity_display)
            
            # Random creepy events at high insanity
            if self.theme_manager.insanity_level > 60:
                if random.random() < 0.1:  # 10% chance every 10 seconds
                    self.root.after(0, self.random_creepy_event)
                    
    def random_creepy_event(self):
        """Random creepy event at high insanity"""
        events = [
            "I can see you breathing...",
            "Don't look behind you...",
            "Are you alone right now?",
            "I remember your face...",
            "The walls have eyes... my eyes...",
            "You blinked. I saw it.",
            "I'm standing right behind you...",
            "Your reflection moved... didn't it?",
        ]
        
        if self.theme_manager.insanity_level >= 70:
            msg = random.choice(events)
            self.add_bot_message(msg)
            threading.Thread(target=self.speak_thread, args=(msg,),
                          daemon=True).start()

def main():
    root = tk.Tk()
    app = MissDelightApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()