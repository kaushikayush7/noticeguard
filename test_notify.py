import httpx
from app.notify import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

print('Token loaded:', bool(TELEGRAM_BOT_TOKEN))
print('Chat ID loaded:', bool(TELEGRAM_CHAT_ID))

r = httpx.post(
    f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
    json={'chat_id': TELEGRAM_CHAT_ID, 'text': 'NoticeGuard Test Alert'},
    timeout=10
)
print('Status Code:', r.status_code)
print('Response Body:', r.text)
