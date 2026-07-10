from uuid import UUID
from pydantic import BaseModel

class NotificationChannelCreate(BaseModel):
    channel: str
    destination: str

class NotificationChannelUpdate(BaseModel):
    destination: str | None = None
    is_active: bool | None = None


class NotificationChannelResponse(BaseModel):
    id: UUID
    user_id: UUID
    channel: str
    destination: str
    is_active: bool
    model_config = {
        "from_attributes": True
    }