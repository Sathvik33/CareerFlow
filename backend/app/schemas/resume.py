from uuid import UUID
from pydantic import BaseModel

class ResumeUpload(BaseModel):
    resume_id: UUID
    message: str

class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    file_url: str
    model_config = {
        "from_attributes": True
    }