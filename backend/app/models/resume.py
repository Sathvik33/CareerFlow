from uuid import uuid4

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

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

    raw_text: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    structured_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="resumes"
    )