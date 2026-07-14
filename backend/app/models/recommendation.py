from uuid import uuid4

from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from app.db.base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    match_result_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("match_results.id", ondelete="CASCADE"),
        index=True
    )

    action_items: Mapped[list] = mapped_column(JSONB)
    projected_improvement_pct: Mapped[float] = mapped_column(Float)

    match_result = relationship("MatchResult", backref=backref("recommendations", cascade="all, delete-orphan", passive_deletes=True))
