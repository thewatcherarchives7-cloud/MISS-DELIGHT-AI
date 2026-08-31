#!/usr/bin/env python3
"""
Advanced Training Module for Miss Delight
Train her to recognize you better!
"""

import cv2
import numpy as np
import json
import os
from datetime import datetime

class MissDelightTrainer:
    def __init__(self):
        self.data_dir = "training_data"
        os.makedirs(self.data_dir, exist_ok=True)
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
    def capture_training_data(self, label="student", samples=50):
        """Capture face samples for training"""
        cap = cv2.VideoCapture(0)
        count = 0
        
        print(f"[*] Capturing {samples} samples for '{label}'")
        print("[*] Look at the camera and move your head slightly...")
        print("[*] Press 'q' to quit early")
        
        while count < samples:
            ret, frame = cap.read()
            if not ret:
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                # Extract face
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (200, 200))
                
                # Save sample
                filename = f"{self.data_dir}/{label}_{count}.jpg"
                cv2.imwrite(filename, face_roi)
                
                # Draw rectangle
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Sample {count+1}/{samples}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                           1, (0, 255, 0), 2)
                
                count += 1
                print(f"  Captured sample {count}/{samples}")
                
            cv2.imshow('Training - Miss Delight is Watching', frame)
            
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()
        print(f"[+] Captured {count} samples!")
        
    def train_recognizer(self):
        """Train face recognizer"""
        print("[*] Training face recognizer...")
        
        faces = []
        labels = []
        label_map = {}
        current_label = 0
        
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.jpg'):
                path = os.path.join(self.data_dir, filename)
                label = filename.split('_')[0]
                
                if label not in label_map:
                    label_map[label] = current_label
                    current_label += 1
                    
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                faces.append(img)
                labels.append(label_map[label])
                
        if len(faces) == 0:
            print("[-] No training data found!")
            return None
            
        # Create and train recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        
        # Save model
        model_file = "miss_delight_trained.yml"
        recognizer.save(model_file)
        
        # Save label map
        with open("label_map.json", "w") as f:
            json.dump(label_map, f)
            
        print(f"[+] Model saved to {model_file}")
        print(f"[+] Trained on {len(faces)} images")
        
        return recognizer, label_map
        
    def recognize_face(self):
        """Test face recognition"""
        if not os.path.exists("miss_delight_trained.yml"):
            print("[-] No trained model found! Run training first.")
            return
            
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("miss_delight_trained.yml")
        
        with open("label_map.json", "r") as f:
            label_map = json.load(f)
            
        # Invert map
        id_to_label = {v: k for k, v in label_map.items()}
        
        cap = cv2.VideoCapture(0)
        
        print("[*] Recognition active! Press 'q' to quit.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (200, 200))
                
                label_id, confidence = recognizer.predict(face_roi)
                label = id_to_label.get(label_id, "Unknown")
                
                # Draw results
                color = (0, 255, 0) if confidence < 100 else (0, 0, 255)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, f"{label} ({confidence:.1f})", 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.9, color, 2)
                           
            cv2.imshow('Miss Delight Recognition', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cap.release()
        cv2.destroyAllWindows()

def main():
    trainer = MissDelightTrainer()
    
    print("=" * 50)
    print("🏫 Miss Delight Advanced Training")
    print("=" * 50)
    print("\n1. Capture training data")
    print("2. Train recognizer")
    print("3. Test recognition")
    print("4. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        name = input("Enter your name (label): ").strip() or "student"
        samples = int(input("Number of samples (default 50): ").strip() or "50")
        trainer.capture_training_data(name, samples)
    elif choice == "2":
        trainer.train_recognizer()
    elif choice == "3":
        trainer.recognize_face()
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()