import os
import httpx
import smtplib
import asyncio
import io
import csv
import random
from email.message import EmailMessage
from sqlalchemy.orm import Session
from app.models.notification import NotificationChannel
from app.models.notification_log import NotificationLog
from app.models.report import DailyReport
from app.models.user import User

def generate_leads_csv(jobs, match_results):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Company", "Location", "Remote", "Salary", "Match Score", "Apply URL", "Missing Skills"])
    
    match_dict = {str(m.job_id): m for m in match_results}
    
    for job in jobs:
        m = match_dict.get(str(job.id))
        score = f"{m.final_score:.1f}%" if m else "N/A"
        missing = ", ".join(m.missing_skills) if m and m.missing_skills else ""
        
        writer.writerow([
            job.title,
            job.company,
            job.location,
            "Yes" if job.remote else "No",
            job.salary or "N/A",
            score,
            job.apply_url,
            missing
        ])
    return output.getvalue()

async def dispatch_notifications(db: Session, user_id: str, report: DailyReport, new_jobs=None, match_results=None) -> list[NotificationLog]:
    if new_jobs is None:
        new_jobs = []
    if match_results is None:
        match_results = []
        
    user = db.query(User).filter(User.id == user_id).first()
    user_name = user.name if user and user.name else "there"
    fallback_email = user.email if user else None
        
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
            sender = os.environ.get("SMTP_EMAIL")
            password = os.environ.get("SMTP_PASSWORD")
            to_email = channel.destination if channel.destination else fallback_email
            
            if password and to_email:
                try:
                    msg = EmailMessage()
                    msg['Subject'] = f"CareerFlow Daily Report: {report.report_json.get('new_jobs', 0)} New Jobs Found!"
                    msg['From'] = sender
                    msg['To'] = to_email
                    
                    templates = [
                        f"Hey {user_name}! Waiting for today's reports? Here they are!",
                        f"Good news, {user_name}! We've found some fresh opportunities for you.",
                        f"Hi {user_name}! Your CareerFlow pipeline has finished mining the web. Check out these leads!",
                        f"Hey {user_name}, guess what? More jobs just dropped that match your profile perfectly."
                    ]
                    greeting = random.choice(templates)
                    
                    body = f"{greeting}\n\n"
                    body += f"New Jobs Found: {report.report_json.get('new_jobs', 0)}\n"
                    body += f"Top Companies: {', '.join(report.report_json.get('top_companies', []))}\n\n"
                    body += "Please find attached your tailored job leads for today.\n\nBest,\nCareerFlow Agent"
                    
                    msg.set_content(body)
                    
                    csv_content = generate_leads_csv(new_jobs, match_results)
                    msg.add_attachment(csv_content.encode('utf-8'), maintype='text', subtype='csv', filename='careerflow_leads.csv')
                    
                    def _send():
                        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                            server.login(sender, password)
                            server.send_message(msg)
                            
                    await asyncio.to_thread(_send)
                    status = "sent"
                except Exception as e:
                    print(f"Failed to send email: {e}")
                    status = "failed"

        log = NotificationLog(
            report_id=report.id,
            channel=channel.channel,
            status=status
        )
        db.add(log)
        logs.append(log)

    db.commit()
    return logs
