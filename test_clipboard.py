import httpx

token = "8719246485:AAElogLPP8LpnkmLGaerYLxHA0IAFlukLPM"
chat_id = "8608954908"

r = httpx.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json={"chat_id": chat_id, "text": "NoticeGuard Direct Clipboard Test"},
    timeout=10
)
print("Status Code:", r.status_code)
print("Response Body:", r.text)
