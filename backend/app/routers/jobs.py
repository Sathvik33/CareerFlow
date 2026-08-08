from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import cast, Date, or_
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.database import get_db
from app.models.job import Job
from app.models.match_result import ACTIVE_PIPELINE, MATCH_STATUSES, MatchResult
from app.models.recommendation import Recommendation
from app.models.user import User
from app.schemas.job import JobResponse, MatchStatusUpdate

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def _job_to_response(job: Job, match: MatchResult, action_items=None, improvement=None) -> JobResponse:
    return JobResponse(
        id=job.id,
        title=job.title,
        company=job.company,
        location=job.location,
        source=job.source,
        apply_url=job.apply_url,
        remote=job.remote,
        salary=job.salary,
        employment_type=job.employment_type,
        experience_level=job.experience_level,
        skills=job.skills,
        posted_date=job.posted_date,
        scraped_at=job.scraped_at,
        final_score=match.final_score,
        semantic_score=match.semantic_score,
        bm25_score=match.bm25_score,
        missing_skills=match.missing_skills or [],
        strengths=match.strengths or [],
        match_id=match.id,
        status=match.status or "matched",
        notes=match.notes,
        status_updated_at=match.status_updated_at,
        action_items=action_items,
        projected_improvement_pct=improvement,
    )


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    status: str | None = Query(None, description="Filter by pipeline status"),
    include_dismissed: bool = Query(False),
    days: int = Query(30, ge=1, le=180),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = datetime.now(timezone.utc).date()
    cutoff = today - timedelta(days=days)

    q = (
        db.query(Job, MatchResult, Recommendation)
        .join(MatchResult, Job.id == MatchResult.job_id)
        .outerjoin(Recommendation, Recommendation.match_result_id == MatchResult.id)
        .filter(MatchResult.user_id == current_user.id)
    )

    if status:
        if status not in MATCH_STATUSES:
            raise HTTPException(status_code=400, detail=f"Invalid status. Use one of: {MATCH_STATUSES}")
        q = q.filter(MatchResult.status == status)
    elif not include_dismissed:
        q = q.filter(MatchResult.status != "dismissed")

    q = q.filter(
        or_(
            cast(MatchResult.computed_at, Date) >= cutoff,
            MatchResult.status.in_(ACTIVE_PIPELINE),
        )
    )

    q = q.order_by(MatchResult.final_score.desc())
    rows = q.all()

    seen = set()
    out = []
    for job, match, rec in rows:
        if match.id in seen:
            continue
        seen.add(match.id)
        out.append(
            _job_to_response(
                job,
                match,
                action_items=(rec.action_items if rec else None),
                improvement=(rec.projected_improvement_pct if rec else None),
            )
        )
    return out


@router.get("/pipeline/summary")
def pipeline_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from sqlalchemy import func

    rows = (
        db.query(MatchResult.status, func.count(MatchResult.id))
        .filter(MatchResult.user_id == current_user.id)
        .filter(MatchResult.status != "dismissed")
        .group_by(MatchResult.status)
        .all()
    )
    counts = {s: 0 for s in MATCH_STATUSES if s != "dismissed"}
    for status, count in rows:
        counts[status] = count
    return counts


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(Job, MatchResult, Recommendation)
        .join(MatchResult, Job.id == MatchResult.job_id)
        .outerjoin(Recommendation, Recommendation.match_result_id == MatchResult.id)
        .filter(Job.id == job_id, MatchResult.user_id == current_user.id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Job match not found")
    job, match, rec = row
    return _job_to_response(
        job,
        match,
        action_items=(rec.action_items if rec else None),
        improvement=(rec.projected_improvement_pct if rec else None),
    )


@router.patch("/{job_id}/match", response_model=JobResponse)
def update_match_status(
    job_id: UUID,
    body: MatchStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if body.status not in MATCH_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Use one of: {MATCH_STATUSES}")

    match = (
        db.query(MatchResult)
        .filter(MatchResult.job_id == job_id, MatchResult.user_id == current_user.id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Job match not found")

    match.status = body.status
    match.status_updated_at = datetime.now(timezone.utc)
    if body.notes is not None:
        match.notes = body.notes
    db.commit()
    db.refresh(match)

    job = db.query(Job).filter(Job.id == job_id).first()
    rec = (
        db.query(Recommendation)
        .filter(Recommendation.match_result_id == match.id)
        .first()
    )
    return _job_to_response(
        job,
        match,
        action_items=(rec.action_items if rec else None),
        improvement=(rec.projected_improvement_pct if rec else None),
    )


@router.delete("/{job_id}/match")
def delete_job_match(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft-dismiss: keeps the row for history instead of hard delete."""
    match = (
        db.query(MatchResult)
        .filter(MatchResult.job_id == job_id, MatchResult.user_id == current_user.id)
        .first()
    )
    if not match:
        raise HTTPException(status_code=404, detail="Job match not found")

    match.status = "dismissed"
    match.status_updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Job match dismissed"}
