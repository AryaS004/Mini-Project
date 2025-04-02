import os
import cv2
import time
import firebase_admin
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from firebase_admin import credentials, firestore, auth
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Firebase Admin SDK initialization
cred = credentials.Certificate('attendence-list-lbs-firebase-adminsdk-fbsvc-ae262f0826.json')  # Add your Firebase credentials file
firebase_admin.initialize_app(cred)

# Firestore database
db = firestore.client()

# Secret key for sessions
app.secret_key = 'FLASK_SECRET_KEY'  # Change to a more secure secret key

# Allowed file types for profile images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Function to check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to check if Student ID already exists
def is_student_id_unique(student_id):
    users_ref = db.collection('users').where('student_id', '==', student_id).stream()
    return not any(users_ref)  # Returns True if no duplicate found

# Function to capture 100 images of the student for face recognition
def capture_images(student_id):
    save_path = f'static/faces/{student_id}'
    os.makedirs(save_path, exist_ok=True)

    cap = cv2.VideoCapture(0)
    count = 0

    while count < 100:
        ret, frame = cap.read()
        if not ret:
            break

        img_name = os.path.join(save_path, f"{count}.jpg")
        cv2.imwrite(img_name, frame)
        count += 1
        time.sleep(0.1)  # Small delay to avoid capturing too fast

    cap.release()
    cv2.destroyAllWindows()
    return save_path

# Route to home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for signing up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        student_id = request.form.get('student_id', None)  # Only required for students

        if role == 'student':
            if not student_id:
                flash("Student ID is required for students.", 'danger')
                return redirect(url_for('signup'))

            # Check if Student ID is unique
            if not is_student_id_unique(student_id):
                flash("Student ID already exists. Please enter a unique ID.", 'danger')
                return redirect(url_for('signup'))

        try:
            # Create user in Firebase Authentication
            user = auth.create_user(email=email, password=password, display_name=name)

            # Capture images for students
            image_path = None
            if role == 'student':
                image_path = capture_images(student_id)

            # Store additional details in Firestore
            user_data = {
                'name': name,
                'email': email,
                'role': role,
                'student_id': student_id if role == 'student' else None,
                'face_images': image_path if role == 'student' else None
            }

            db.collection('users').document(user.uid).set(user_data)

            flash("Account created successfully! You can now log in.", 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Signup failed: {str(e)}", 'danger')

    return render_template('signup.html')

# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Retrieve user details from Firebase Authentication
            user = auth.get_user_by_email(email)

            # Fetch additional details from Firestore
            user_doc = db.collection('users').document(user.uid).get()

            if not user_doc.exists:
                flash("User not found in database!", "danger")
                return redirect(url_for('login'))

            user_data = user_doc.to_dict()

            session['user_id'] = user.uid
            session['user'] = {
                'email': user.email,
                'name': user.display_name,
                'role': user_data.get('role', ''),
                'student_id': user_data.get('student_id', None)
            }

            # Redirect based on role
            if session['user']['role'] == 'student':
                return redirect(url_for('student_dashboard'))
            elif session['user']['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif session['user']['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid role detected!", "danger")
                return redirect(url_for('login'))

        except Exception as e:
            flash(f"Login failed: {str(e)}", 'danger')

    return render_template('login.html')

# Route for teacher dashboard
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    return render_template('teacher_dashboard.html')

# Route for student dashboard
@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    return render_template('student_dashboard.html')

# Route for admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))  # Ensure the user is logged in

    user_id = session['user_id']  # Correct the session variable name
    
    # Fetch user data from Firebase 'users' collection using user_id
    user_ref = db.collection('users').document(user_id)
    user_data = user_ref.get()
    if user_data.exists:
        user = user_data.to_dict()
        session['user'] = user  # Optionally update session with user data
    else:
        flash("User not found in the database.", "danger")
        return redirect(url_for('login'))  # If no user data found, redirect to login

    return render_template('admin_dashboard.html', user=user)

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user data from session
    return redirect(url_for('login'))

# Route for viewing attendance
@app.route('/view_attendance')
def view_attendance():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    # Query attendance records for the logged-in student
    attendance_ref = db.collection('attendance').where('student_id', '==', session['user'].get('student_id', ''))
    attendance_records = attendance_ref.stream()

    records = []
    for record in attendance_records:
        data = record.to_dict()
        records.append({
            'name': data.get('name'),
            'student_id': data.get('student_id'),
            'class': data.get('class'),
            'subject': data.get('subject'),
            'time': data.get('time')
        })

    return render_template('attendance.html', records=records)

# Route for marking attendance (for teacher)
@app.route('/mark_attendance')
def mark_attendance():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    return render_template('mark_attendance.html')

@app.route('/manage_users')
def manage_users():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))
    
    return render_template('manage_users.html')

# Route for uploading profile image (for students)
@app.route('/upload_profile', methods=['GET', 'POST'])
def upload_profile():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['profile_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join('static/uploads', filename)
            file.save(file_path)

            # Save image URL to Firestore
            user_ref = db.collection('users').document(session['user_id'])
            user_ref.update({'profile_image': filename})

            flash('Profile image uploaded successfully!', 'success')
            return redirect(url_for('student_dashboard'))

    return render_template('upload_profile.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
