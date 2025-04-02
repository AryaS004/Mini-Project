import smtplib
import os
from email.message import EmailMessage

def send_attendance_email(to_email):
    sender_email = "your_email@example.com"
    sender_password = "your_email_password"  # Use app password if needed

    subject = "Attendance Report"
    body = "Please find the attached attendance report for today's session."

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Attach attendance CSV
    filename = "attendance.csv"
    if os.path.exists(filename):
        with open(filename, "rb") as file:
            msg.add_attachment(file.read(), maintype="application", subtype="octet-stream", filename=filename)

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print("Attendance email sent successfully.")
