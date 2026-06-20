from uuid import uuid4
from uuid import UUID as PyUUID
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.db.base import Base

class User(Base):

    __tablename__ = "users"

    id: Mapped[PyUUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash: Mapped[str] =mapped_column(
        String,
        nullable=False
    )

#relationships
    preference = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    ) 

    resumes = relationship(
        "Resume",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    reports = relationship(
        "DailyReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    notification_channels = relationship(
        "NotificationChannel",
        back_populates="user",
        cascade="all, delete-orphan"
    )