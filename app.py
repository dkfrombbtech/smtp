from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import time
import os
import re
import logging
import threading

logging.basicConfig(level=logging.DEBUG)

SENDER_EMAIL = "noreply.bytebandits@gmail.com"
APP_PASSWORD = "zurx cpxz tucp ktjf"

app = Flask(__name__)
CORS(app)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "Templates")
TEMPLATE_PATHS = {
    "contact_user": os.path.join(TEMPLATES_DIR, "user_email.html"),
    "contact_admin": os.path.join(TEMPLATES_DIR, "admin_email.html"),
    "job_application": os.path.join(TEMPLATES_DIR, "job_application.html")
}

TEMPLATES = {}
for key, path in TEMPLATE_PATHS.items():
    try:
        with open(path, "r") as file:
            TEMPLATES[key] = file.read()
    except Exception as e:
        logging.error(f"Error loading template {key}: {e}")
        TEMPLATES[key] = ""

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_html_email(sender, recipient, subject, html_content):
    try:
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content("This email contains HTML content.")
        msg.add_alternative(html_content, subtype="html")

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, APP_PASSWORD)
            server.send_message(msg)

        logging.info(f"Email sent to {recipient}")
    except Exception as e:
        logging.error(f"Sending failed: {e}")

def send_html_email_async(sender, recipient, subject, html_content):
    thread = threading.Thread(target=send_html_email, args=(sender, recipient, subject, html_content))
    thread.start()

@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        template_type = data.get("template_type", "contact")

        unique_id = "BB-" + str(int(time.time()))
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        if template_type == "contact":
            first_name = data.get("first_name")
            last_name = data.get("last_name", "")
            email = data.get("email")
            phone = data.get("phone", "Not provided")
            subject = data.get("subject", "No subject provided")
            full_name = f"{first_name} {last_name}".strip()

            if not first_name or not email or not is_valid_email(email):
                return jsonify({"error": "First name and valid email are required."}), 400

            user_html = TEMPLATES["contact_user"].format(name=full_name, unique_id=unique_id, timestamp=timestamp)
            admin_html = TEMPLATES["contact_admin"].format(name=full_name, email=email, phone=phone, subject=subject, unique_id=unique_id, timestamp=timestamp)

            send_html_email_async(SENDER_EMAIL, email, "Thank You for Reaching Out", user_html)
            send_html_email_async(SENDER_EMAIL, "bbtechworks@gmail.com", f"New Contact Request - {full_name}", admin_html)

        elif template_type == "job_application":
            full_name = data.get("full_name")
            email = data.get("email")
            position = data.get("position")
            date_applied = data.get("date")

            if not full_name or not email or not position or not date_applied:
                return jsonify({"error": "All fields are required for job applications."}), 400
            if not is_valid_email(email):
                return jsonify({"error": "Invalid email address."}), 400

            user_html = TEMPLATES["job_application"].format(
                full_name=full_name,
                position=position,
                date=date_applied,
                unique_id=unique_id,
                timestamp=timestamp
            )

            send_html_email_async(SENDER_EMAIL, email, "Application Received", user_html)

        else:
            return jsonify({"error": "Invalid template type."}), 400

        return jsonify({"message": "Email(s) sending in background."}), 200

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Byte Bandits Email API</title>
    </head>
    <body style="font-family: Arial, sans-serif; text-align: center; padding-top: 50px;">
        <h1>Byte Bandits Email API</h1>
        <p>Status: <strong style="color: green;">Working ✅</strong></p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)
