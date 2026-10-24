import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ALERT_EMAIL = os.getenv("ALERT_EMAIL")

def send_telegram(row: dict) -> bool:
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return False
    badge = "Verified official source" if row.get("verified") else "Unverified source"
    text = (f"{row.get('exam') or row.get('title')}\n[{row.get('notice_type')}] {row.get('summary')}\n"
            f"{row.get('published_date')} | {badge}\n{row.get('pdf_url') or row.get('source_url')}")
    try:
        r = httpx.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                       json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        return r.status_code == 200
    except httpx.HTTPError:
        return False

def send_email(row: dict, to_email: str = None) -> bool:
    recipient = to_email or ALERT_EMAIL
    if not (SMTP_USER and SMTP_PASSWORD and recipient):
        return False
    
    badge = "Verified official source" if row.get("verified") else "Unverified source"
    subject = f"NoticeGuard Alert: {row.get('exam') or row.get('title')} [{row.get('notice_type')}]"
    body = (f"Exam/Title: {row.get('exam') or row.get('title')}\n"
            f"Notice Type: {row.get('notice_type')}\n"
            f"Summary: {row.get('summary')}\n"
            f"Published Date: {row.get('published_date')}\n"
            f"Status: {badge}\n\n"
            f"Link: {row.get('pdf_url') or row.get('source_url')}")
    
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False

def send_alerts(row: dict, to_email: str = None) -> dict:
    """Dispatches both Telegram and Email notifications simultaneously."""
    return {
        "telegram": send_telegram(row),
        "email": send_email(row, to_email=to_email)
    }
