from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.pilot_rank import PilotRank
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=128)


class UserCreate(UserBase):
    discord_id: str


class UserUpdate(BaseModel):
    username: str | None = None
    won_balance: int | None = None
    role: UserRole | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    discord_id: str
    username: str
    won_balance: int
    role: UserRole
    total_flight_minutes: int = 0
    pilot_rank: PilotRank = PilotRank.TRAINEE
    total_flight_hours: float = 0.0
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def compute_flight_hours(self) -> "UserResponse":
        self.total_flight_hours = round(self.total_flight_minutes / 60, 2)
        return self


class UserBalanceAdjust(BaseModel):
    amount: int = Field(description="Positive to credit, negative to debit")
    reason: str = "Admin adjustment"
