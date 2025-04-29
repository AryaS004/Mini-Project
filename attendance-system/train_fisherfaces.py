import cv2
import os
import numpy as np
from sklearn.model_selection import train_test_split

# ✅ Paths
DATASET_PATH = "preprocess_dataset"
MODEL_PATH = "models/fisherface_model.yml"
LABEL_MAP_PATH = "models/label_map.npy"

# ✅ Ensure model directory exists
os.makedirs("models", exist_ok=True)

def load_dataset():
    """Load dataset and return face images, labels, and label mapping."""
    faces, labels = [], []
    label_map = {}
    label_id = 0

    if not os.path.exists(DATASET_PATH) or len(os.listdir(DATASET_PATH)) == 0:
        raise ValueError("❌ ERROR: No preprocessed dataset found. Run `preprocess_faces.py` first!")

    for person_name in os.listdir(DATASET_PATH):
        person_folder = os.path.join(DATASET_PATH, person_name)
        if not os.path.isdir(person_folder):
            continue  # ✅ Skip non-folder items

        label_map[label_id] = person_name
        image_count = 0

        for img_name in os.listdir(person_folder):
            img_path = os.path.join(person_folder, img_name)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

            if img is not None:
                # ✅ Use detected size from the first image
                if len(faces) == 0:
                    img_height, img_width = img.shape
                img_resized = cv2.resize(img, (img_width, img_height))  # ✅ Resize dynamically

                faces.append(img_resized)
                labels.append(label_id)
                image_count += 1
            else:
                print(f"⚠️ Warning: Could not load image {img_path}. Skipping...")

        if image_count < 50:  # ✅ Require at least 50 images per person
            raise ValueError(f"❌ ERROR: Not enough images for {person_name}. Capture at least 50.")

        label_id += 1

    if len(set(labels)) < 2:
        raise ValueError("❌ ERROR: Fisherfaces requires at least 2 different people in the dataset!")

    return np.array(faces, dtype=np.uint8), np.array(labels, dtype=np.int32), label_map

# ✅ Load dataset
print("📂 Loading dataset...")
try:
    faces, labels, label_map = load_dataset()
    print(f"✅ Dataset loaded: {len(faces)} images, {len(np.unique(labels))} classes.")
except ValueError as e:
    print(str(e))
    exit(1)

# ✅ Train/Test Split (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(faces, labels, test_size=0.2, random_state=42)

# ✅ Train FisherFace Model
print("🔄 Training FisherFace model...")
try:
    recognizer = cv2.face.FisherFaceRecognizer_create()
    recognizer.train(X_train, y_train)

    # ✅ Evaluate Model on Test Set
    correct = 0
    for i in range(len(X_test)):
        predicted_label, confidence = recognizer.predict(X_test[i])
        actual_label = y_test[i]
        if predicted_label == actual_label:
            correct += 1
        print(f"Actual: {actual_label}, Predicted: {predicted_label}, Confidence: {confidence:.2f}")

    accuracy = (correct / len(X_test)) * 100
    print(f"✅ Validation Accuracy: {accuracy:.2f}%")

    # ✅ Save Model & Label Map
    recognizer.write(MODEL_PATH)
    np.save(LABEL_MAP_PATH, label_map)

    # ✅ Verify model save
    if os.path.exists(MODEL_PATH) and os.path.exists(LABEL_MAP_PATH):
        print(f"✅ Model trained and saved at {MODEL_PATH}")
        print(f"✅ Label map saved at {LABEL_MAP_PATH}")
    else:
        print("❌ Error saving model!")

except cv2.error as e:
    print(f"❌ Training error: {e}")
    exit(1)
