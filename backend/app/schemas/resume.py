from uuid import UUID
from pydantic import BaseModel

class ResumeUpload(BaseModel):
    resume_id: UUID
    message: str

class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    file_url: str
    is_default: bool
    raw_text: str | None
    structured_json: dict | None
    model_config = {
        "from_attributes": True
    }