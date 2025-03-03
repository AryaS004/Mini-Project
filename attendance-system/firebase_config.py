import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase Admin SDK
cred = credentials.Certificate(r"C:\Users\Anju\OneDrive\Desktop\Mini-Project-1\attendance-system\attendence-list-lbs-firebase-adminsdk-fbsvc-a5eaad4159.json")

firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

