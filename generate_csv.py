import csv
from firebase_config import db

def fetch_and_generate_csv():
    attendance_ref = db.collection('attendance')
    docs = attendance_ref.stream()
    attendance_data = [["Name", "Timestamp"]]  # CSV Header

    count = 0
    for doc in docs:
        data = doc.to_dict()
        name = data.get("name", "Unknown")
        timestamp = data.get("timestamp", "Unknown")
        attendance_data.append([name, timestamp])
        count += 1

    if count == 0:
        print("⚠️ No attendance records found in Firebase.")
        return

    filename = "attendance.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(attendance_data)

    print(f"✅ Attendance CSV generkated: {filename}")

# Run the function
fetch_and_generate_csv()
