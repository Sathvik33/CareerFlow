from uuid import UUID
from pydantic import BaseModel

class DailyReportResponse(BaseModel):
    id: UUID
    report_json: dict
    model_config = {
        "from_attributes": True
    }