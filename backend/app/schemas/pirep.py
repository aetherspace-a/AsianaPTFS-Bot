from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.pirep import PirepStatus
from app.schemas.flight import FlightResponse
from app.schemas.user import UserResponse


class PirepCreate(BaseModel):
    flight_id: UUID
    flight_time_hours: int = Field(ge=0, default=0)
    flight_time_minutes: int = Field(ge=0, le=59, default=0)
    landing_rate_fpm: int = Field(ge=0, description="Landing rate in feet per minute")
    fuel_used_lbs: int | None = Field(default=None, ge=0)
    notes: str | None = Field(default=None, max_length=2000)

    def total_minutes(self) -> int:
        return self.flight_time_hours * 60 + self.flight_time_minutes


class PirepReject(BaseModel):
    reason: str | None = Field(default=None, max_length=512)


class PirepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    flight_id: UUID
    flight_time_minutes: int
    landing_rate_fpm: int
    fuel_used_lbs: int | None
    notes: str | None
    status: PirepStatus
    won_bonus: int | None
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    rejection_reason: str | None
    created_at: datetime
    estimated_bonus: int | None = None


class PirepDetailResponse(PirepResponse):
    flight: FlightResponse | None = None
    user: UserResponse | None = None


class EligibleFlightOption(BaseModel):
    flight_id: UUID
    flight_number: str
    departure: str
    arrival: str
    booking_id: UUID
    seat_number: str
