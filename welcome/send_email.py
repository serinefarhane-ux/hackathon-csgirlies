import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_welcome_email(target_email, user_name):
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    if not sender_email or not sender_password:
        print("Error: Missing email environment credentials.")
        sys.exit(1)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Welcome aboard, {user_name if user_name else 'Friend'}! 🚀"
    msg["From"] = f"My GitHub Website <{sender_email}>"
    msg["To"] = target_email

    html_content = f"""
    <h3>Hi {user_name if user_name else 'there'},</h3>
    <p>Thanks for subscribing to my newsletter directly from my GitHub page!</p>
    <p>Best,<br>Your Python Bot</p>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, target_email, msg.as_string())

        print(f"Successfully sent welcome email to {target_email}")

    except Exception as e:
        print(f"SMTP Server Connection Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    client_payload = json.loads(os.getenv("GITHUB_CLIENT_PAYLOAD", "{}"))

    email = client_payload.get("email")
    name = client_payload.get("name", "Friend")

    if email:
        send_welcome_email(email, name)
    else:
        print("Error: No email payload provided by the form.")
