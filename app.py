from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import time
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# Hardcoded constants
SENDER_EMAIL = "noreply.bytebandits@gmail.com"
APP_PASSWORD = "zurx cpxz tucp ktjf"
DEFAULT_SUBJECT = "Thank You for Reaching Out"

# Template paths
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "Templates")
ADMIN_EMAIL_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "admin_email.html")
USER_EMAIL_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "user_email.html")

# Load HTML templates with error handling
try:
    with open(ADMIN_EMAIL_TEMPLATE_PATH, "r") as file:
        ADMIN_EMAIL_TEMPLATE = file.read()
except Exception as e:
    logging.error(f"Error loading admin email template: {e}")
    ADMIN_EMAIL_TEMPLATE = ""

try:
    with open(USER_EMAIL_TEMPLATE_PATH, "r") as file:
        USER_EMAIL_TEMPLATE = file.read()
except Exception as e:
    logging.error(f"Error loading user email template: {e}")
    USER_EMAIL_TEMPLATE = ""

def is_valid_email(email):
    """Basic regex for validating an email address."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route("/send-email", methods=["POST"])
def send_email():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract inputs
        first_name = data.get("first_name")
        last_name = data.get("last_name", "")  # Optional field
        email = data.get("email")
        phone = data.get("phone", "Not provided")  # Optional field
        subject = data.get("subject", "No subject provided")

        if not first_name or not email or not is_valid_email(email):
            return jsonify({"error": "First Name, Email (valid) and Subject are required"}), 400

        full_name = f"{first_name} {last_name}".strip()
        
        # Generate unique ID and timestamp per request
        unique_id = "BB-" + str(int(time.time()))
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the user email content
        if USER_EMAIL_TEMPLATE:
            user_html_content = USER_EMAIL_TEMPLATE.format(name=full_name, unique_id=unique_id, timestamp=timestamp)
        else:
            return jsonify({"error": "Error loading user email template"}), 500

        user_subject = DEFAULT_SUBJECT

        # Prepare the admin email content
        if ADMIN_EMAIL_TEMPLATE:
            admin_html_content = ADMIN_EMAIL_TEMPLATE.format(name=full_name, email=email, phone=phone, subject=subject)
        else:
            return jsonify({"error": "Error loading admin email template"}), 500

        admin_subject = f"New Contact Request - {full_name} from {email}"

        # Send emails
        send_html_email(SENDER_EMAIL, email, user_subject, user_html_content)
        send_html_email(SENDER_EMAIL, "bbtechworks@gmail.com", admin_subject, admin_html_content)

        logging.info(f"Emails sent to {email} and admin.")

        return jsonify({"message": "Emails sent successfully!"}), 200

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

def send_html_email(sender, recipient, subject, html_content):
    """Send an HTML email."""
    try:
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

        logging.info(f"Email sent to {recipient} with subject {subject}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        raise

if __name__ == "__main__":
    app.run(debug=True)
