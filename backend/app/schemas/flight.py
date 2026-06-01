from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.flight import FlightStatus


class FlightBase(BaseModel):
    flight_number: str = Field(max_length=16)
    departure: str = Field(max_length=8)
    arrival: str = Field(max_length=8)
    aircraft: str | None = Field(default=None, max_length=32)
    departure_time: datetime
    status: FlightStatus = FlightStatus.SCHEDULED


class FlightCreate(FlightBase):
    pass


class FlightUpdate(BaseModel):
    flight_number: str | None = None
    departure: str | None = None
    arrival: str | None = None
    aircraft: str | None = None
    departure_time: datetime | None = None
    status: FlightStatus | None = None


class FlightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    flight_number: str
    departure: str
    arrival: str
    aircraft: str | None
    status: FlightStatus
    departure_time: datetime
    created_at: datetime
    updated_at: datetime
