import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase
cred = credentials.Certificate("C:/Users/Anju/Downloads/attendence-list-lbs-firebase-adminsdk-fbsvc-c93787b982.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def log_attendance_firebase(name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attendance_data = {"name": name, "timestamp": timestamp}
    attendance_ref = db.collection('attendance')
    attendance_ref.add(attendance_data)
    print(f"Attendance logged for {name} at {timestamp}")

def fetch_and_generate_csv():
    attendance_ref = db.collection('attendance')
    docs = attendance_ref.stream()
    attendance_data = [["Name", "Timestamp"]]
    for doc in docs:
        data = doc.to_dict()
        name = data.get("name")
        timestamp = data.get("timestamp")
        attendance_data.append([name, timestamp])

    with open('attendance.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(attendance_data)
    print("Attendance CSV generated.")


