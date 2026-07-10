from datetime import datetime
from uuid import uuid4

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

class NotificationLog(Base):
    __tablename__ = "notifications_log"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    report_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("daily_reports.id", ondelete="CASCADE"),
        index=True
    )

    channel: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now()
    )

    report = relationship("DailyReport", backref="notification_logs")
