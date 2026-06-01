from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import decode_access_token, get_token_user_id
from app.db.session import get_db
from app.models.user import User, UserRole

security = HTTPBearer(auto_error=False)
settings = get_settings()


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> User:
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        user_id = get_token_user_id(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc

    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found")
    return user


async def require_staff(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role not in (UserRole.STAFF, UserRole.ADMIN):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Staff access required")
    return user


async def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin access required")
    return user


async def verify_bot_key(x_bot_key: Annotated[str | None, Header()] = None) -> None:
    if not x_bot_key or x_bot_key != settings.bot_api_key:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid bot API key")


async def get_or_create_user_by_discord(
    db: AsyncSession,
    discord_id: str,
    username: str,
) -> User:
    result = await db.execute(select(User).where(User.discord_id == discord_id))
    user = result.scalar_one_or_none()
    if user:
        if user.username != username:
            user.username = username
        return user
    user = User(discord_id=discord_id, username=username)
    db.add(user)
    await db.flush()
    return user
