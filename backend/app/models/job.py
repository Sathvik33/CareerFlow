from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, Text, UniqueConstraint, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    source: Mapped[str] = mapped_column(String)
    external_id: Mapped[str] = mapped_column(String)
    company: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    location: Mapped[str] = mapped_column(String, nullable=True)
    remote: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str] = mapped_column(Text)
    salary: Mapped[str] = mapped_column(String, nullable=True)
    employment_type: Mapped[str] = mapped_column(String, nullable=True)
    experience_level: Mapped[str] = mapped_column(String, nullable=True)
    skills: Mapped[list[str]] = mapped_column(JSONB, nullable=True)
    apply_url: Mapped[str] = mapped_column(String)
    company_logo: Mapped[str] = mapped_column(String, nullable=True)
    posted_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now()
    )
    structured_json: Mapped[dict] = mapped_column(JSONB, nullable=True)

    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_job_source_external_id"),
    )
