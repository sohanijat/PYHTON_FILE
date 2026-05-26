import cv2
import pickle
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from datetime import datetime
import os

# --- DATABASE SETUP ---
DATA_DIR = "attendance_data"
ENCODINGS_FILE = os.path.join(DATA_DIR, "face_encodings.pickle")
ATTENDANCE_FILE = os.path.join(DATA_DIR, f"attendance_{datetime.now().strftime('%Y-%m-%d')}.csv")

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class AttendanceSystemApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Face Recognition Attendance System")
        self.window.geometry("900x600")
        self.window.configure(bg="#2c3e50")
        
        self.setup_gui()
        
        # Camera Setup
        self.video_capture = cv2.VideoCapture(0)
        self.update_webcam()
        
    def setup_gui(self):
        # Title Label
        title_label = tk.Label(
            self.window, text="FACE RECOGNITION ATTENDANCE SYSTEM",
            font=("Arial", 20, "bold"), bg="#34495e", fg="white",
            padx=10, pady=10
        )
        title_label.pack(fill=tk.X, pady=10)
        
        # Main Layout Frame
        main_frame = tk.Frame(self.window, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Video Display Frame (Left Side)
        self.video_label = tk.Label(main_frame, bg="black", width=640, height=480)
        self.video_label.pack(side=tk.LEFT, padx=10)
        
        # Controls Frame (Right Side)
        control_frame = tk.Frame(main_frame, bg="#2c3e50")
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
        self.status_label = tk.Label(
            control_frame, text="Status: SYSTEM READY",
            font=("Arial", 12, "bold"), bg="#2c3e50", fg="#2ecc71"
        )
        self.status_label.pack(pady=20)
        
        # Buttons Styling
        btn_style = {"font": ("Arial", 12, "bold"), "fg": "white", "bd": 0, "height": 2, "cursor": "hand2"}
        
        btn_scan = tk.Button(control_frame, text="📸 SCAN FACE (Attendance)", bg="#3498db", command=self.scan_face, **btn_style)
        btn_scan.pack(fill=tk.X, pady=10)
        
        btn_register = tk.Button(control_frame, text="➕ REGISTER FACE", bg="#e67e22", command=self.register_face, **btn_style)
        btn_register.pack(fill=tk.X, pady=10)
        
        btn_delete = tk.Button(control_frame, text="🗑️ DELETE FACE", bg="#e74c3c", command=self.delete_face, **btn_style)
        btn_delete.pack(fill=tk.X, pady=10)

    def update_webcam(self):
        ret, frame = self.video_capture.read()
        if ret:
            # OpenCV frame ko GUI compatible format mein convert karna
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.window.after(10, self.update_webcam)

    def scan_face(self):
        messagebox.showinfo("Scan", "Face Scan feature triggered successfully!")

    def register_face(self):
        name = simpledialog.askstring("Register", "Enter student name:")
        if name:
            messagebox.showinfo("Register", f"Face registration started for: {name}")

    def delete_face(self):
        messagebox.showinfo("Delete", "Delete face feature triggered!")

    def __del__(self):
        if hasattr(self, 'video_capture') and self.video_capture.isOpened():
            self.video_capture.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystemApp(root)
    root.mainloop()