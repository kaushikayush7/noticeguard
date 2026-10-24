import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
ALERT_PHONE_NUMBER = os.getenv("ALERT_PHONE_NUMBER")

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

def send_sms(row: dict) -> bool:
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER and ALERT_PHONE_NUMBER):
        return False
    
    badge = "Verified" if row.get("verified") else "Unverified"
    body = (f"NoticeGuard Alert: {row.get('exam') or row.get('title')} "
            f"[{row.get('notice_type')}] - {row.get('summary')} ({badge}) "
            f"Link: {row.get('pdf_url') or row.get('source_url')}")
    
    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    
    try:
        r = httpx.post(
            url,
            data={
                "To": ALERT_PHONE_NUMBER,
                "From": TWILIO_PHONE_NUMBER,
                "Body": body
            },
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=10
        )
        return r.status_code in [200, 201]
    except httpx.HTTPError:
        return False

def send_alerts(row: dict) -> dict:
    """Dispatches both Telegram and SMS notifications."""
    return {
        "telegram": send_telegram(row),
        "sms": send_sms(row)
    }
