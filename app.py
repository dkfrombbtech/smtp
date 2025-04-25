from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.message import EmailMessage
import time
import os
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)

# Hardcoded constants
SENDER_EMAIL = "noreply.bytebandits@gmail.com"
APP_PASSWORD = "zurx cpxz tucp ktjf"
DEFAULT_SUBJECT = "Greetings from Byte Bandits."

# Template paths
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "Templates")
GREETINGS_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "greetings.html")
FROMUSER_TEMPLATE_PATH = os.path.join(TEMPLATES_DIR, "fromuser.html")

# Load HTML templates
with open(GREETINGS_TEMPLATE_PATH, "r") as file:
    GREETINGS_TEMPLATE = file.read()

with open(FROMUSER_TEMPLATE_PATH, "r") as file:
    FROMUSER_TEMPLATE = file.read()

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
        recipient_email = data.get("email")
        name = data.get("name", "User")
        phone = data.get("phone", "Not provided")
        message = data.get("message", "No message provided")

        if not recipient_email or not is_valid_email(recipient_email):
            return jsonify({"error": "Valid email is required"}), 400

        # Generate unique ID and timestamp per request
        unique_id = "BB-" + str(int(time.time()))
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Prepare the user email
        user_html_content = GREETINGS_TEMPLATE.format(name=name, unique_id=unique_id, timestamp=timestamp)
        user_subject = DEFAULT_SUBJECT

        # Prepare the admin email
        admin_html_content = FROMUSER_TEMPLATE.format(name=name, email=recipient_email, phone=phone, message=message)
        admin_subject = f"Email from User {name} signed up using the email {recipient_email}"

        # Send emails
        send_html_email(SENDER_EMAIL, recipient_email, user_subject, user_html_content)
        send_html_email(SENDER_EMAIL, "bbtechworks@gmail.com", admin_subject, admin_html_content)

        logging.info(f"Emails sent to {recipient_email} and admin.")

        return jsonify({"message": "Emails sent successfully!"}), 200

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

def send_html_email(sender, recipient, subject, html_content):
    """Send an HTML email."""
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

if __name__ == "__main__":
    app.run(debug=True)
