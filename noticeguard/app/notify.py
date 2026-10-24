import httpx

from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram(row: dict) -> bool:
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return False
    badge = "Verified official source" if row["verified"] else "Unverified source"
    text = (f"{row['exam'] or row['title']}\n[{row['notice_type']}] {row['summary']}\n"
            f"{row['published_date']} | {badge}\n{row['pdf_url'] or row['source_url']}")
    try:
        r = httpx.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                       json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
        return r.status_code == 200
    except httpx.HTTPError:
        return False
