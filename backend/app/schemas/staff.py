from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class StaffShiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    clock_in: datetime
    clock_out: datetime | None
    created_at: datetime
    duration_seconds: int | None = None
    user: UserResponse | None = None


class StaffDutySummary(BaseModel):
    user_id: UUID
    discord_id: str
    username: str
    role: str
    total_shifts: int
    total_seconds: int
    is_clocked_in: bool


class ClockStatusResponse(BaseModel):
    clocked_in: bool
    shift: StaffShiftResponse | None = None
