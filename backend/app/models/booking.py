import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.flight import Flight
    from app.models.user import User


class SeatClass(str, enum.Enum):
    ECONOMY = "Economy"
    BUSINESS = "Business"
    FIRST = "First"


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        # Prevent double-booking the same seat on a flight
        UniqueConstraint("flight_id", "seat_number", name="uq_booking_flight_seat"),
    )

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
    seat_number: Mapped[str] = mapped_column(String(8), nullable=False)
    seat_class: Mapped[SeatClass] = mapped_column(
        Enum(SeatClass, name="seat_class", native_enum=False),
        nullable=False,
        default=SeatClass.ECONOMY,
    )
    price_won: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    booked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    boarding_pass_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="bookings")
    flight: Mapped["Flight"] = relationship("Flight", back_populates="bookings")
