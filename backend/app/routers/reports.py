from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import json
import asyncio
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.report import DailyReport
from app.schemas.report import DailyReportResponse
from app.models.resume import Resume
from app.models.preference import UserPreference
from app.pipeline.daily_pipeline import daily_pipeline
from app.db.database import SessionLocal
from pydantic import BaseModel

class ScanRequest(BaseModel):
    websites: list[str] = ["boards.greenhouse.io", "jobs.lever.co", "remoteok.com"]
    max_jobs: int = 5

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/latest", response_model=DailyReportResponse)
def get_latest_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = db.query(DailyReport).filter(DailyReport.user_id == current_user.id).order_by(DailyReport.created_at.desc()).first()
    if not report:
        raise HTTPException(status_code=404, detail="No reports found")
    return report

@router.get("/", response_model=list[DailyReportResponse])
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(DailyReport).filter(DailyReport.user_id == current_user.id).order_by(DailyReport.created_at.desc()).all()


async def run_pipeline_background(user_id: str):
    db = SessionLocal()
    try:
        resume = db.query(Resume).filter(Resume.user_id == user_id, Resume.is_default == True).first()
        if not resume:
            resume = db.query(Resume).filter(Resume.user_id == user_id).first()

        if not resume:
            print(f"Skipping pipeline for user {user_id}: No resume found")
            return

        preferences = db.query(UserPreference).filter(UserPreference.user_id == user_id).first()

        initial_state = {
            "db": db,
            "user_id": user_id,
            "resume": resume,
            "preferences": preferences,
            "raw_jobs": [],
            "new_jobs": [],
            "jds": [],
            "match_results": [],
            "gap_analyses": [],
            "recommendations": [],
            "daily_report": None
        }

        try:
            await daily_pipeline.ainvoke(initial_state)
        except Exception as e:
            print(f"Pipeline error for user {user_id}: {str(e)}")

    finally:
        db.close()


@router.post("/generate", status_code=202)
def trigger_report_generation(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume first.")
        
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        raise HTTPException(status_code=400, detail="Please set your preferences first.")

    background_tasks.add_task(run_pipeline_background, str(current_user.id))
    
@router.post("/stream-scan")
async def stream_report_generation(
    request: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    resume = db.query(Resume).filter(Resume.user_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume first.")
        
    pref = db.query(UserPreference).filter(UserPreference.user_id == current_user.id).first()
    if not pref:
        raise HTTPException(status_code=400, detail="Please set your preferences first.")

    async def event_stream():
        session = SessionLocal()
        try:
            yield f"data: {json.dumps({'message': 'Initializing AI Agent Pipeline...'})}\n\n"
            await asyncio.sleep(0.5)

            local_resume = session.query(Resume).filter(Resume.id == resume.id).first()

            initial_state = {
                "db": session,
                "user_id": str(current_user.id),
                "resume": local_resume,
                "preferences": pref,
                "target_websites": request.websites,
                "max_jobs": request.max_jobs,
                "raw_jobs": [],
                "new_jobs": [],
                "jds": [],
                "match_results": [],
                "gap_analyses": [],
                "recommendations": [],
                "daily_report": None
            }

            try:
                async for event in daily_pipeline.astream(initial_state):
                    for node_name, node_state in event.items():
                        log_msg = f"Completed step: {node_name}"
                        if node_name == "collect_jobs":
                            log_msg = f"Scraping websites (LinkedIn, Wellfound, Internshala)... Found {len(node_state.get('raw_jobs', []))} potential jobs."
                        elif node_name == "deduplicate":
                            log_msg = f"Removed duplicate listings. Kept {len(node_state.get('new_jobs', []))} fresh jobs."
                        elif node_name == "parse_jds":
                            log_msg = "Extracting structured JSON from Job Descriptions..."
                        elif node_name == "match_and_analyze":
                            log_msg = "Running semantic matching and gap analysis..."
                        elif node_name == "career_intelligence":
                            log_msg = "Identifying career trends and top missing skills..."
                        elif node_name == "report":
                            log_msg = "Generating final Daily Intelligence Report..."
                        elif node_name == "notify":
                            log_msg = "Dispatching notifications..."
                            
                        yield f"data: {json.dumps({'message': log_msg})}\n\n"
                        await asyncio.sleep(0.5) 
                
                yield f"data: {json.dumps({'message': 'Scan Complete!', 'done': True})}\n\n"
            except Exception as e:
                print(f"Streaming error: {e}")
                yield f"data: {json.dumps({'error': f'Pipeline failed: {str(e)}'})}\n\n"
        finally:
            session.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")
