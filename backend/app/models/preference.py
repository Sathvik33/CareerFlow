from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.db.base import Base
from app.models.mixins import TimestampMixin

class UserPreference(Base, TimestampMixin):
    __tablename__ = "user_preferences"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        unique=True,
        index=True
    )

    roles: Mapped[list] = mapped_column(JSONB)

    locations: Mapped[list] = mapped_column(JSONB)

    experience_level: Mapped[str]

    job_types: Mapped[list] = mapped_column(JSONB)

    work_modes: Mapped[list] = mapped_column(JSONB)

    preferred_skills: Mapped[list] = mapped_column(JSONB)

    salary_min: Mapped[int | None]

    salary_max: Mapped[int | None]

    user = relationship(
        "User",
        back_populates="preference"
    )