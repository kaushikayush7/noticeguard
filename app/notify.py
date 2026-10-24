import smtplib
import os
import sqlite3
import httpx
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER", "noticeguardbot@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL = os.getenv("ALERT_EMAIL", "noticeguardbot@gmail.com")

def send_email_alert(notice_data: dict):
    if not SMTP_PASSWORD:
        print("SMTP Password not set. Skipping email alert.")
        return
    
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = ALERT_EMAIL
        msg["Subject"] = f"🚨 NoticeGuard Alert: {notice_data.get('exam')}"

        body = f"""
Official NoticeGuard Alert:

Exam: {notice_data.get('exam')}
Type: {notice_data.get('notice_type')}
Summary: {notice_data.get('summary')}
Date: {notice_data.get('published_date')}
Source: {notice_data.get('source_url')}
        """
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, ALERT_EMAIL, msg.as_string())
        server.quit()
        print(f"-> [EMAIL SENT] Successfully sent alert email for {notice_data.get('exam')}")
    except Exception as e:
        print(f"-> Error sending email alert: {e}")

def send_telegram_alert(notice_data: dict):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return

    conn = sqlite3.connect("noticeguard.db")
    c = conn.cursor()
    try:
        c.execute('''
            CREATE TABLE IF NOT EXISTS telegram_subscribers (
                chat_id TEXT PRIMARY KEY,
                subscribed_at TEXT
            )
        ''')
        subscribers = c.execute("SELECT chat_id FROM telegram_subscribers").fetchall()
    except sqlite3.OperationalError:
        subscribers = []
    conn.close()

    chat_ids = [sub[0] for sub in subscribers]
    env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if env_chat_id and env_chat_id not in chat_ids:
        chat_ids.append(env_chat_id)

    message = (
        f"🚨 *NoticeGuard Alert*\n\n"
        f"📌 *Exam:* {notice_data.get('exam')}\n"
        f"📢 *Type:* {notice_data.get('notice_type')}\n"
        f"📝 *Summary:* {notice_data.get('summary')}\n"
        f"📅 *Date:* {notice_data.get('published_date')}\n\n"
        f"🔗 [View Official Source]({notice_data.get('source_url')})"
    )

    for chat_id in chat_ids:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        try:
            httpx.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Failed to send Telegram alert to {chat_id}: {e}")

def send_alerts(notice_data: dict):
    send_email_alert(notice_data)
    send_telegram_alert(notice_data)
