import cv2
import numpy as np
from firebase_config import log_attendance_firebase
# Function to detect faces using DNN
def detect_faces(frame):
    # Use OpenCV DNN face detector
    net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel")
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123), True, crop=False)
    net.setInput(blob)
    detections = net.forward()

    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
            (x, y, x2, y2) = box.astype("int")
            faces.append((x, y, x2, y2))
    
    return faces

# Function to recognize faces using Fisherfaces model
def recognize_face(frame, faces):
    if confidence < 100:
    name = label_map.get(label, "Unknown")
    log_attendance_firebase(name)
    pass
