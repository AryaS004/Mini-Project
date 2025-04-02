import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ✅ Initialize Firebase
cred = credentials.Certificate("attendence-list-lbs-firebase-adminsdk-fbsvc-ae262f0826.json")  # 🔹 Replace with your actual Firebase config file
firebase_admin.initialize_app(cred)

# Initialize Firestore database
firestore_db = firestore.client()

# ✅ Load Pretrained Face Detector (DNN)
face_net = cv2.dnn.readNetFromCaffe("models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000.caffemodel")

# ✅ Load FisherFace Model & Labels
recognizer = cv2.face.FisherFaceRecognizer_create()
recognizer.read("models/fisherface_model.yml")
label_map = np.load("models/label_map.npy", allow_pickle=True).item()  # 🔹 Load label mapping dictionary

IMG_WIDTH, IMG_HEIGHT = 200, 200  # Resize face images to match trained model

# ✅ Function to Detect Faces using DNN
def detect_faces_dnn(frame):
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
    face_net.setInput(blob)
    detections = face_net.forward()

    faces = []
    locations = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x, y, x2, y2 = box.astype("int")
            faces.append(frame[y:y2, x:x2])
            locations.append((x, y, x2, y2))

    return faces, locations

# ✅ Function to Recognize Face
def recognize_face(face):
    gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
    resized_face = cv2.resize(gray, (IMG_WIDTH, IMG_HEIGHT))

    try:
        label, confidence = recognizer.predict(resized_face)
        if confidence < 3000:  # 🔹 Adjust confidence threshold as needed
            student_id = label_map.get(label, "Unknown")
            return student_id, confidence
    except:
        pass
    
    return "Unknown", None

# ✅ Function to Log Attendance in Firestore
def mark_attendance(student_id, student_name, subject, teacher_email):
    if student_id == "Unknown":
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date = datetime.now().strftime("%Y-%m-%d")

    # ✅ Firestore (Permanent Storage)
    attendance_ref = firestore_db.collection("attendance").document(date)
    attendance_ref.set({
        student_id: {
            "name": student_name,
            "timestamp": timestamp,
            "subject": subject,
            "teacher_email": teacher_email
        }
    }, merge=True)

    print(f"✅ Attendance marked for {student_name} at {timestamp}")

# ✅ Start Face Recognition
def start_recognition():
    cap = cv2.VideoCapture(0)
    print("📷 Starting Face Recognition...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        faces, locations = detect_faces_dnn(frame)

        for face, (x, y, x2, y2) in zip(faces, locations):
            student_id, confidence = recognize_face(face)
            student_name = student_id if student_id != "Unknown" else "Unknown"

            # ✅ Draw bounding box
            color = (0, 255, 0) if student_id != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x2, y2), color, 2)
            cv2.putText(frame, f"{student_name} ({confidence:.2f})", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

            # ✅ Log attendance if face is recognized
            if student_id != "Unknown":
                mark_attendance(student_id, student_name, subject="CS101", teacher_email="teacher@example.com")

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🔴 Stopped Face Recognition.")

# ✅ Run Recognition
if __name__ == "__main__":
    start_recognition()
