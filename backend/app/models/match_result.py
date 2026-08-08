from datetime import datetime
from uuid import uuid4

from sqlalchemy import Float, ForeignKey, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base

MATCH_STATUSES = (
    "matched",
    "saved",
    "applied",
    "interview",
    "offer",
    "rejected",
    "dismissed",
)

ACTIVE_PIPELINE = ("saved", "applied", "interview", "offer", "rejected")


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )

    job_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        index=True
    )

    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        index=True
    )

    semantic_score: Mapped[float] = mapped_column(Float)
    bm25_score: Mapped[float] = mapped_column(Float)
    final_score: Mapped[float] = mapped_column(Float)

    missing_skills: Mapped[list] = mapped_column(JSONB)
    strengths: Mapped[list] = mapped_column(JSONB)

    status: Mapped[str] = mapped_column(
        String(32),
        default="matched",
        server_default="matched",
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )

    user = relationship("User", backref="match_results")
    job = relationship("Job", backref="match_results")
    resume = relationship("Resume", backref="match_results")
