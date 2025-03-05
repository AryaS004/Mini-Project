import cv2
import numpy as np
from firebase_config import log_attendance_firebase
# Load trained model
recognizer = cv2.face.FisherFaceRecognizer_create()
recognizer.read("models/fisherface_model.yml")

# Load label map
label_map = np.load("models/label_map.npy", allow_pickle=True).item()

# Load face detector
net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "res10_300x300_ssd_iter_140000.caffemodel")

def detect_faces(frame):
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

def recognize_face(frame, faces):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    for (x, y, x2, y2) in faces:
        roi = gray[y:y2, x:x2]

        # Ensure ROI is valid before processing
        if roi.shape[0] == 0 or roi.shape[1] == 0:
            print("Skipping invalid face region")
            continue
        
        # Resize the ROI to match training input size
        roi = cv2.resize(roi, (200, 200))

        label, confidence = recognizer.predict(roi)

        if confidence < 100:  # Confidence threshold
            name = label_map.get(label, "Unknown")
        else:
            name = "Unknown"

        cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"{name}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        if confidence < 100:
            log_attendance_firebase(name)

    return frame

cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    faces = detect_faces(frame)
    frame = recognize_face(frame, faces)

    cv2.imshow("Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
