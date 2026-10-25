from fastapi import APIRouter
from app.notify import send_alerts

router = APIRouter()

@router.post("/send-test")
def trigger_test_email():
    sample_notice = {
        "exam": "NoticeGuard Test Exam 2026",
        "notice_type": "Test Notification",
        "summary": "This is a test notification dispatched via SMTP STARTTLS to verify the system.",
        "published_date": "2026-10-25",
        "source_url": "https://example.com"
    }
    try:
        send_alerts(sample_notice)
        return {"status": "success", "message": "Test email and Telegram alert dispatched successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
