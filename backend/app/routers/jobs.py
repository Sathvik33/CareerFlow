from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.job import Job
from app.schemas.job import JobResponse
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.get("/", response_model=list[JobResponse])
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    return db.query(Job).filter(Job.scraped_at >= yesterday).all()

@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
