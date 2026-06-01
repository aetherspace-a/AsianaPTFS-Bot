from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.leaderboard import LeaderboardResponse
from app.services.leaderboard import get_leaderboard

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=LeaderboardResponse)
async def leaderboard(db: Annotated[AsyncSession, Depends(get_db)]):
    data = await get_leaderboard(db)
    return LeaderboardResponse(**data)
