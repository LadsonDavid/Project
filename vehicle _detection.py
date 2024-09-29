import torch
import cv2
import numpy as np

# Load YOLOv5 model and move to CPU (since no GPU is detected)
model = torch.hub.load('ultralytics/yolov5', 'yolov5n', device='cpu')  # YOLOv5n for speed

# Classes for detection (COCO dataset vehicle-related class IDs)
VEHICLE_CLASSES = [2, 3, 5, 7]  # Car, Motorcycle, Bus, Truck

# Function to detect vehicles and count them
def detect_vehicles(img):
    # Ensure image is in BGR format (as expected by OpenCV)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Perform inference
    results = model(img)
    
    # Get detections (bounding boxes, class labels, and confidence scores)
    detections = results.xyxy[0]  # (x1, y1, x2, y2, conf, class)
    
    vehicle_detections = []
    for *box, conf, cls in detections:
        if int(cls) in VEHICLE_CLASSES:
            vehicle_detections.append((box, conf, cls))
    
    return vehicle_detections

# Initialize camera (0 is usually the default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Set the desired width and height of the camera feed (optional)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    # Capture frame-by-frame from the camera
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    # Detect vehicles in the current frame
    vehicle_detections = detect_vehicles(frame)

    # Count the number of detected vehicles
    vehicle_count = len(vehicle_detections)
    print(vehicle_count)
    # Draw bounding boxes on detected vehicles
    for box, conf, cls in vehicle_detections:
        x1, y1, x2, y2 = map(int, box)
        label = model.names[int(cls)]  # Get label for detected vehicle
        #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #cv2.putText(frame, f'{label} {conf:.2f}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    # Display vehicle count on the frame
    cv2.putText(frame, f'Vehicles detected: {vehicle_count}', (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

    # Show the frame with detected vehicles and count
    cv2.imshow('Real-Time Vehicle Detection', frame)

    # Press 'q' to quit the video stream
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()
