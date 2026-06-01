from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.staff_shift import StaffShift
from app.models.user import User, UserRole


class DutyError(Exception):
    def __init__(self, message: str, code: str = "duty_error"):
        self.message = message
        self.code = code
        super().__init__(message)


def _ensure_staff(user: User) -> None:
    if user.role not in (UserRole.STAFF, UserRole.ADMIN):
        raise DutyError("Only staff members can clock in/out", "not_staff")


async def get_open_shift(session: AsyncSession, user_id: UUID) -> StaffShift | None:
    result = await session.execute(
        select(StaffShift).where(
            StaffShift.user_id == user_id,
            StaffShift.clock_out.is_(None),
        )
    )
    return result.scalar_one_or_none()


async def clock_in(session: AsyncSession, user: User) -> StaffShift:
    _ensure_staff(user)
    open_shift = await get_open_shift(session, user.id)
    if open_shift:
        raise DutyError("You are already clocked in", "already_clocked_in")

    shift = StaffShift(
        user_id=user.id,
        clock_in=datetime.now(UTC),
    )
    session.add(shift)
    await session.flush()
    return shift


async def clock_out(session: AsyncSession, user: User) -> StaffShift:
    _ensure_staff(user)
    shift = await get_open_shift(session, user.id)
    if not shift:
        raise DutyError("You are not clocked in", "not_clocked_in")

    shift.clock_out = datetime.now(UTC)
    await session.flush()
    return shift


def shift_duration_seconds(shift: StaffShift) -> int | None:
    if not shift.clock_out:
        end = datetime.now(UTC)
    else:
        end = shift.clock_out
    return int((end - shift.clock_in).total_seconds())


async def list_shifts(
    session: AsyncSession,
    *,
    active_only: bool = False,
    limit: int = 100,
) -> list[StaffShift]:
    q = (
        select(StaffShift)
        .options(selectinload(StaffShift.user))
        .order_by(StaffShift.clock_in.desc())
        .limit(limit)
    )
    if active_only:
        q = q.where(StaffShift.clock_out.is_(None))
    result = await session.execute(q)
    return list(result.scalars().all())
