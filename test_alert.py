import asyncio
from app.alerts import send_telegram_alert

async def test():
    await send_telegram_alert(
        title="UPSC Civil Services Corrigendum 2026",
        summary="Date extended for application submission.",
        url="https://upsc.gov.in/sample-notice",
        source="UPSC"
    )

asyncio.run(test())
