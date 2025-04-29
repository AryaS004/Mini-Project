import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import firebase_admin
from firebase_admin import credentials, firestore, auth
from firebase_config import db  # Ensure firebase_config.py is correctly set up
from flask_session import Session
from face_recognition import recognize_face  # Function for face recognition
import smtplib
from email.mime.text import MIMEText
import cv2
import numpy as np
import base64
from datetime import datetime
from cv2 import dnn 
from datetime import datetime
from google.cloud import firestore
app = Flask(__name__)
DATASET_PATH = "dataset"
PREPROCESS_PATH = "preprocess_dataset"
IMG_SIZE = 200

if not firebase_admin._apps:
    cred = credentials.Certificate("attendence-list-lbs-firebase-adminsdk-fbsvc-ae262f0826.json")
    firebase_admin.initialize_app(cred)

# ✅ Load Pretrained Face Detector (DNN)
face_net = dnn.readNetFromCaffe("models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000.caffemodel")

# ✅ Load FisherFace Model & Labels
recognizer = cv2.face.FisherFaceRecognizer_create()
recognizer.read("models/fisherface_model.yml")
label_map = np.load("models/label_map.npy", allow_pickle=True).item()  # 🔹 Load label mapping dictionary

IMG_WIDTH, IMG_HEIGHT = 200, 200  # Resize images

def save_images(student_id, images):
    """Save base64 images to a dataset directory."""
    student_path = os.path.join(DATASET_PATH, student_id)
    os.makedirs(student_path, exist_ok=True)

    for i, img_data in enumerate(images):
        img_bytes = base64.b64decode(img_data.split(",")[1])
        img_path = os.path.join(student_path, f"{i}.jpg")
        with open(img_path, "wb") as img_file:
            img_file.write(img_bytes)

@app.route("/api/upload_faces", methods=["POST"])
def upload_faces():
    """Receive face images, save them, and store user details in Firebase."""
    data = request.json
    student_id = data["studentId"]
    images = data["images"]
    name = data["name"]
    branch = data["branch"]
    admission_no = data["admissionNo"]
    email = data["email"]

    # Save images
    save_images(student_id, images)

    try:
        uid = auth.get_user_by_email(email).uid
        db.collection("users").document(uid).set({
            "name": name,
            "branch": branch,
            "admissionNo": admission_no,
            "email": email,
            "role": "student"
        })

        return jsonify({"status": "success", "message": "Images saved and user registered."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# ✅ Function to Detect Faces
def detect_faces_dnn(frame):
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177, 123))
    face_net.setInput(blob)
    detections = face_net.forward()

    faces = []
    locations = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x, y, x2, y2 = box.astype("int")
            faces.append(frame[y:y2, x:x2])
            locations.append((x, y, x2, y2))

    return faces, locations

# 🔹 Configure Flask Session Storage
app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key")

Session(app)

# 🔹 Email Configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER", "your-email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your-email-password")

def send_email(student_name, student_email, subject):
    """ Sends an email when attendance is marked. """
    try:
        msg = MIMEText(f"Hello {student_name},\n\nYour attendance for '{subject}' has been recorded successfully.")
        msg["Subject"] = "Attendance Confirmation"
        msg["From"] = EMAIL_USER
        msg["To"] = student_email

        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USER, student_email, msg.as_string())

        print(f"📧 Email sent to {student_email}")

    except Exception as e:
        print(f"❌ Email failed: {str(e)}")

# 🔹 Homepage
@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/get_attendance', methods=['GET'])
def get_attendance():
    branch = request.args.get('branch')
    batch = request.args.get('batch')
    semester = request.args.get('semester')
    subject = request.args.get('subject')

    if not all([branch, batch, semester, subject]):
        return jsonify({"error": "Missing required parameters"}), 400

    attendance_ref = db.collection('attendance')
    query = attendance_ref.where("branch_name", "==", branch).where("batch_name", "==", batch)\
                          .where("semester", "==", semester).where("subject", "==", subject)

    try:
        attendance_records = query.stream()
        attendance_list = []
        
        for record in attendance_records:
            data = record.to_dict()
            attendance_list.append({
                "student_id": data.get("student_id"),
                "timestamp": data.get("timestamp"),
                "status": data.get("status")
            })
        
        return jsonify({"attendance": attendance_list})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🔹 Student Login
@app.route('/studentlogin', methods=['GET', 'POST'])
def studentlogin():
    if request.method == 'POST':
        email = request.form['email']
        try:
            user = auth.get_user_by_email(email)
            user_id = user.uid
            session['user_id'] = user_id
            return redirect(url_for('student'))
        except Exception as e:
            flash("Login failed. Try again.", "danger")
            return render_template('studentlogin.html')
    return render_template('studentlogin.html')



# 🔹 Student Dashboard
@app.route('/student')
def student():
    user_id = session.get('user_id')
    if not user_id:
        flash('Please log in first.', 'warning')
        return redirect(url_for('studentlogin'))
    
    user_doc = db.collection('users').document(user_id).get()
    if user_doc.exists:
        student_data = user_doc.to_dict()
        return render_template('student.html', student=student_data)
    else:
        flash('Student not found.', 'danger')
        return redirect(url_for('studentlogin'))
    
@app.route('/api/sessionLogin', methods=['POST'])
def session_login():
    data = request.get_json()
    id_token = data.get('idToken')

    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        session['user_id'] = uid
        return jsonify({'success': True}), 200
    except Exception as e:
        print("[ERROR] Token verification failed:", e)
        return jsonify({'success': False}), 401




# 🔹 Teacher Login
@app.route('/teacherfacetlogin', methods=['GET', 'POST'])
def teacherfacetlogin():
    if request.method == 'POST':
        email = request.form['email']

        try:
            user = auth.get_user_by_email(email)
            user_doc = db.collection('users').document(user.uid).get()

            if user_doc.exists and user_doc.to_dict().get('role') == 'teacher':
                session['user_id'] = user.uid
                return redirect(url_for('teacherdashboard', user_id=user.uid))

            flash("Invalid role!", "danger")

        except Exception as e:
            flash(f"Login failed: {str(e)}", "danger")

    return render_template('teacherfacetlogin.html')


# 🔹 Teacher Dashboard
@app.route('/teacherdashboard/<user_id>')
def teacherdashboard(user_id):
    try:
        user_doc = db.collection('users').document(user_id).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            return render_template('teacherdashboard.html', user=user_data)

        flash("User not found!", "danger")
    except Exception as e:
        flash("Something went wrong!", "danger")

    return redirect(url_for('teacherfacetlogin'))

# ✅ Function to Log Attendance
@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.json
        student_id = data.get("student_id")
        branch = data.get("branch")
        batch = data.get("batch")
        semester = data.get("semester")
        subject = data.get("subject")

        if not all([student_id, branch, batch, semester, subject]):
            return jsonify({"error": "Missing fields"}), 400

        # ✅ Use a flat structure for better querying
        attendance_data = {
            "student_id": student_id,
            "branch_name": branch,  # Ensure consistent field naming
            "batch_name": batch,
            "semester": semester,
            "subject": subject,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "status": "Present"
        }

        # ✅ Directly add to "attendance" collection (FLAT STRUCTURE)
        db.collection("attendance").add(attendance_data)

        return jsonify({"message": "Attendance marked successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# ✅ API Endpoint to Process Image
@app.route("/recognize", methods=["POST"])
def recognize():
    try:
        data = request.json
        image_data = data['image']

        # ✅ Fix Base64 Decoding Issue
        if image_data.startswith("data:image"):
            image_data = image_data.split(",")[1]

        img_bytes = base64.b64decode(image_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # ✅ Ensure Image is Not Empty
        if img is None or img.size == 0:
            return jsonify({"status": "error", "message": "Invalid image data"})

        # ✅ Detect Faces
        faces, locations = detect_faces_dnn(img)

        if len(faces) == 0:
            return jsonify({"status": "error", "message": "No face detected"})

        # ✅ Extract Class, Subject, Batch, Branch, and Semester
        class_id = data.get("class_id", "Unknown")
        subject = data.get("subject", "Unknown")
        batch_name = data.get("batch_name", "Unknown")
        branch_name = data.get("branch_name", "Unknown")
        semester = data.get("semester", "Unknown")

        today_date = datetime.today().strftime('%Y-%m-%d')

        for face, (x, y, x2, y2) in zip(faces, locations):
            student_id, confidence = recognize_face(face)
            student_name = student_id if student_id != "Unknown" else "Unknown"

            # ✅ Log attendance if recognized
            if student_id != "Unknown" and confidence > 80:
                attendance_ref = db.collection("attendance").where("student_id", "==", student_id).where("class_id", "==", class_id).where("subject", "==", subject).where("date", "==", today_date).get()

                if not attendance_ref:  # Prevent duplicate attendance
                    mark_attendance_data = {
                        "student_id": student_id,
                        "class_id": class_id,
                        "subject": subject,
                        "status": "Present",
                        "date": today_date,
                        "batch_name": batch_name,
                        "branch_name": branch_name,
                        "semester": semester
                    }
                    db.collection("attendance").add(mark_attendance_data)

                return jsonify({"status": "success", "student": student_name})

        return jsonify({"status": "error", "message": "Face not recognized"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/attendance_report', methods=['GET'])
def attendance_report():
    # Get filters from query parameters
    branch = request.args.get('branch')
    batch = request.args.get('batch')
    semester = request.args.get('semester')
    subject = request.args.get('subject')

    # Validate filters
    if not all([branch, batch, semester, subject]):
        return jsonify({"error": "Missing required filters"}), 400

    try:
        attendance_ref = db.collection('attendance')
        query = attendance_ref.where('branch_name', '==', branch)\
                              .where('batch_name', '==', batch)\
                              .where('semester', '==', semester)\
                              .where('subject', '==', subject)
        
        docs = query.stream()

        attendance_summary = {}

        for doc in docs:
            data = doc.to_dict()
            student_id = data.get('student_id')
            if student_id:
                attendance_summary[student_id] = attendance_summary.get(student_id, 0) + 1

        return jsonify({"attendance_report": attendance_summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/attendanceview')
def attendanceview():
    return render_template('Attendaenceview.html')

# 🔹 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('student_login'))  # student_login is the route function


if __name__ == '__main__':
    app.run(debug=True)