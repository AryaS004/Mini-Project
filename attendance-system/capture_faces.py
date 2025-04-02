import cv2
import os
import numpy as np
from firebase_config import register_student

# ✅ Load OpenCV DNN Face Detector
MODEL_PATH = "models/"
net = cv2.dnn.readNetFromCaffe(
    os.path.join(MODEL_PATH, "deploy.prototxt"),
    os.path.join(MODEL_PATH, "res10_300x300_ssd_iter_140000.caffemodel")
)

# ✅ Create dataset directory
DATASET_DIR = "dataset"
os.makedirs(DATASET_DIR, exist_ok=True)

# ✅ Get student details
name = input("Enter Student Name: ").strip()
student_id = input("Enter Student ID: ").strip()
email = input("Enter Student Email: ").strip()

# ✅ Create folder for student
person_folder = os.path.join(DATASET_DIR, student_id)
os.makedirs(person_folder, exist_ok=True)

# ✅ Initialize camera
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  # High resolution
cap.set(4, 720)

if not cap.isOpened():
    print("❌ Error: Could not open webcam.")
    exit(1)

print("\n🎥 Capturing 100 images... Stay still and look at the camera.")

count = 0
retry_count = 0
IMG_SIZE = 200  # Fixed size for training

while count < 100:
    ret, frame = cap.read()
    if not ret:
        print("❌ Error: Failed to capture frame.")
        retry_count += 1
        if retry_count > 10:
            print("❌ Camera not responding. Exiting.")
            break
        continue

    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104.0, 177.0, 123.0))
    net.setInput(blob)
    detections = net.forward()

    face_detected = False
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.8:  # ✅ High threshold to avoid false detections
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # ✅ Expand bounding box slightly
            startX, startY = max(0, startX - 20), max(0, startY - 20)
            endX, endY = min(w, endX + 20), min(h, endY + 20)

            # ✅ Crop face (NORMAL SCALE, NO GRAYSCALE)
            face = frame[startY:endY, startX:endX]
            if face.shape[0] == 0 or face.shape[1] == 0:
                continue

            face_detected = True

            # ✅ Resize to 200x200 (but keep COLOR)
            face_resized = cv2.resize(face, (IMG_SIZE, IMG_SIZE))

            # ✅ Save normal color face
            img_path = os.path.join(person_folder, f"{count}.jpg")
            cv2.imwrite(img_path, face_resized)
            count += 1
            print(f"📸 Image {count}/100 captured.")

            # ✅ Draw bounding box
            cv2.rectangle(frame, (startX, startY), (endX, endY), (0, 255, 0), 2)

            break  # ✅ Process only the first detected face

    if not face_detected:
        print("⚠️ No face detected, retrying...")

    cv2.imshow("Capturing Faces", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ✅ Release resources
cap.release()
cv2.destroyAllWindows()

print(f"\n✅ Successfully captured {count} images for {name}.")

# ✅ Register student in Firebase
register_student(name, student_id, email, person_folder)
