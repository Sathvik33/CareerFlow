from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, List


class JobResponse(BaseModel):
    id: UUID
    title: str
    company: str
    location: Optional[str] = None
    source: str
    apply_url: str
    remote: bool = False
    salary: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    skills: Optional[List[str]] = None
    posted_date: Optional[datetime] = None
    scraped_at: datetime
    final_score: Optional[float] = None
    semantic_score: Optional[float] = None
    bm25_score: Optional[float] = None
    missing_skills: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    match_id: Optional[UUID] = None
    status: Optional[str] = "matched"
    notes: Optional[str] = None
    status_updated_at: Optional[datetime] = None
    action_items: Optional[List[str]] = None
    projected_improvement_pct: Optional[float] = None

    model_config = {"from_attributes": True}


class MatchStatusUpdate(BaseModel):
    status: str = Field(..., description="matched|saved|applied|interview|offer|rejected|dismissed")
    notes: Optional[str] = None
