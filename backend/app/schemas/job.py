from uuid import UUID
from pydantic import BaseModel

class JobResponse(BaseModel):
    id: UUID
    title: str
    company: str
    location: str
    job_type: str
    source: str
    apply_url: str 
    model_config = {
        "from_attributes": True
    }