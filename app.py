from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import time
import os
import re
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

SENDER_EMAIL = "noreply.bytebandits@gmail.com"
APP_PASSWORD = "zurx cpxz tucp ktjf"
DEFAULT_USER_SUBJECT = "Thank You for Getting in Touch - Byte Bandits"
ADMIN_EMAIL = "bbtechworks@gmail.com"

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "Templates")
USER_EMAIL_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "user_email.html")
ADMIN_EMAIL_PATH = os.path.join(TEMPLATES_DIR, "admin_email.html")

with open(USER_EMAIL_TEMPLATE_PATH, "r", encoding="utf-8") as file:
    USER_EMAIL_TEMPLATE = file.read()

with open(ADMIN_EMAIL_PATH, "r", encoding="utf-8") as file:
    ADMIN_EMAIL = file.read()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_html_email(sender, recipient, subject, html_content):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content("This email contains HTML content. Please view it in an email client that supports HTML.")
    msg.add_alternative(html_content, subtype="html")

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, APP_PASSWORD)
        server.send_message(msg)

@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided."}), 400

        first_name = data.get("first_name")
        last_name = data.get("last_name", "")
        email = data.get("email")
        phone = data.get("phone", "Not provided")
        subject = data.get("subject")

        if not first_name or not email or not subject:
            return jsonify({"error": "First Name, Email, and Subject are required."}), 400

        if not is_valid_email(email):
            return jsonify({"error": "A valid email is required."}), 400

        full_name = f"{first_name} {last_name}".strip()
        unique_id = "BB-" + str(int(time.time()))
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        user_html = USER_EMAIL_TEMPLATE.format(name=full_name, unique_id=unique_id, timestamp=timestamp)
        admin_html = ADMIN_EMAIL.format(name=full_name, email=email, phone=phone, subject=subject)

        send_html_email(SENDER_EMAIL, email, DEFAULT_USER_SUBJECT, user_html)
        send_html_email(SENDER_EMAIL, ADMIN_EMAIL, f"New Contact Request: {subject}", admin_html)

        logging.info(f"Emails sent to {email} and admin.")

        return jsonify({"message": f"Thank you {first_name}! We've received your request and will get in touch soon."}), 200

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": "An error occurred while sending emails."}), 500

if __name__ == "__main__":
    app.run(debug=True)
