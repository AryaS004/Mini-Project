import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime

# ✅ Load Firebase credentials from environment variable or default path
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "attendence-list-lbs-firebase-adminsdk-fbsvc-ae262f0826.json")

if not os.path.exists(FIREBASE_CREDENTIALS):
    raise FileNotFoundError(f"❌ Firebase credentials file not found: {FIREBASE_CREDENTIALS}")

# ✅ Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Initialized Successfully!")
    except Exception as e:
        print(f"❌ Firebase Initialization Error: {e}")
        raise e

# ✅ Firestore Database Reference
db = firestore.client()

# ✅ Function to Get Firestore Collection
def get_collection(collection_name):
    return db.collection(collection_name)

# ✅ Function to Add Student Record
def add_student(student_id, name, email):
    try:
        student_ref = db.collection("students").document(student_id)
        student_ref.set({
            "name": name,
            "email": email,
            "role": "student"
        })
        return f"✅ Student {name} added successfully."
    except Exception as e:
        return f"❌ Error adding student: {e}"

# ✅ Function to Get Student Data
def get_student(student_id):
    try:
        student_ref = db.collection("students").document(student_id).get()
        return student_ref.to_dict() if student_ref.exists else None
    except Exception as e:
        print(f"❌ Error fetching student data: {e}")
        return None

# ✅ Function to Add Teacher Record
def add_teacher(teacher_id, name, email):
    try:
        teacher_ref = db.collection("teachers").document(teacher_id)
        teacher_ref.set({
            "name": name,
            "email": email,
            "role": "teacher"
        })
        return f"✅ Teacher {name} added successfully."
    except Exception as e:
        return f"❌ Error adding teacher: {e}"

# ✅ Function to Get Teacher Data
def get_teacher(teacher_id):
    try:
        teacher_ref = db.collection("teachers").document(teacher_id).get()
        return teacher_ref.to_dict() if teacher_ref.exists else None
    except Exception as e:
        print(f"❌ Error fetching teacher data: {e}")
        return None

# ✅ Function to Store Attendance with Timestamp
def mark_attendance(student_id, class_id, status):
    try:
        attendance_ref = db.collection("attendance").document()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attendance_ref.set({
            "student_id": student_id,
            "class_id": class_id,
            "status": status,
            "timestamp": timestamp
        })
        return f"✅ Attendance marked for {student_id} in class {class_id} with status {status} at {timestamp}."
    except Exception as e:
        return f"❌ Error marking attendance: {e}"

# ✅ Test the connection
if __name__ == "__main__":
    print("✅ Firebase Config Initialized Successfully!")
