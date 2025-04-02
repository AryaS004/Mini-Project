import cv2
import os

# ✅ Define paths
DATASET_PATH = "dataset"
PREPROCESS_PATH = "preprocess_dataset"
IMG_SIZE = 200  # ✅ Fixed size for training

# ✅ Create preprocess dataset folder if it doesn’t exist
os.makedirs(PREPROCESS_PATH, exist_ok=True)

# ✅ Check if dataset exists
if not os.path.exists(DATASET_PATH):
    print("❌ Error: Dataset folder not found!")
    exit(1)

# ✅ Process each student's folder
for student_id in os.listdir(DATASET_PATH):
    student_folder = os.path.join(DATASET_PATH, student_id)

    if not os.path.isdir(student_folder):
        continue  # ✅ Skip non-folder files

    preprocess_student_folder = os.path.join(PREPROCESS_PATH, student_id)
    os.makedirs(preprocess_student_folder, exist_ok=True)  # ✅ Create folder in preprocess dataset

    print(f"📂 Processing images for Student ID: {student_id}")

    for img_name in os.listdir(student_folder):
        img_path = os.path.join(student_folder, img_name)
        preprocess_img_path = os.path.join(preprocess_student_folder, img_name)

        # ✅ Load image
        img = cv2.imread(img_path)
        if img is None:
            print(f"⚠️ Skipping invalid image: {img_path}")
            continue

        # ✅ Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # ✅ Resize to uniform size
        resized = cv2.resize(gray, (IMG_SIZE, IMG_SIZE))

        # ✅ Save the preprocessed image in the new dataset
        cv2.imwrite(preprocess_img_path, resized)

    print(f"✅ Preprocessing complete for {student_id}\n")

print("🎉 All images processed and stored in 'preprocess_dataset' successfully!")
