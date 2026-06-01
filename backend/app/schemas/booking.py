from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import SeatClass
from app.schemas.flight import FlightResponse
from app.schemas.user import UserResponse


class BookingCreate(BaseModel):
    flight_id: UUID
    seat_number: str = Field(max_length=8)
    seat_class: SeatClass = SeatClass.ECONOMY


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    flight_id: UUID
    seat_number: str
    seat_class: SeatClass
    price_won: int
    booked_at: datetime
    boarding_pass_path: str | None = None
    has_boarding_pass: bool = False


class BookingDetailResponse(BookingResponse):
    flight: FlightResponse | None = None
    user: UserResponse | None = None


class SeatMapSeat(BaseModel):
    seat_number: str
    seat_class: SeatClass | None = None
    available: bool
    booked_by: UUID | None = None


class SeatMapResponse(BaseModel):
    flight_id: UUID
    rows: int
    seats_per_row: int
    seats: list[SeatMapSeat]
