from pydantic import BaseModel


class LeaderboardPilotHours(BaseModel):
    rank: int
    username: str
    discord_id: str
    pilot_rank: str
    total_hours: float
    total_flight_minutes: int


class LeaderboardPilotWealth(BaseModel):
    rank: int
    username: str
    discord_id: str
    won_balance: int
    pilot_rank: str


class LeaderboardResponse(BaseModel):
    top_pilots_by_hours: list[LeaderboardPilotHours]
    top_pilots_by_wealth: list[LeaderboardPilotWealth]
    cached_seconds: int
