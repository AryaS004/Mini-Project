import cv2
import numpy as np

# Load pre-trained DNN face detector
net = cv2.dnn.readNetFromCaffe("models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000.caffemodel")

def detect_faces(frame):
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123), True, crop=False)
    net.setInput(blob)
    detections = net.forward()
    
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
            (x, y, x2, y2) = box.astype("int")
            cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)

    return frame

# Open webcam and test face detection
cap = cv2.VideoCapture(0)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_faces(frame)
    cv2.imshow("Face Detection Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
