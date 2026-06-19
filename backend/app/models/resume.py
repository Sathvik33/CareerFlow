from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.mixins import TimestampMixin

class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(100)
    )

    file_url: Mapped[str] = mapped_column(
        String
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    user = relationship(
        "User",
        back_populates="resumes"
    )