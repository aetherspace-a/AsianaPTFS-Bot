import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.flight import Flight
    from app.models.user import User


class PirepStatus(str, enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class Pirep(Base):
    __tablename__ = "pireps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    flight_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flights.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    flight_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    landing_rate_fpm: Mapped[int] = mapped_column(Integer, nullable=False)
    fuel_used_lbs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PirepStatus] = mapped_column(
        Enum(PirepStatus, name="pirep_status", native_enum=False),
        nullable=False,
        default=PirepStatus.PENDING,
        server_default=PirepStatus.PENDING.value,
        index=True,
    )
    won_bonus: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="pireps", foreign_keys=[user_id])
    flight: Mapped["Flight"] = relationship("Flight", back_populates="pireps")
    reviewer: Mapped["User | None"] = relationship("User", foreign_keys=[reviewed_by])
