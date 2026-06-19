from uuid import UUID
from pydantic import BaseModel

class NotificationChannelCreate(BaseModel):
    channel: str
    desination: str


class NotificationChannelResponse(BaseModel):
    id: UUID
    user_id: UUID
    channel: str
    destination: str
    is_active: bool
    model_config = {
        "from_attributes": True
    }