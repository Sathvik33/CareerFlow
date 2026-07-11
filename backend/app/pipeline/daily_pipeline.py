import asyncio
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from app.models.preference import UserPreference
from app.agents.models import JDModel, GapAnalysisModel, RecommendationModel, DailyReportModel, CareerTrendModel
from app.agents.job_search import search_jobs
from app.agents.dedup import deduplicate_jobs
from app.agents.jd_parser import parse_jd
from app.agents.semantic_match import compute_semantic_score
from app.agents.bm25_match import compute_bm25_score
from app.agents.gap_analysis import analyze_gap
from app.agents.recommendation import generate_recommendations
from app.agents.career_intelligence import analyze_career_trends
from app.agents.report_generator import generate_daily_report
from app.agents.notification_router import dispatch_notifications
from app.models.job import Job
from app.models.resume import Resume
from app.models.match_result import MatchResult
from sqlalchemy.orm import Session

class CareerFlowState(TypedDict):
    db: Session
    user_id: str
    resume: Resume
    preferences: UserPreference | None
    target_websites: list[str]
    max_jobs: int
    raw_jobs: list[dict]
    new_jobs: list[Job]
    jds: list[JDModel]
    match_results: list[MatchResult]
    gap_analyses: list[GapAnalysisModel]
    recommendations: list[RecommendationModel]
    career_trends: CareerTrendModel
    daily_report: DailyReportModel

async def collect_jobs(state: CareerFlowState):
    preferences = state.get("preferences")
    max_jobs = state.get("max_jobs", 50)
    target_websites = state.get("target_websites", [])

    print(f"[collect_jobs] Starting job aggregation...")
    raw_jobs = await search_jobs(preferences, max_jobs, target_websites)
    return {"raw_jobs": raw_jobs}

def deduplicate(state: CareerFlowState):
    db = state["db"]
    new_jobs = deduplicate_jobs(state["raw_jobs"], db)
    
    # We enforce max_jobs AFTER deduplication, so we don't accidentally
    # drop all new jobs just because the first batch were duplicates!
    max_jobs = state.get("max_jobs", 50)
    
    # Shuffle new_jobs to get a variety of sources instead of just the first ones
    import random
    random.shuffle(new_jobs)
    
    if len(new_jobs) > max_jobs:
        # Keep only the requested amount, and delete the rest from the DB to prevent them 
        # from becoming permanently orphaned/un-analyzed
        orphaned_jobs = new_jobs[max_jobs:]
        new_jobs = new_jobs[:max_jobs]
        
        for orphan in orphaned_jobs:
            db.delete(orphan)
        db.commit()
        
    return {"new_jobs": new_jobs}

async def parse_jds(state: CareerFlowState):
    db = state["db"]
    tasks = [parse_jd(job.description) for job in state["new_jobs"]]
    jds = await asyncio.gather(*tasks) if tasks else []
    
    for i, job in enumerate(state["new_jobs"]):
        parsed_jd = jds[i]
        job.structured_json = parsed_jd.model_dump()
        
        # Explicitly save the extracted skills list to the Job row
        if parsed_jd.skills:
            job.skills = [s for s in parsed_jd.skills if s is not None]
            
        # Explicitly save the extracted salary to the Job row if it was found
        if parsed_jd.salary and not job.salary:
            job.salary = parsed_jd.salary
            
    db.commit()
    return {"jds": jds}

from app.agents.job_embedder import embed_jobs

def embed_new_jobs(state: CareerFlowState):
    db = state["db"]
    new_jobs = state["new_jobs"]
    if new_jobs:
        embed_jobs(db, new_jobs)
    return {}

async def match_and_analyze(state: CareerFlowState):
    db = state["db"]
    resume = state["resume"]
    user_id = state["user_id"]

    # Delete previous match results for this user that are OLDER than today
    from app.models.match_result import MatchResult
    from datetime import datetime, timezone
    from sqlalchemy import cast, Date
    today = datetime.now(timezone.utc).date()
    
    db.query(MatchResult).filter(
        MatchResult.user_id == user_id,
        cast(MatchResult.computed_at, Date) < today
    ).delete(synchronize_session=False)
    db.commit()

    match_results = []
    gap_analyses = []
    recommendations = []
    
    gap_tasks = []
    match_data = []

    for i, job in enumerate(state["new_jobs"]):
        jd = state["jds"][i]

        sem_score = compute_semantic_score(db, str(resume.id), str(job.id))
        bm25_score = compute_bm25_score(resume.raw_text, job.description)
        final_score = (sem_score * 0.7) + (bm25_score * 0.3)
        
        # Reward remote preferences if applicable
        preferences = state.get("preferences")
        if preferences and "Remote" in (preferences.locations or []) and job.remote:
            final_score += 5.0
            final_score = min(100.0, final_score)

        from app.agents.models import ResumeModel
        if resume.structured_json:
            parsed_resume = ResumeModel(**resume.structured_json)
        else:
            parsed_resume = ResumeModel(skills=[], projects=[], experience=[], education=[])

        # Prepare arguments for the async tasks
        gap_tasks.append(analyze_gap(parsed_resume, jd, sem_score, bm25_score))
        match_data.append({
            "job_id": job.id,
            "sem_score": sem_score,
            "bm25_score": bm25_score,
            "final_score": final_score
        })

    # Execute gap analysis concurrently
    gap_analyses = await asyncio.gather(*gap_tasks) if gap_tasks else []
    
    # Execute recommendations concurrently
    rec_tasks = [generate_recommendations(gap) for gap in gap_analyses]
    recommendations = await asyncio.gather(*rec_tasks) if rec_tasks else []

    from app.models.recommendation import Recommendation

    for i, data in enumerate(match_data):
        gap = gap_analyses[i]
        rec = recommendations[i]
        mr = MatchResult(
            user_id=user_id,
            job_id=data["job_id"],
            resume_id=resume.id,
            semantic_score=data["sem_score"],
            bm25_score=data["bm25_score"],
            final_score=data["final_score"],
            missing_skills=gap.missing_skills,
            strengths=gap.strengths
        )
        db.add(mr)
        db.flush()

        rec_record = Recommendation(
            match_result_id=mr.id,
            action_items=rec.action_items,
            projected_improvement_pct=rec.projected_improvement_pct
        )
        db.add(rec_record)
        match_results.append(mr)

    db.commit()
    return {
        "match_results": match_results,
        "gap_analyses": gap_analyses,
        "recommendations": recommendations
    }

def career_intelligence(state: CareerFlowState):
    trends = analyze_career_trends(state["jds"])
    return {"career_trends": trends}

async def report(state: CareerFlowState):
    new_jobs_count = len(state["new_jobs"])
    high_match_jobs_count = sum(1 for m in state["match_results"] if m.final_score > 70)
    top_companies = [job.company for job in state["new_jobs"]][:5]

    daily_rep = await generate_daily_report(
        new_jobs_count=new_jobs_count,
        high_match_jobs_count=high_match_jobs_count,
        top_companies=top_companies,
        gap_analysis_list=state["gap_analyses"],
        recommendation_list=state["recommendations"]
    )

    from app.models.report import DailyReport
    db = state["db"]
    dr = DailyReport(
        user_id=state["user_id"],
        report_json=daily_rep.model_dump()
    )
    db.add(dr)
    db.commit()

    return {"daily_report": daily_rep}

async def notify(state: CareerFlowState):
    db = state["db"]
    from app.models.report import DailyReport
    db_report = db.query(DailyReport).filter_by(user_id=state["user_id"]).order_by(DailyReport.created_at.desc()).first()
    if db_report:
        await dispatch_notifications(
            db, 
            state["user_id"], 
            db_report, 
            new_jobs=state.get("new_jobs", []), 
            match_results=state.get("match_results", [])
        )
    return {}

builder = StateGraph(CareerFlowState)

builder.add_node("collect_jobs", collect_jobs)
builder.add_node("deduplicate", deduplicate)
builder.add_node("embed_new_jobs", embed_new_jobs)
builder.add_node("parse_jds", parse_jds)
builder.add_node("match_and_analyze", match_and_analyze)
builder.add_node("career_intelligence", career_intelligence)
builder.add_node("report", report)
builder.add_node("notify", notify)

builder.add_edge(START, "collect_jobs")
builder.add_edge("collect_jobs", "deduplicate")
builder.add_edge("deduplicate", "embed_new_jobs")
builder.add_edge("embed_new_jobs", "parse_jds")
builder.add_edge("parse_jds", "match_and_analyze")
builder.add_edge("match_and_analyze", "career_intelligence")
builder.add_edge("career_intelligence", "report")
builder.add_edge("report", "notify")
builder.add_edge("notify", END)

daily_pipeline = builder.compile()
