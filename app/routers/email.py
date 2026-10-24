from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from app.notify import send_email

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

class EmailAlertRequest(BaseModel):
    email: EmailStr
    exam: str
    notice_type: str
    summary: str
    published_date: str
    verified: bool = True
    pdf_url: str = None
    source_url: str = None

@router.post("/email")
async def trigger_email_alert(payload: EmailAlertRequest, background_tasks: BackgroundTasks):
    """API endpoint to dispatch email alerts asynchronously."""
    notice_data = payload.dict()
    
    # Dispatch email in the background to keep API response lightning fast
    background_tasks.add_task(send_email, notice_data, to_email=payload.email)
    
    return {
        "status": "success", 
        "message": f"Email alert queued successfully for {payload.email}"
    }
