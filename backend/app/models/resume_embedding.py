from uuid import uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ARRAY, Float

from app.db.base import Base

class ResumeEmbedding(Base):
    __tablename__ = "resume_embeddings"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    resume_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        index=True
    )

    embedding = mapped_column(ARRAY(Float))

    chunk_type: Mapped[str] = mapped_column(String)

    resume = relationship("Resume", backref="embeddings")
