import cv2
import os

# Create dataset directory if it doesn't exist
dataset_path = "dataset"
if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

person_name = input("Enter person's name: ")
person_folder = os.path.join(dataset_path, person_name)

if not os.path.exists(person_folder):
    os.makedirs(person_folder)

cap = cv2.VideoCapture(0)  # Open webcam
count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Show the webcam feed
    cv2.imshow("Capturing Face", frame)

    # Save images in the person's folder
    img_path = os.path.join(person_folder, f"{count}.jpg")
    cv2.imwrite(img_path, frame)

    count += 1

    # Stop capturing after 50 images
    if count >= 50:
        break

    # Press 'q' to quit manually
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"Saved {count} images for {person_name}.")
