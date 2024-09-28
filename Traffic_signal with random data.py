import tkinter as tk
from tkinter import ttk
import random
import threading
import time

class ModernTrafficSignalUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Traffic Signal System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f4f8")  # Light blue-grey background

        self.directions = ['North', 'South', 'East', 'West']
        self.vehicle_counts = [random.randint(15, 20) for _ in range(4)]
        self.current_signal = ["RED" for _ in range(4)]
        self.emergency_vehicles = [0 for _ in range(4)]
        self.waiting_times = [0 for _ in range(4)]
        
        self.signal_frames = []
        self.signal_labels = []
        self.vehicle_labels = []
        self.emergency_labels = []
        self.waiting_time_labels = []

        self.create_widgets()
        self.start_simulation()

    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#ffffff", pady=20)
        header_frame.pack(fill=tk.X)

        title_label = tk.Label(header_frame, text="Smart Traffic Signal System", 
                               font=("Helvetica", 24, "bold"), fg="#2c5282", bg="#ffffff")
        title_label.pack()

        # Main content
        content_frame = tk.Frame(self.root, bg="#f0f4f8")
        content_frame.pack(expand=True, fill=tk.BOTH, padx=40, pady=20)

        # Traffic signals grid
        signals_frame = tk.Frame(content_frame, bg="#f0f4f8")
        signals_frame.pack(expand=True, fill=tk.BOTH)

        for i, direction in enumerate(self.directions):
            row = i // 2
            col = i % 2
            self.create_signal_widget(signals_frame, direction, row, col)

        signals_frame.grid_columnconfigure(0, weight=1)
        signals_frame.grid_columnconfigure(1, weight=1)
        signals_frame.grid_rowconfigure(0, weight=1)
        signals_frame.grid_rowconfigure(1, weight=1)

    def create_signal_widget(self, parent, direction, row, col):
        frame = tk.Frame(parent, bg="#ffffff", padx=20, pady=20, relief="raised", borderwidth=1)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        self.signal_frames.append(frame)

        tk.Label(frame, text=direction, font=("Helvetica", 20, "bold"), fg="#2c5282", bg="#ffffff").pack(pady=(0, 10))

        signal_label = tk.Label(frame, text="RED", font=("Helvetica", 36, "bold"), fg="#e53e3e", bg="#ffffff")
        signal_label.pack(pady=10)
        self.signal_labels.append(signal_label)

        vehicle_label = tk.Label(frame, text="Vehicles: 0", font=("Helvetica", 16), fg="#4a5568", bg="#ffffff")
        vehicle_label.pack(pady=5)
        self.vehicle_labels.append(vehicle_label)

        emergency_label = tk.Label(frame, text="", font=("Helvetica", 14, "bold"), fg="#ed8936", bg="#ffffff")
        emergency_label.pack(pady=5)
        self.emergency_labels.append(emergency_label)

        waiting_time_label = tk.Label(frame, text="Waiting Time: 0s", font=("Helvetica", 14), fg="#4a5568", bg="#ffffff")
        waiting_time_label.pack(pady=5)
        self.waiting_time_labels.append(waiting_time_label)

    def start_simulation(self):
        threading.Thread(target=self.run_simulation, daemon=True).start()

    def run_simulation(self):
        current_signal_index = 0
        emergency_active = False
        emergency_direction = None
        emergency_priority_time = 0

        while True:
            time.sleep(1)

            # Handle emergency priority logic
            if emergency_active and emergency_priority_time > 0:
                emergency_priority_time -= 1
                green_signal_index = self.directions.index(emergency_direction)
            else:
                emergency_active = False
                green_signal_index = current_signal_index

            # Update vehicle counts, signals, and waiting times
            for i in range(4):
                if i == green_signal_index:
                    decrease = random.randint(5, 10)
                    self.vehicle_counts[i] = max(0, self.vehicle_counts[i] - decrease)
                    self.current_signal[i] = "GREEN"
                    self.waiting_times[i] = 0
                else:
                    increase = random.randint(1, 3)
                    self.vehicle_counts[i] += increase
                    self.current_signal[i] = "RED"
                    self.waiting_times[i] += 1

                # If emergency vehicle is present and vehicle count is zero, set vehicle count to 1
                if self.emergency_vehicles[i] > 0 and self.vehicle_counts[i] == 0:
                    self.vehicle_counts[i] = 1

            # Handle emergency vehicle occurrence
            if not emergency_active and random.random() < 0.05:  # 5% chance of emergency
                emergency_direction = random.choice(self.directions)
                emergency_index = self.directions.index(emergency_direction)
                self.emergency_vehicles[emergency_index] = 1
                emergency_active = True
                emergency_priority_time = 3
            elif emergency_active and emergency_priority_time == 0:
                self.emergency_vehicles[self.directions.index(emergency_direction)] = 0

            # Change signal when green side has no cars or max waiting time reached
            if not emergency_active and (self.vehicle_counts[green_signal_index] == 0 or 
                                         max(self.waiting_times) >= 60 or 
                                         sum(self.vehicle_counts) == 0):
                current_signal_index = (current_signal_index + 1) % 4
                if sum(self.vehicle_counts) == 0:
                    self.vehicle_counts = [random.randint(15, 20) for _ in range(4)]

            self.root.after(0, self.update_ui)

    def update_ui(self):
        for i in range(4):
            signal = self.current_signal[i]
            self.signal_labels[i].config(text=signal, fg="#38a169" if signal == "GREEN" else "#e53e3e")
            self.vehicle_labels[i].config(text=f"Vehicles: {self.vehicle_counts[i]}")
            self.waiting_time_labels[i].config(text=f"Waiting Time: {self.waiting_times[i]}s")

            if self.emergency_vehicles[i] > 0:
                self.emergency_labels[i].config(text="EMERGENCY VEHICLE")
            else:
                self.emergency_labels[i].config(text="")

def run_ui():
    root = tk.Tk()
    app = ModernTrafficSignalUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_ui()
