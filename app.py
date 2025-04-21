import csv
import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
from flask import Flask, render_template, request,send_file, redirect, url_for, flash, session,Response

from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("app_secret_Key")


EXCEL_FILE = "contact_data.csv"


EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
CSV_DOWNLOAD_PASSWORD = os.getenv("CSV_PASSWORD")


# Track the last visited page (excluding static & download-related pages)
@app.before_request
def store_last_page():
    if request.endpoint not in ("static", "download_csv", "verify_password", "get_previous_page"):
        session['last_page'] = request.path


# === Save form data to CSV ===
def save_to_excel(name, email, subject, message):
    file_exists = os.path.isfile(EXCEL_FILE)

    with open(EXCEL_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["customer_name", "customer_id", "customery_query", "query_description"])
        writer.writerow([name, email, subject, message])

# === Send thank-you email ===
def send_email(to_email, name):
    msg = EmailMessage()
    msg["Subject"] = "Thank You for Reaching Out to Coastal Crown Realty!"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    msg.set_content(f"""
    Hi {name},

    Thank you for contacting Coastal Crown Realty.

    We’ve received your message and our team will review it shortly. If your inquiry is urgent, please feel free to call us at (123) 456-7890 for immediate assistance.

    In the meantime, you're welcome to explore our property listings on our website.

    Best regards,  
    Coastal Crown Realty  
    Phone: (123) 456-7890  
    Website: www.coastalcrownrealty.com  
    Email: contactcoastalrealty@gmail.com
    """)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print("Email sending failed:", e)



# === Routes ===

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/properties")
def properties():
    return render_template("properties.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/blogs")
def blogs():
    return render_template("blogs.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        print("== FORM DATA RECEIVED ==")
        print("Name:", name)
        print("Email:", email)
        print("Subject:", subject)
        print("Message:", message)

        save_to_excel(name, email, subject, message)
        send_email(email, name)

        return render_template("contact.html", success=True)

    return render_template("contact.html")

@app.route("/download_csv", methods=["GET"])
def download_csv():
    previous = session.get('last_page', '/')
    session['previous_page'] = previous
    return render_template("csv_prompt.html", previous_page=previous)

@app.route("/get_csv")
def get_csv():
    return send_file(EXCEL_FILE, as_attachment=True)

@app.route("/verify_password", methods=["POST"])
def verify_password():
    password = request.form.get("password")

    if password == CSV_DOWNLOAD_PASSWORD:
        previous = session.get('last_page', '/')
        return render_template("download_and_redirect.html", previous_page=previous)
    else:
        flash("Incorrect password.")
        return redirect(url_for("download_csv"))





if __name__ == "__main__":
    app.run(debug=True)

