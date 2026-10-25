from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

response = client.post("/api/notifications/email", json={
    "email": "ayushkaushikk7@gmail.com",
    "exam": "JEE Main 2026",
    "notice_type": "Exam Dates",
    "summary": "NTA has officially released the exam schedule dates.",
    "published_date": "2026-03-30",
    "verified": True,
    "source_url": "https://example.com/notice.pdf"
})

print("Status Code:", response.status_code)
print("Response JSON:", response.json())
