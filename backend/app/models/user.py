import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.pilot_rank import PilotRank

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.pilot_rank import PilotRank
    from app.models.pirep import Pirep
    from app.models.staff_shift import StaffShift
    from app.models.transaction import Transaction


class UserRole(str, enum.Enum):
    USER = "User"
    STAFF = "Staff"
    ADMIN = "Admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    discord_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    won_balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False),
        nullable=False,
        default=UserRole.USER,
        server_default=UserRole.USER.value,
    )
    total_flight_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    pilot_rank: Mapped[PilotRank] = mapped_column(
        Enum(PilotRank, name="pilot_rank", native_enum=False),
        nullable=False,
        default=PilotRank.TRAINEE,
        server_default=PilotRank.TRAINEE.value,
    )
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
        back_populates="user",
        cascade="all, delete-orphan",
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    staff_shifts: Mapped[list["StaffShift"]] = relationship(
        "StaffShift",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    pireps: Mapped[list["Pirep"]] = relationship(
        "Pirep",
        back_populates="user",
        foreign_keys="Pirep.user_id",
        cascade="all, delete-orphan",
    )
