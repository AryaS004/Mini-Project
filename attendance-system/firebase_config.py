import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

# Load Firebase JSON Key Securely
FIREBASE_JSON = os.getenv("FIREBASE_JSON", "attendence-list-lbs-firebase-adminsdk-fbsvc-ae262f0826.json")

# Initialize Firebase only if not already initialized
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(FIREBASE_JSON)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            exit(1)  # Exit if Firebase fails to initialize
    else:
        print("⚠️ Firebase already initialized.")
    
initialize_firebase()

# Firestore Database and Auth
db = firestore.client()
auth = firebase_admin.auth

# Function to Log Attendance in Firebase
def log_attendance_firebase(name, teacher_email):
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        db.collection('attendance').add({
            "name": name,
            "timestamp": timestamp,
            "teacher_email": teacher_email
        })
        print(f"✅ Attendance logged for {name} at {timestamp}")
    except Exception as e:
        print(f"❌ Error logging attendance: {e}")

# Function to Register a New Student
def register_student(name, student_id, email, image_path):
    try:
        db.collection("students").document(student_id).set({
            "name": name,
            "email": email,
            "image_path": image_path
        })
        print(f"✅ Student {name} registered successfully!")
    except Exception as e:
        print(f"❌ Error registering student {name}: {e}")
