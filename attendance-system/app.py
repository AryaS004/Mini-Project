from flask import Flask, render_template, Response, request, jsonify
import cv2
import os
import csv
from datetime import datetime
from firebase_config import db
from face_recognition import recognize_face
from email_sender import send_email

app = Flask(__name__)

# Home Route
@app.route('/')
def index():
    return render_template('index.html')

# Route to Fetch Attendance Data
@app.route('/attendance')
def fetch_attendance():
    attendance_ref = db.collection('attendance')
    docs = attendance_ref.stream()
    
    attendance_data = []
    for doc in docs:
        attendance_data.append(doc.to_dict())

    return jsonify(attendance_data)

# Route to Capture and Recognize Face
@app.route('/capture')
def capture():
    return render_template('capture.html')

# Route to Start Face Recognition
@app.route('/start_recognition')
def start_recognition():
    recognize_face()
    return jsonify({"message": "Face recognition started!"})

# Route to Generate CSV
@app.route('/generate_csv')
def generate_csv():
    attendance_ref = db.collection('attendance')
    docs = attendance_ref.stream()

    filename = "uploads/attendance.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Timestamp"])

        for doc in docs:
            data = doc.to_dict()
            writer.writerow([data["name"], data["timestamp"]])

    return jsonify({"message": "CSV Generated Successfully!", "file": filename})

# Route to Send Attendance via Email
@app.route('/send_email', methods=['POST'])
def send_attendance_email():
    data = request.get_json()
    email = data['email']
    send_email(email)
    return jsonify({"message": "Attendance email sent successfully!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


