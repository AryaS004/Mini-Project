import cv2
import numpy as np

# Load trained model
recognizer = cv2.face.FisherFaceRecognizer_create()
recognizer.read("models/fisherface_model.yml")

# Load label map
label_map = np.load("models/label_map.npy", allow_pickle=True).item()

# Load test image
test_img = cv2.imread("dataset/LBT22IT015/1.jpg", cv2.IMREAD_GRAYSCALE)  # Change to a real student image path
test_img = cv2.resize(test_img, (200, 200))

label, confidence = recognizer.predict(test_img)
accuracy = round((100 - confidence), 2)  # Convert confidence to accuracy %

name = label_map.get(label, "Unknown")
print(f"✅ Test Image Recognized: {name} (Confidence: {confidence}, Accuracy: {accuracy}%)")
