import os
import sys

# ---------- PYTHON PATH FIX ----------
models_path = r"C:\Users\SOHANI\AppData\Local\Programs\Python\Python314\Lib\site-packages"

if models_path not in sys.path:
    sys.path.append(models_path)

# ---------- FACE RECOGNITION FIX ----------
try:
    import face_recognition_models
    sys.modules['face_recognition_models'] = face_recognition_models
except ImportError:
    print("face_recognition_models not found")

# ---------- IMPORTS ----------
import face_recognition
import cv2
import pickle
import numpy as np
import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from datetime import datetime
import threading

# ---------- VOICE ----------
try:
    import win32com.client

    def speak(text):
        def run_speech():
            try:
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Speak(text)
            except:
                pass

        threading.Thread(target=run_speech, daemon=True).start()

except:
    def speak(text):
        pass


# ---------- DATABASE ----------
DATA_DIR = "attendance_data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

ENCODINGS_FILE = os.path.join(DATA_DIR, "face_encodings.pickle")

ATTENDANCE_FILE = os.path.join(
    DATA_DIR,
    f"attendance_{datetime.now().strftime('%Y-%m-%d')}.csv"
)


# ---------- MAIN CLASS ----------
class AttendanceSystemApp:

    def __init__(self, window):

        self.window = window
        self.window.title("Smart Face Attendance System")
        self.window.geometry("1000x650")
        self.window.configure(bg="#1e272e")

        self.known_encodings = []
        self.known_names = []

        self.load_database()

        self.last_marked_user = None
        self.last_marked_time = datetime.now()

        self.setup_gui()

        # CAMERA
        self.video_capture = cv2.VideoCapture(0)

        if not self.video_capture.isOpened():
            messagebox.showerror("Camera Error", "Webcam not detected")
            return

        self.update_system_loop()

    # ---------- LOAD DATABASE ----------
    def load_database(self):

        if os.path.exists(ENCODINGS_FILE):

            with open(ENCODINGS_FILE, "rb") as f:

                data = pickle.load(f)

                self.known_encodings = data.get("encodings", [])
                self.known_names = data.get("names", [])

    # ---------- GUI ----------
    def setup_gui(self):

        header_frame = tk.Frame(self.window, bg="#2f3542", height=80)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(
            header_frame,
            text="SMART ATTENDANCE DASHBOARD",
            font=("Arial", 18, "bold"),
            bg="#2f3542",
            fg="white"
        )

        title_label.pack(side=tk.LEFT, padx=20, pady=20)

        self.clock_label = tk.Label(
            header_frame,
            text="",
            font=("Consolas", 16, "bold"),
            bg="#2f3542",
            fg="#eccc68"
        )

        self.clock_label.pack(side=tk.RIGHT, padx=20)

        main_frame = tk.Frame(self.window, bg="#1e272e")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # VIDEO
        self.video_label = tk.Label(main_frame, bg="black")
        self.video_label.pack(side=tk.LEFT, padx=10, pady=10)

        # RIGHT PANEL
        control_frame = tk.Frame(main_frame, bg="#2f3542", width=300)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_label = tk.Label(
            control_frame,
            text="Status : SCANNING ACTIVE",
            font=("Arial", 12, "bold"),
            bg="#2f3542",
            fg="#2ed573"
        )

        self.status_label.pack(pady=20)

        # BUTTON STYLE
        btn_style = {
            "font": ("Arial", 11, "bold"),
            "fg": "white",
            "bd": 0,
            "height": 2,
            "cursor": "hand2"
        }

        # REGISTER BUTTON
        register_btn = tk.Button(
            control_frame,
            text="REGISTER NEW EMPLOYEE",
            bg="#ffa502",
            command=self.register_face,
            **btn_style
        )

        register_btn.pack(fill=tk.X, padx=20, pady=10)

        # DELETE BUTTON
        delete_btn = tk.Button(
            control_frame,
            text="CLEAR DATABASE",
            bg="#ff4757",
            command=self.delete_face,
            **btn_style
        )

        delete_btn.pack(fill=tk.X, padx=20, pady=10)

    # ---------- CAMERA LOOP ----------
    def update_system_loop(self):

        now = datetime.now()

        self.clock_label.config(
            text=now.strftime("%d-%m-%Y  %H:%M:%S")
        )

        ret, frame = self.video_capture.read()

        if ret:

            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            rgb_small_frame = cv2.cvtColor(
                small_frame,
                cv2.COLOR_BGR2RGB
            )

            face_locations = face_recognition.face_locations(rgb_small_frame)

            face_encodings = face_recognition.face_encodings(
                rgb_small_frame,
                face_locations
            )

            for (top, right, bottom, left), face_encoding in zip(
                face_locations,
                face_encodings
            ):

                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                name = "Unknown"
                box_color = (0, 0, 255)

                if len(self.known_encodings) > 0:

                    matches = face_recognition.compare_faces(
                        self.known_encodings,
                        face_encoding,
                        tolerance=0.5
                    )

                    face_distances = face_recognition.face_distance(
                        self.known_encodings,
                        face_encoding
                    )

                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:

                        name = self.known_names[best_match_index]
                        box_color = (0, 255, 0)

                # DRAW RECTANGLE
                cv2.rectangle(
                    frame,
                    (left, top),
                    (right, bottom),
                    box_color,
                    2
                )

                cv2.putText(
                    frame,
                    name,
                    (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )

                # ATTENDANCE
                if name != "Unknown":

                    current_time = datetime.now()

                    if (
                        self.last_marked_user != name
                        or
                        (current_time - self.last_marked_time).seconds > 30
                    ):

                        self.log_attendance(name)

            # SHOW FRAME IN TKINTER
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            img = Image.fromarray(cv2image)

            imgtk = ImageTk.PhotoImage(image=img)

            self.video_label.imgtk = imgtk

            self.video_label.configure(image=imgtk)

        self.window.after(10, self.update_system_loop)

    # ---------- LOG ATTENDANCE ----------
    def log_attendance(self, name):

        now = datetime.now()

        time_string = now.strftime("%H:%M:%S")

        date_string = now.strftime("%Y-%m-%d")

        file_is_empty = (
            not os.path.exists(ATTENDANCE_FILE)
            or
            os.stat(ATTENDANCE_FILE).st_size == 0
        )

        with open(ATTENDANCE_FILE, "a") as f:

            if file_is_empty:
                f.write("Employee Name,Date,Time\n")

            f.write(f"{name},{date_string},{time_string}\n")

        self.status_label.config(
            text=f"Attendance Marked : {name}",
            fg="#2ed573"
        )

        self.last_marked_user = name
        self.last_marked_time = now

        speak(f"Attendance marked for {name}")

    # ---------- REGISTER FACE ----------
    def register_face(self):

        ret, frame = self.video_capture.read()

        if not ret:
            messagebox.showerror("Error", "Camera capture failed")
            return

        name = simpledialog.askstring(
            "Registration",
            "Enter Employee Name"
        )

        if not name:
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame)

        face_encodings = face_recognition.face_encodings(
            rgb_frame,
            face_locations
        )

        if len(face_encodings) == 0:

            messagebox.showwarning(
                "Failed",
                "No face detected"
            )

            return

        self.known_encodings.append(face_encodings[0])

        self.known_names.append(name)

        with open(ENCODINGS_FILE, "wb") as f:

            pickle.dump(
                {
                    "encodings": self.known_encodings,
                    "names": self.known_names
                },
                f
            )

        messagebox.showinfo(
            "Success",
            f"{name} registered successfully"
        )

    # ---------- DELETE DATABASE ----------
    def delete_face(self):

        confirm = messagebox.askyesno(
            "Warning",
            "Delete complete database?"
        )

        if confirm:

            if os.path.exists(ENCODINGS_FILE):
                os.remove(ENCODINGS_FILE)

            self.known_encodings = []
            self.known_names = []

            self.status_label.config(
                text="DATABASE CLEARED",
                fg="#ff4757"
            )

            messagebox.showinfo(
                "Deleted",
                "Database cleared successfully"
            )

    # ---------- CLOSE ----------
    def __del__(self):

        if hasattr(self, 'video_capture'):

            self.video_capture.release()


# ---------- MAIN ----------
if __name__ == "__main__":

    root = tk.Tk()

    app = AttendanceSystemApp(root)

    root.mainloop()