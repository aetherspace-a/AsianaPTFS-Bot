from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin, require_staff
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User, UserRole
from app.schemas.staff import StaffDutySummary, StaffShiftResponse
from app.schemas.transaction import TransactionResponse
from app.schemas.user import UserResponse
from app.services.duty import list_shifts, shift_duration_seconds

router = APIRouter(prefix="/admin", tags=["admin"])


def _shift_response(shift) -> StaffShiftResponse:
    return StaffShiftResponse(
        id=shift.id,
        user_id=shift.user_id,
        clock_in=shift.clock_in,
        clock_out=shift.clock_out,
        created_at=shift.created_at,
        duration_seconds=shift_duration_seconds(shift),
        user=shift.user if hasattr(shift, "user") and shift.user else None,
    )


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
    search: str | None = Query(None, description="Filter by username or discord_id"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    q = select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)
    if search:
        pattern = f"%{search}%"
        q = q.where(
            (User.username.ilike(pattern)) | (User.discord_id.ilike(pattern))
        )
    result = await db.execute(q)
    return list(result.scalars().all())


@router.get("/users/{discord_id}/transactions", response_model=list[TransactionResponse])
async def user_transactions(
    discord_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
    limit: int = Query(50, ge=1, le=200),
):
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    tx_result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == user.id)
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
    )
    return list(tx_result.scalars().all())


@router.patch("/users/{discord_id}/role", response_model=UserResponse)
async def set_user_role(
    discord_id: str,
    role: UserRole = Query(...),
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.role = role
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/staff/shifts", response_model=list[StaffShiftResponse])
async def staff_shifts(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
    active_only: bool = False,
    limit: int = Query(100, ge=1, le=500),
):
    shifts = await list_shifts(db, active_only=active_only, limit=limit)
    return [_shift_response(s) for s in shifts]


@router.get("/staff/summary", response_model=list[StaffDutySummary])
async def staff_duty_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
):
    shifts = await list_shifts(db, active_only=False, limit=500)
    by_user: dict = {}
    for shift in shifts:
        uid = shift.user_id
        if uid not in by_user:
            u = shift.user
            by_user[uid] = {
                "user_id": uid,
                "discord_id": u.discord_id if u else "",
                "username": u.username if u else "Unknown",
                "role": u.role.value if u else "User",
                "total_shifts": 0,
                "total_seconds": 0,
                "is_clocked_in": False,
            }
        dur = shift_duration_seconds(shift) or 0
        by_user[uid]["total_shifts"] += 1
        if shift.clock_out:
            by_user[uid]["total_seconds"] += dur
        else:
            by_user[uid]["is_clocked_in"] = True
            by_user[uid]["total_seconds"] += dur

    return [StaffDutySummary(**v) for v in by_user.values()]
