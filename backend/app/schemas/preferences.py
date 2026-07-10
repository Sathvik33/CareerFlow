from enum import Enum
from pydantic import BaseModel
from uuid import UUID

class ExperienceLevel(str, Enum):
    student="student"
    fresher="fresher"
    junior="junior"
    mid="mid"
    senior="senior"

class JobType(str, Enum):
    internship="internship"
    full_time="full_time"
    part_time="part_time"
    contract="contract"

class WorkMode(str, Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"

class PreferenceCreate(BaseModel):
    roles: list[str]
    locations: list[str]
    experience_level: ExperienceLevel
    job_types: list[JobType]
    preferred_skills: list[str]
    work_modes: list[WorkMode]
    salary_min: int | None = None
    salary_max: int | None = None


class PreferenceUpdate(BaseModel):
    roles: list[str] | None = None
    locations: list[str] | None = None
    experience_level: ExperienceLevel | None = None
    job_types: list[JobType] | None = None
    preferred_skills: list[str] | None = None
    work_modes: list[WorkMode] | None = None

    salary_min: int | None = None
    salary_max: int | None = None


class PreferenceResponse(BaseModel):
    id: UUID
    user_id: UUID
    roles: list[str]
    locations: list[str]
    experience_level: ExperienceLevel
    job_types: list[JobType]
    preferred_skills: list[str]
    work_modes: list[WorkMode]
    salary_min: int | None
    salary_max: int | None

    model_config = {
        "from_attributes": True
    }

