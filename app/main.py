from fastapi import FastAPI
from app.routers import email, dashboard

app = FastAPI(
    title="NoticeGuard API",
    version="1.0.0",
    description="Real-time automated exam notice monitoring system powered by TinyFish AI Agent, Telegram, and SMTP."
)

# Mount the HTML dashboard at the root URL
app.include_router(dashboard.router, prefix="", tags=["Web Dashboard"])
app.include_router(email.router, prefix="/api/email", tags=["Email Notifications"])

@app.get("/health")
def health_check():
    return {
        "status": "online",
        "project": "NoticeGuard",
        "hackathon": "HackIIITD 2026",
        "endpoints": {
            "docs": "/docs",
            "email_test": "/api/email/send-test"
        }
    }
