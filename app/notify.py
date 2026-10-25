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

def get_subscribers_for_exam(exam_id: str = None):
    conn = sqlite3.connect("noticeguard.db")
    c = conn.cursor()
    try:
        # Fetch aspirants who explicitly selected this exam, or fetch all aspirants if exam_id not filtered
        if exam_id:
            query = '''
                SELECT DISTINCT a.gmail, a.telegram_chat_id 
                FROM aspirants a
                JOIN aspirant_exams ae ON a.id = ae.aspirant_id
                WHERE ae.exam_id = ?
            '''
            subscribers = c.execute(query, (exam_id,)).fetchall()
        else:
            subscribers = []

        # If no specific preferences found, fallback to all registered aspirants
        if not subscribers:
            subscribers = c.execute("SELECT gmail, telegram_chat_id FROM aspirants").fetchall()
            
    except sqlite3.OperationalError:
        subscribers = []
    conn.close()
    return subscribers

def send_alerts(notice_data: dict):
    exam_id = notice_data.get("exam")
    subscribers = get_subscribers_for_exam(exam_id)

    # Fallback to .env defaults if no logged-in aspirants exist in DB
    if not subscribers:
        env_email = os.getenv("ALERT_EMAIL", SMTP_USER)
        env_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        subscribers = [(env_email, env_chat_id)]

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    for email, chat_id in subscribers:
        # 1. Send Email to Aspirant
        if email and SMTP_PASSWORD:
            try:
                msg = MIMEMultipart()
                msg["From"] = SMTP_USER
                msg["To"] = email
                msg["Subject"] = f"🚨 NoticeGuard Alert: {notice_data.get('exam')}"

                body = f"""
Hello Aspirant,

A new official notice has been published for your tracked exam:

Exam: {notice_data.get('exam')}
Type: {notice_data.get('notice_type')}
Summary: {notice_data.get('summary')}
Date: {notice_data.get('published_date')}

Official Source Link: {notice_data.get('source_url')}

Best regards,
NoticeGuard Intelligence Team
                """
                msg.attach(MIMEText(body, "plain"))

                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, email, msg.as_string())
                server.quit()
                print(f"-> [EMAIL SENT] Alert sent to aspirant: {email}")
            except Exception as e:
                print(f"-> Failed to send email to {email}: {e}")

        # 2. Send Telegram Alert to Aspirant
        if chat_id and token:
            message = (
                f"🚨 *NoticeGuard Alert*\n\n"
                f"📌 *Exam:* {notice_data.get('exam')}\n"
                f"📢 *Type:* {notice_data.get('notice_type')}\n"
                f"📝 *Summary:* {notice_data.get('summary')}\n"
                f"📅 *Date:* {notice_data.get('published_date')}\n\n"
                f"🔗 [View Official Source]({notice_data.get('source_url')})"
            )
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }
            try:
                httpx.post(url, json=payload, timeout=10)
                print(f"-> [TELEGRAM SENT] Alert sent to chat ID: {chat_id}")
            except Exception as e:
                print(f"-> Failed to send Telegram alert to {chat_id}: {e}")
