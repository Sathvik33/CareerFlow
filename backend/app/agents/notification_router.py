import os
import httpx
from sqlalchemy.orm import Session
from app.models.notification import NotificationChannel
from app.models.notification_log import NotificationLog
from app.models.report import DailyReport

async def dispatch_notifications(db: Session, user_id: str, report: DailyReport) -> list[NotificationLog]:
    channels = db.query(NotificationChannel).filter(
        NotificationChannel.user_id == user_id,
        NotificationChannel.is_active == True
    ).all()

    logs = []
    for channel in channels:
        status = "failed"
        if channel.channel.lower() == "telegram":
            bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
            if bot_token:
                try:
                    report_text = f"CareerFlow Daily Report:\nNew Jobs: {report.report_json.get('new_jobs', 0)}\nRecommended Action: {report.report_json.get('recommended_action', '')}"
                    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(url, json={
                            "chat_id": channel.destination,
                            "text": report_text
                        })
                        if resp.status_code == 200:
                            status = "sent"
                except Exception as e:
                    pass
        elif channel.channel.lower() == "email":
            # Stub for email
            status = "sent_stub"

        log = NotificationLog(
            report_id=report.id,
            channel=channel.channel,
            status=status
        )
        db.add(log)
        logs.append(log)

    db.commit()
    return logs
