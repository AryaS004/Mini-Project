import cv2
import numpy as np
import os

def load_dataset(dataset_path):
    faces = []
    labels = []
    label_map = {}  # Mapping of label numbers to person names
    current_label = 0

    for person_name in os.listdir(dataset_path):
        person_folder = os.path.join(dataset_path, person_name)
        if not os.path.isdir(person_folder):
            continue

        label_map[current_label] = person_name

        for image_name in os.listdir(person_folder):
            image_path = os.path.join(person_folder, image_name)
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue

            faces.append(img)
            labels.append(current_label)

        current_label += 1

    return faces, np.array(labels), label_map

def train_fisherfaces():
    dataset_path = "dataset"
    faces, labels, label_map = load_dataset(dataset_path)

    recognizer = cv2.face.FisherFaceRecognizer_create()
    recognizer.train(faces, labels)
    recognizer.save("models/fisherface_model.yml")

    # Save label map for later use
    np.save("models/label_map.npy", label_map)
    print("Training completed. Model saved as fisherface_model.yml")

train_fisherfaces()
