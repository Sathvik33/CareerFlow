from uuid import UUID
from pydantic import BaseModel

class DailyReportResponse(BaseModel):
    id: UUID
    jobs_found: int
    top_matches: int
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]