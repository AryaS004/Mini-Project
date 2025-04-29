import cv2
import numpy as np
from cv2 import dnn 

# Load the face detection model
face_net = dnn.readNetFromCaffe("models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000.caffemodel")

def detect_faces(image_path):
    frame = cv2.imread(image_path)
    h, w = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
    face_net.setInput(blob)
    detections = face_net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x, y, x2, y2 = box.astype("int")
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)
            print(f"Face detected with confidence: {confidence}")
    
    cv2.imshow("Face Detection", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Test with an image
detect_faces("76.jpg")
