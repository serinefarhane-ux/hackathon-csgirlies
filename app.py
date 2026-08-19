app.py:
import os
import re
import smtplib
import sqlite3
from email.message import EmailMessage
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_FILE = "subscribers.db"

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def init_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def valid_email(email):
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None


def save_subscriber(email):
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO subscribers (email) VALUES (?)",
            (email,)
        )
        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_subscribers():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute("SELECT email FROM subscribers")
    subscribers = [row[0] for row in cursor.fetchall()]

    connection.close()

    return subscribers


def send_email(to_email, subject, body):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise RuntimeError("Email credentials are not configured.")

    message = EmailMessage()
    message["From"] = EMAIL_ADDRESS
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(message)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json()

    if not data or "email" not in data:
        return jsonify({
            "success": False,
            "message": "Please enter an email address."
        }), 400

    email = data["email"].strip().lower()

    if not valid_email(email):
        return jsonify({
            "success": False,
            "message": "Please enter a valid email address."
        }), 400

    saved = save_subscriber(email)

    if not saved:
        return jsonify({
            "success": False,
            "message": "This email is already subscribed."
        }), 409

    try:
        send_email(
            email,
            "Welcome to Wellify 💜",
            """Hi!

Thanks for subscribing to Wellify 💜

You'll receive our newsletter with wellbeing tips, activities and updates.

Take care,
The Wellify Team
"""
        )

    except Exception as error:
        print("Email error:", error)

        return jsonify({
            "success": True,
            "message": "You're subscribed! Your welcome email could not be sent right now."
        })

    return jsonify({
        "success": True,
        "message": "You're subscribed! Check your inbox 💜"
    })


@app.route("/subscribers", methods=["GET"])
def subscribers():
    return jsonify({
        "subscribers": get_subscribers()
    })


init_database()

if __name__ == "__main__":
    app.run(debug=True)
