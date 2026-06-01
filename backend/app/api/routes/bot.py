from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_create_user_by_discord, verify_bot_key
from app.db.session import get_db
from app.models.user import User
from app.models.pilot_rank import PilotRank
from app.schemas.auth import (
    BotEconomyRequest,
    BotGambleRequest,
    BotGambleResponse,
    BotPayRequest,
    BotSyncRolesRequest,
    BotWorkResponse,
)
from app.services.discord_roles import sync_discord_rank_roles
from app.schemas.staff import ClockStatusResponse, StaffShiftResponse
from app.schemas.user import UserResponse
from app.services.duty import DutyError, clock_in, clock_out, get_open_shift
from app.services.economy import (
    EconomyError,
    get_last_work_time,
    get_user_by_discord_for_update,
    perform_coinflip,
    perform_work,
    transfer_won,
    work_cooldown_remaining,
)

router = APIRouter(prefix="/bot", tags=["bot"], dependencies=[Depends(verify_bot_key)])


@router.post("/users/ensure", response_model=UserResponse)
async def ensure_user(
    payload: BotEconomyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    username = payload.username or f"User_{payload.discord_id[-4:]}"
    user = await get_or_create_user_by_discord(db, payload.discord_id, username)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/users/{discord_id}/balance", response_model=UserResponse)
async def bot_get_balance(
    discord_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.post("/economy/work", response_model=BotWorkResponse)
async def bot_work(
    payload: BotEconomyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    username = payload.username or f"User_{payload.discord_id[-4:]}"
    user = await get_or_create_user_by_discord(db, payload.discord_id, username)
    last_work = await get_last_work_time(db, user.id)
    remaining = work_cooldown_remaining(last_work)
    if remaining > 0:
        return BotWorkResponse(
            earned=0,
            new_balance=user.won_balance,
            cooldown_seconds_remaining=remaining,
        )
    try:
        earned, balance = await perform_work(db, user.id)
        await db.commit()
    except EconomyError as exc:
        await db.rollback()
        if exc.code == "cooldown":
            last_work = await get_last_work_time(db, user.id)
            remaining = work_cooldown_remaining(last_work)
            return BotWorkResponse(
                earned=0,
                new_balance=user.won_balance,
                cooldown_seconds_remaining=remaining,
            )
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc
    return BotWorkResponse(earned=earned, new_balance=balance)


@router.post("/economy/coinflip", response_model=BotGambleResponse)
async def bot_coinflip(
    payload: BotGambleRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    username = payload.username or f"User_{payload.discord_id[-4:]}"
    user = await get_or_create_user_by_discord(db, payload.discord_id, username)
    try:
        won, balance, result, payout = await perform_coinflip(
            db, user.id, payload.bet, payload.choice
        )
        await db.commit()
    except EconomyError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc
    return BotGambleResponse(
        won=won,
        payout=payout,
        new_balance=balance,
        result=result,
    )


@router.post("/economy/pay", response_model=dict)
async def bot_pay(
    payload: BotPayRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if payload.from_discord_id == payload.to_discord_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot pay yourself")

    from_result = await db.execute(
        select(User).where(User.discord_id == payload.from_discord_id)
    )
    from_user = from_result.scalar_one_or_none()
    to_user = await get_or_create_user_by_discord(
        db,
        payload.to_discord_id,
        f"User_{payload.to_discord_id[-4:]}",
    )
    if not from_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Sender not found")

    try:
        sender, receiver = await transfer_won(
            db, from_user.id, to_user.id, payload.amount
        )
        await db.commit()
    except EconomyError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc

    return {
        "from_balance": sender.won_balance,
        "to_balance": receiver.won_balance,
        "amount": payload.amount,
    }


def _shift_api_response(shift) -> StaffShiftResponse:
    from app.services.duty import shift_duration_seconds

    return StaffShiftResponse(
        id=shift.id,
        user_id=shift.user_id,
        clock_in=shift.clock_in,
        clock_out=shift.clock_out,
        created_at=shift.created_at,
        duration_seconds=shift_duration_seconds(shift),
    )


@router.post("/duty/clockin", response_model=StaffShiftResponse)
async def bot_clock_in(
    payload: BotEconomyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    username = payload.username or f"User_{payload.discord_id[-4:]}"
    user = await get_or_create_user_by_discord(db, payload.discord_id, username)
    try:
        shift = await clock_in(db, user)
        await db.commit()
        await db.refresh(shift)
    except DutyError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc
    return _shift_api_response(shift)


@router.post("/duty/clockout", response_model=StaffShiftResponse)
async def bot_clock_out(
    payload: BotEconomyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.discord_id == payload.discord_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    try:
        shift = await clock_out(db, user)
        await db.commit()
        await db.refresh(shift)
    except DutyError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc
    return _shift_api_response(shift)


@router.get("/duty/{discord_id}/status", response_model=ClockStatusResponse)
async def bot_duty_status(
    discord_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if not user:
        return ClockStatusResponse(clocked_in=False, shift=None)
    shift = await get_open_shift(db, user.id)
    if not shift:
        return ClockStatusResponse(clocked_in=False, shift=None)
    return ClockStatusResponse(clocked_in=True, shift=_shift_api_response(shift))


@router.post("/sync-roles")
async def bot_sync_roles(payload: BotSyncRolesRequest):
    """Assign Discord rank roles after promotion (also called internally on PIREP approve)."""
    old = PilotRank(payload.old_rank) if payload.old_rank else PilotRank.TRAINEE
    new = PilotRank(payload.new_rank)
    await sync_discord_rank_roles(payload.discord_id, old, new)
    return {"status": "ok", "discord_id": payload.discord_id, "new_rank": new.value}
