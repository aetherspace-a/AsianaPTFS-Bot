from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_staff
from app.db.session import get_db
from app.models.booking import Booking
from app.models.flight import Flight, FlightStatus
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.schemas.analytics import AnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def analytics_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
):
    total_users = await db.scalar(select(func.count()).select_from(User)) or 0

    week_ago = datetime.now(UTC) - timedelta(days=7)
    active_users = await db.scalar(
        select(func.count(func.distinct(Transaction.user_id))).where(
            Transaction.timestamp >= week_ago
        )
    ) or 0

    total_bookings = await db.scalar(select(func.count()).select_from(Booking)) or 0

    revenue = await db.scalar(
        select(func.coalesce(func.sum(Booking.price_won), 0))
    ) or 0

    won_circulation = await db.scalar(
        select(func.coalesce(func.sum(User.won_balance), 0))
    ) or 0

    flights_scheduled = await db.scalar(
        select(func.count())
        .select_from(Flight)
        .where(Flight.status == FlightStatus.SCHEDULED)
    ) or 0

    flights_active = await db.scalar(
        select(func.count())
        .select_from(Flight)
        .where(Flight.status.in_([FlightStatus.BOARDING, FlightStatus.IN_AIR]))
    ) or 0

    return AnalyticsSummary(
        total_users=total_users,
        active_users_7d=active_users,
        total_bookings=total_bookings,
        total_revenue_won=int(revenue),
        won_in_circulation=int(won_circulation),
        flights_scheduled=flights_scheduled,
        flights_active=flights_active,
    )
