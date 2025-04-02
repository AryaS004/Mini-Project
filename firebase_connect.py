import firebase_admin
from firebase_admin import credentials, firestore, auth
from datetime import datetime
import os

# Load Firebase Credentials (Replace with your actual path)
FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "attendence-list-lbs-firebase-adminsdk-fbsvc-ae262f0826.json")

# Initialize Firebase
def initialize_firebase():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            exit(1)  # Exit if Firebase fails to initialize
    else:
        print("⚠️ Firebase already initialized.")
    
initialize_firebase()

# Connect to Firestore Database
db = firestore.client()

# ============================
# ✅ Register Student
# ============================
def register_student(name, student_id, email, image_path):
    """
    Registers a new student in the Firestore database.
    :param name: Student's full name
    :param student_id: Unique Student ID
    :param email: Student's email
    :param image_path: Path to stored image in Firebase Storage
    """
    try:
        doc_ref = db.collection("students").document(student_id)
        doc_ref.set({
            "name": name,
            "email": email,
            "image_path": image_path,
            "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        print(f"✅ Student {name} (ID: {student_id}) registered successfully!")
    except Exception as e:
        print(f"❌ Error registering student: {e}")

# ============================
# ✅ Mark Attendance
# ============================
def mark_attendance(student_id, student_name, subject, teacher_email):
    """Marks attendance for a recognized student in Firebase Firestore"""
    if student_id == "Unknown":
        print("❌ Unknown face detected, attendance not marked.")
        return  # ❌ Ignore unrecognized faces

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # ✅ Get current timestamp
    date = datetime.now().strftime("%Y-%m-%d")  # ✅ Get current date

    attendance_ref = db.collection("attendance").document(date)
    
    # ✅ Update attendance record for the student
    attendance_ref.set({
        student_id: {
            "name": student_name,
            "subject": subject,
            "teacher_email": teacher_email,
            "timestamp": timestamp
        }
    }, merge=True)

    print(f"✅ Attendance marked for {student_name} ({student_id}) at {timestamp}")

# ============================
# ✅ Fetch Attendance Records
# ============================
def get_attendance(student_id):
    """
    Retrieves attendance records for a specific student.
    :param student_id: Unique Student ID
    :return: List of attendance records
    """
    records = []
    try:
        attendance_docs = db.collection("attendance").stream()
        for doc in attendance_docs:
            data = doc.to_dict()
            if student_id in data:
                records.append({doc.id: data[student_id]})
        
        if records:
            print(f"📄 Attendance records found for {student_id}:")
            for record in records:
                print(record)
        else:
            print(f"❌ No attendance records found for {student_id}")
        
        return records
    except Exception as e:
        print(f"❌ Error fetching attendance: {e}")
        return []

# ============================
# ✅ Fetch All Students
# ============================
def get_all_students():
    """
    Retrieves all registered students from Firestore.
    :return: Dictionary of students
    """
    students = {}
    try:
        student_docs = db.collection("students").stream()
        for doc in student_docs:
            students[doc.id] = doc.to_dict()
        
        if students:
            print("📄 Registered Students:")
            for sid, details in students.items():
                print(f"🔹 {sid}: {details}")
        else:
            print("❌ No students found in database.")

        return students
    except Exception as e:
        print(f"❌ Error fetching students: {e}")
        return {}
