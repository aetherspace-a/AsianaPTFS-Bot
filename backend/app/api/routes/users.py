from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_staff
from app.db.session import get_db
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.user import UserBalanceAdjust, UserResponse, UserUpdate
from app.services.economy import EconomyError, adjust_balance

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.get("/{discord_id}", response_model=UserResponse)
async def get_user_by_discord(
    discord_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
):
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.patch("/{discord_id}", response_model=UserResponse)
async def update_user(
    discord_id: str,
    payload: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current: Annotated[User, Depends(get_current_user)],
):
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    is_self = user.discord_id == current.discord_id
    is_staff = current.role.value in ("Staff", "Admin")

    if not is_self and not is_staff:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Cannot update other users")

    if payload.username is not None:
        user.username = payload.username
    if payload.role is not None:
        if current.role.value != "Admin":
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Only admins can change roles")
        user.role = payload.role
    if payload.won_balance is not None and is_staff:
        user.won_balance = payload.won_balance

    await db.commit()
    await db.refresh(user)
    return user


@router.post("/{discord_id}/balance", response_model=UserResponse)
async def admin_adjust_balance(
    discord_id: str,
    payload: UserBalanceAdjust,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_staff)],
):
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    try:
        user = await adjust_balance(
            db, user.id, payload.amount, TransactionType.ADMIN
        )
        await db.commit()
        await db.refresh(user)
    except EconomyError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, exc.message) from exc
    return user
