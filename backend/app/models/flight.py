import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.pirep import Pirep


class FlightStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    BOARDING = "Boarding"
    IN_AIR = "In-Air"
    LANDED = "Landed"


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    flight_number: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    departure: Mapped[str] = mapped_column(String(8), nullable=False)
    arrival: Mapped[str] = mapped_column(String(8), nullable=False)
    aircraft: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[FlightStatus] = mapped_column(
        Enum(FlightStatus, name="flight_status", native_enum=False),
        nullable=False,
        default=FlightStatus.SCHEDULED,
        server_default=FlightStatus.SCHEDULED.value,
        index=True,
    )
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="flight",
        cascade="all, delete-orphan",
    )
    pireps: Mapped[list["Pirep"]] = relationship(
        "Pirep",
        back_populates="flight",
        cascade="all, delete-orphan",
    )
