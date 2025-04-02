import cv2
print(cv2.__version__)  # Should be 4.x.x
recognizer = cv2.face.FisherFaceRecognizer_create()
print("FisherFaceRecognizer loaded successfully!")

