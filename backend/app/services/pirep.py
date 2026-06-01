from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.branding import load_branding
from app.models.booking import Booking
from app.models.pilot_rank import PilotRank
from app.models.pirep import Pirep, PirepStatus
from app.models.transaction import TransactionType
from app.models.user import User
from app.services.discord_roles import sync_discord_rank_roles
from app.services.economy import EconomyError, get_user_for_update, record_transaction
from app.services.leaderboard import invalidate_leaderboard_cache
from app.services.ranks import rank_for_minutes


class PirepError(Exception):
    def __init__(self, message: str, code: str = "pirep_error"):
        self.message = message
        self.code = code
        super().__init__(message)


def landing_multiplier(fpm: int) -> float:
    branding = load_branding()
    pirep_cfg = branding.pirep or {}
    tiers = pirep_cfg.get(
        "landing_multipliers",
        [
            {"max_fpm": 200, "multiplier": 1.25},
            {"max_fpm": 400, "multiplier": 1.0},
            {"max_fpm": 600, "multiplier": 0.75},
            {"max_fpm": 9999, "multiplier": 0.5},
        ],
    )
    for tier in sorted(tiers, key=lambda t: t["max_fpm"]):
        if fpm <= tier["max_fpm"]:
            return float(tier["multiplier"])
    return 0.5


def calculate_won_bonus(flight_time_minutes: int, landing_rate_fpm: int) -> int:
    branding = load_branding()
    won_per_hour = int((branding.pirep or {}).get("won_per_hour", 600))
    hours = flight_time_minutes / 60
    base = hours * won_per_hour
    return max(1, int(base * landing_multiplier(landing_rate_fpm)))


async def submit_pirep(
    session: AsyncSession,
    user: User,
    flight_id: UUID,
    flight_time_minutes: int,
    landing_rate_fpm: int,
    fuel_used_lbs: int | None,
    notes: str | None,
) -> Pirep:
    if flight_time_minutes < 1:
        raise PirepError("Flight time must be at least 1 minute")
    if landing_rate_fpm < 0:
        raise PirepError("Landing rate must be a positive fpm value")

    booking = await session.execute(
        select(Booking).where(
            Booking.user_id == user.id,
            Booking.flight_id == flight_id,
        )
    )
    if not booking.scalar_one_or_none():
        raise PirepError("You must book this flight before filing a PIREP", "no_booking")

    existing = await session.execute(
        select(Pirep).where(
            Pirep.user_id == user.id,
            Pirep.flight_id == flight_id,
            Pirep.status.in_([PirepStatus.PENDING, PirepStatus.APPROVED]),
        )
    )
    if existing.scalar_one_or_none():
        raise PirepError("A PIREP already exists for this flight", "duplicate")

    pirep = Pirep(
        user_id=user.id,
        flight_id=flight_id,
        flight_time_minutes=flight_time_minutes,
        landing_rate_fpm=landing_rate_fpm,
        fuel_used_lbs=fuel_used_lbs,
        notes=notes,
        status=PirepStatus.PENDING,
    )
    session.add(pirep)
    await session.flush()
    return pirep


async def approve_pirep(
    session: AsyncSession,
    pirep_id: UUID,
    reviewer: User,
) -> Pirep:
    result = await session.execute(
        select(Pirep)
        .where(Pirep.id == pirep_id)
        .options(selectinload(Pirep.user), selectinload(Pirep.flight))
    )
    pirep = result.scalar_one_or_none()
    if not pirep:
        raise PirepError("PIREP not found", "not_found")
    if pirep.status != PirepStatus.PENDING:
        raise PirepError("PIREP is not pending", "invalid_status")

    bonus = calculate_won_bonus(pirep.flight_time_minutes, pirep.landing_rate_fpm)
    pilot = await get_user_for_update(session, pirep.user_id)
    old_rank = pilot.pilot_rank

    pilot.total_flight_minutes += pirep.flight_time_minutes
    new_rank = rank_for_minutes(pilot.total_flight_minutes)
    pilot.pilot_rank = new_rank

    await record_transaction(session, pilot, bonus, TransactionType.PIREP, reference_id=pirep.id)

    if new_rank != old_rank:
        await record_transaction(
            session,
            pilot,
            0,
            TransactionType.RANK_PROMOTION,
            reference_id=pirep.id,
        )

    pirep.status = PirepStatus.APPROVED
    pirep.won_bonus = bonus
    pirep.reviewed_by = reviewer.id
    pirep.reviewed_at = datetime.now(UTC)

    await session.flush()

    if new_rank != old_rank:
        await sync_discord_rank_roles(pilot.discord_id, old_rank, new_rank)

    invalidate_leaderboard_cache()
    return pirep


async def reject_pirep(
    session: AsyncSession,
    pirep_id: UUID,
    reviewer: User,
    reason: str | None,
) -> Pirep:
    result = await session.execute(select(Pirep).where(Pirep.id == pirep_id))
    pirep = result.scalar_one_or_none()
    if not pirep:
        raise PirepError("PIREP not found", "not_found")
    if pirep.status != PirepStatus.PENDING:
        raise PirepError("PIREP is not pending", "invalid_status")

    pirep.status = PirepStatus.REJECTED
    pirep.reviewed_by = reviewer.id
    pirep.reviewed_at = datetime.now(UTC)
    pirep.rejection_reason = reason
    await session.flush()
    return pirep
