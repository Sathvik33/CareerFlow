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
    from app.models.match_result import MatchResult
    from datetime import datetime, timezone
    from sqlalchemy import cast, Date
    today = datetime.now(timezone.utc).date()
    
    results = (
        db.query(Job, MatchResult.final_score)
        .join(MatchResult, Job.id == MatchResult.job_id)
        .filter(MatchResult.user_id == current_user.id)
        .filter(cast(MatchResult.computed_at, Date) == today)
        .all()
    )
    
    jobs_with_scores = []
    for job, score in results:
        job.final_score = score
        jobs_with_scores.append(job)
        
    return jobs_with_scores

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

@router.delete("/{job_id}/match")
def delete_job_match(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.match_result import MatchResult
    match = db.query(MatchResult).filter(
        MatchResult.job_id == job_id,
        MatchResult.user_id == current_user.id
    ).first()
    
    if not match:
        raise HTTPException(status_code=404, detail="Job match not found")
        
    db.delete(match)
    db.commit()
    return {"message": "Job match deleted successfully"}
