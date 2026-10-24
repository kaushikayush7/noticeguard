import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

print(f"Testing STARTTLS connection (Port {SMTP_PORT}) for user: {SMTP_USER} -> target: {ALERT_EMAIL}")

msg = MIMEMultipart()
msg["From"] = SMTP_USER
msg["To"] = ALERT_EMAIL
msg["Subject"] = "NoticeGuard SMTP Diagnostic Test"
msg.attach(MIMEText("If you see this email, your NoticeGuard STARTTLS email setup is working perfectly!", "plain"))

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        print("Initiating STARTTLS...")
        server.starttls()
        server.ehlo()
        print("Logging in...")
        server.login(SMTP_USER, SMTP_PASSWORD)
        print("Sending test email...")
        server.send_message(msg)
    print("SUCCESS: Email sent successfully!")
except Exception as e:
    print("\n--- SMTP ERROR CAUGHT ---")
    print(e)
