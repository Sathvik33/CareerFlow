from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.notification import NotificationChannel
from app.schemas.notification import NotificationChannelCreate, NotificationChannelUpdate, NotificationChannelResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/channels", response_model=NotificationChannelResponse)
def add_notification_channel(
    channel_in: NotificationChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(NotificationChannel).filter(
        NotificationChannel.user_id == current_user.id,
        NotificationChannel.channel == channel_in.channel,
        NotificationChannel.destination == channel_in.destination
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Channel already exists.")

    new_channel = NotificationChannel(
        user_id=current_user.id,
        **channel_in.model_dump()
    )
    db.add(new_channel)
    db.commit()
    db.refresh(new_channel)
    return new_channel

@router.get("/channels", response_model=list[NotificationChannelResponse])
def list_notification_channels(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(NotificationChannel).filter(NotificationChannel.user_id == current_user.id).all()

@router.delete("/channels/{channel_id}")
def remove_notification_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    channel = db.query(NotificationChannel).filter(
        NotificationChannel.id == channel_id,
        NotificationChannel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found.")

    db.delete(channel)
    db.commit()
    return {"message": "Channel removed successfully."}

@router.put("/channels/{channel_id}", response_model=NotificationChannelResponse)
def update_notification_channel(
    channel_id: str,
    channel_update: NotificationChannelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    channel = db.query(NotificationChannel).filter(
        NotificationChannel.id == channel_id,
        NotificationChannel.user_id == current_user.id
    ).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found.")

    if channel_update.destination is not None:
        channel.destination = channel_update.destination
    if channel_update.is_active is not None:
        channel.is_active = channel_update.is_active

    db.commit()
    db.refresh(channel)
    return channel
