import cv2
import numpy as np

# Load trained FisherFace model
recognizer = cv2.face.FisherFaceRecognizer_create()

try:
    recognizer.read("models/fisherface_model.yml")
    print("✅ FisherFace model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# Check label map
try:
    label_map = np.load("models/label_map.npy", allow_pickle=True).item()
    print(f"✅ Label Map: {label_map}")
except Exception as e:
    print(f"❌ Error loading label map: {e}")
