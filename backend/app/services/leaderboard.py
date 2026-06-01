import time
from typing import Any

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.ranks import hours_from_minutes

_CACHE_TTL_SECONDS = 60
_cache: dict[str, Any] = {"expires_at": 0.0, "payload": None}


def invalidate_leaderboard_cache() -> None:
    _cache["expires_at"] = 0.0
    _cache["payload"] = None


async def get_leaderboard(session: AsyncSession) -> dict:
    now = time.time()
    if _cache["payload"] is not None and now < _cache["expires_at"]:
        return _cache["payload"]

    hours_result = await session.execute(
        select(User)
        .order_by(desc(User.total_flight_minutes))
        .limit(25)
    )
    wealth_result = await session.execute(
        select(User).order_by(desc(User.won_balance)).limit(25)
    )

    top_hours = [
        {
            "rank": i + 1,
            "username": u.username,
            "discord_id": u.discord_id,
            "pilot_rank": u.pilot_rank.value,
            "total_hours": hours_from_minutes(u.total_flight_minutes),
            "total_flight_minutes": u.total_flight_minutes,
        }
        for i, u in enumerate(hours_result.scalars().all())
    ]
    top_wealth = [
        {
            "rank": i + 1,
            "username": u.username,
            "discord_id": u.discord_id,
            "won_balance": u.won_balance,
            "pilot_rank": u.pilot_rank.value,
        }
        for i, u in enumerate(wealth_result.scalars().all())
    ]

    payload = {
        "top_pilots_by_hours": top_hours,
        "top_pilots_by_wealth": top_wealth,
        "cached_seconds": _CACHE_TTL_SECONDS,
    }
    _cache["payload"] = payload
    _cache["expires_at"] = now + _CACHE_TTL_SECONDS
    return payload
