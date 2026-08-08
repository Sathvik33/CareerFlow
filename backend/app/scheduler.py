import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.resume import Resume
from app.models.preference import UserPreference
from app.pipeline.daily_pipeline import daily_pipeline

scheduler = AsyncIOScheduler()

async def run_daily_pipeline_for_all_users():
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        for user in users:
            resume = db.query(Resume).filter_by(user_id=user.id, is_default=True).first()
            if not resume:
                continue

            preferences = db.query(UserPreference).filter_by(user_id=user.id).first()
            state = {
                "db": db,
                "user_id": str(user.id),
                "resume": resume,
                "preferences": preferences,
                "target_websites": ["Greenhouse", "Lever", "RemoteOK", "Indeed"],
                "max_jobs": 10,
                "raw_jobs": [],
                "new_jobs": [],
                "jds": [],
                "match_results": [],
                "gap_analyses": [],
                "recommendations": [],
                "career_trends": None,
                "daily_report": None
            }
            # LangGraph supports async invoke for pipelines containing async nodes
            await daily_pipeline.ainvoke(state)

    except Exception as e:
        print(f"Error in scheduled job: {e}")
    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(run_daily_pipeline_for_all_users, 'cron', hour=21, minute=0)
    scheduler.start()

def shutdown_scheduler():
    scheduler.shutdown()
