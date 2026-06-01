from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_users: int
    active_users_7d: int
    total_bookings: int
    total_revenue_won: int
    won_in_circulation: int
    flights_scheduled: int
    flights_active: int
