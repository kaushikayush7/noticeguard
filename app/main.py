from fastapi import FastAPI
from app.routers import email

app = FastAPI(
    title="NoticeGuard API",
    version="1.0.0",
    description="Real-time automated exam notice monitoring system powered by TinyFish AI Agent, Telegram, and SMTP."
)

app.include_router(email.router, prefix="/api/email", tags=["Email Notifications"])

@app.get("/")
def root():
    return {
        "status": "online",
        "project": "NoticeGuard",
        "hackathon": "HackIIITD 2026",
        "endpoints": {
            "docs": "/docs",
            "email_test": "/api/email/send-test"
        }
    }
