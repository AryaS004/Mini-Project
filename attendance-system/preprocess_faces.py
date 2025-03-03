import cv2
import os

dataset_path = "dataset"

for person_name in os.listdir(dataset_path):
    person_folder = os.path.join(dataset_path, person_name)
    if not os.path.isdir(person_folder):
        continue

    for image_name in os.listdir(person_folder):
        image_path = os.path.join(person_folder, image_name)
        img = cv2.imread(image_path)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Resize image to 200x200
        resized = cv2.resize(gray, (200, 200))

        # Save preprocessed image
        cv2.imwrite(image_path, resized)

print("Image preprocessing complete.")
