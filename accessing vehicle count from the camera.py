import tkinter as tk
import threading
import time
import cv2
import torch

# Load YOLOv5 model (make sure you have YOLOv5 installed via `torch.hub`)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

# Function to count vehicles using YOLOv5
def count_vehicles(frame):
    # Convert the frame to RGB for YOLOv5
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Run the YOLOv5 model
    results = model(img_rgb)
    
    # Filter only vehicles (cars, trucks, buses, etc.)
    vehicle_classes = [2, 3, 5, 7]  # YOLOv5 label indices for cars, trucks, buses, and trains
    labels = results.xyxyn[0][:, -1]  # Get the detected labels
    vehicle_count = 0
    
    for label in labels:
        if int(label) in vehicle_classes:
            vehicle_count += 1

    return vehicle_count

# Lane class for managing lane-specific data
class Lane:
    def __init__(self, name):
        self.name = name
        self.vehicle_count = 0
        self.waiting_time = 0

    # Update vehicle count based on the video frame
    def update_from_video(self, frame):
        self.vehicle_count = count_vehicles(frame)
        self.waiting_time = 0

    # Increment waiting time for lanes not in green signal
    def increment_waiting_time(self):
        self.waiting_time += 1

# TrafficSignal class for managing traffic flow logic
class TrafficSignal:
    def __init__(self, gui):
        self.lanes = {
            'lane1': Lane('Lane 1'),
            'lane2': Lane('Lane 2'),
            'lane3': Lane('Lane 3'),
            'lane4': Lane('Lane 4')
        }
        self.pedestrian_waiting = False
        self.gui = gui

    # Emergency vehicle priority logic
    def emergency_vehicle_priority(self):
        self.gui.update_status("Emergency vehicle detected. Giving green signal for 10 seconds.")
        self.gui.set_signal("green", "lane1")
        time.sleep(10)
        self.gui.set_signal("red", "lane1")

    # Less congested lane priority logic
    def less_congested_lane_priority(self):
        for lane_name, lane in self.lanes.items():
            if lane.vehicle_count < 5:
                green_time = lane.vehicle_count * 5
                self.gui.update_status(f"Giving green signal to {lane.name} for {green_time} seconds.")
                self.gui.set_signal("green", lane_name)
                time.sleep(green_time)
                lane.vehicle_count = 0
                self.gui.set_signal("red", lane_name)

    # Most congested lane priority logic
    def most_congested_lane_priority(self):
        most_congested_lane_name = max(self.lanes, key=lambda lane: self.lanes[lane].vehicle_count)
        most_congested_lane = self.lanes[most_congested_lane_name]
        self.gui.update_status(f"Giving green signal to {most_congested_lane.name} for up to 100 seconds.")
        self.gui.set_signal("green", most_congested_lane_name)
        for _ in range(100):
            if most_congested_lane.vehicle_count == 0:
                break
            time.sleep(1)
            most_congested_lane.vehicle_count -= 1
        self.gui.set_signal("red", most_congested_lane_name)

    # Pedestrian crossing priority
    def pedestrian_priority(self):
        if self.pedestrian_waiting:
            self.gui.update_status("Pedestrian crossing active. All lanes red for 60 seconds.")
            self.gui.set_signal("red", "all")
            time.sleep(60)
            self.pedestrian_waiting = False

    # Update lane status (for display)
    def update_lane_status(self):
        status = ""
        for lane in self.lanes.values():
            lane.increment_waiting_time()
            status += f"{lane.name}: {lane.vehicle_count} vehicles, {lane.waiting_time}s wait.\n"
        self.gui.update_status(status)

    # Main cycle of traffic signal control
    def run_cycle(self, frame):
        self.update_lane_vehicle_counts(frame)
        self.emergency_vehicle_priority()
        self.less_congested_lane_priority()
        self.most_congested_lane_priority()
        self.pedestrian_priority()
        self.update_lane_status()

    # Update vehicle count for all lanes based on the current frame
    def update_lane_vehicle_counts(self, frame):
        self.lanes['lane1'].update_from_video(frame)
        self.lanes['lane2'].update_from_video(frame)
        self.lanes['lane3'].update_from_video(frame)
        self.lanes['lane4'].update_from_video(frame)

# GUI class for managing the visual representation of the traffic signals
class TrafficSignalGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Signal Management")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c3e50")

        self.signals = {}
        for i in range(4):
            frame = tk.Frame(root, bg="#2c3e50")
            if i == 0:
                frame.place(x=50, y=50)
            elif i == 1:
                frame.place(x=450, y=50)
            elif i == 2:
                frame.place(x=50, y=350)
            elif i == 3:
                frame.place(x=450, y=350)
            self.signals[f'lane{i+1}'] = {
                'red': tk.Label(frame, bg="grey", width=5, height=2),
                'yellow': tk.Label(frame, bg="grey", width=5, height=2),
                'green': tk.Label(frame, bg="grey", width=5, height=2)
            }
            self.signals[f'lane{i+1}']['red'].pack(pady=2)
            self.signals[f'lane{i+1}']['yellow'].pack(pady=2)
            self.signals[f'lane{i+1}']['green'].pack(pady=2)

        self.status_label = tk.Label(root, text="Status: ", anchor="w", justify="left", bg="#ecf0f1", fg="#2c3e50", font=("Helvetica", 10), padx=5, pady=5)
        self.status_label.place(x=150, y=200, width=300, height=100)

        self.start_button = tk.Button(root, text="Start", command=self.start_traffic_signal, bg="#27ae60", fg="#ecf0f1", font=("Helvetica", 12), padx=5, pady=5)
        self.start_button.place(x=250, y=320, width=100, height=40)

        self.traffic_signal = TrafficSignal(self)

    def update_status(self, status):
        self.status_label.config(text=f"Status: \n{status}")

    def set_signal(self, color, lane_name):
        for signal_name, signal in self.signals.items():
            if lane_name == "all" or signal_name == lane_name:
                signal['red'].config(bg="grey")
                signal['yellow'].config(bg="grey")
                signal['green'].config(bg="grey")
                if color == "red":
                    signal['red'].config(bg="red")
                elif color == "yellow":
                    signal['yellow'].config(bg="yellow")
                elif color == "green":
                    signal['green'].config(bg="green")
            else:
                signal['red'].config(bg="red")
                signal['yellow'].config(bg="grey")
                signal['green'].config(bg="grey")

    def start_traffic_signal(self):
        threading.Thread(target=self.run_traffic_signal, daemon=True).start()

    def run_traffic_signal(self):
        video_path = "four_way_road_video.mp4"
        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Run the traffic signal cycle with the current frame
            self.traffic_signal.run_cycle(frame)

            time.sleep(1)
        
        cap.release()
        cv2.destroyAllWindows()

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSignalGUI(root)
    root.mainloop()
