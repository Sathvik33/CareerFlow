from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
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
    
    model_config = {
        "from_attributes": True
    }