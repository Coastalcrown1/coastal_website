import csv
import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage
from flask import Flask, render_template, request
load_dotenv()

app = Flask(__name__)

EXCEL_FILE = "contact_data.csv"

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def save_to_excel(name, email, subject, message):
    file_exists = os.path.isfile(EXCEL_FILE)

    with open(EXCEL_FILE, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Write headers if file does not exist
        if not file_exists:
            writer.writerow(["customer_name", "customer_id", "customery_query", "query_description"])

        # Write form data
        writer.writerow([name, email, subject, message])
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
            smtp.sendmail(EMAIL_USER, to_email, msg.as_string())
    except Exception as e:
        print("Email sending failed:", e)

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

if __name__ == "__main__":
    app.run(debug=True)
