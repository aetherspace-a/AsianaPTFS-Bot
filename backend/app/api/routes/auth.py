from typing import Annotated
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_or_create_user_by_discord
from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import get_db
from app.schemas.auth import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

DISCORD_API = "https://discord.com/api/v10"
DISCORD_OAUTH_AUTHORIZE = "https://discord.com/api/oauth2/authorize"


@router.get("/discord")
async def discord_login():
    params = {
        "client_id": settings.discord_client_id,
        "redirect_uri": settings.discord_redirect_uri,
        "response_type": "code",
        "scope": "identify",
    }
    if not settings.discord_client_id:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Discord OAuth not configured",
        )
    return RedirectResponse(f"{DISCORD_OAUTH_AUTHORIZE}?{urlencode(params)}")


@router.get("/discord/callback", response_model=TokenResponse)
async def discord_callback(
    code: str = Query(...),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    if not settings.discord_client_id or not settings.discord_client_secret:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Discord OAuth not configured",
        )

    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            f"{DISCORD_API}/oauth2/token",
            data={
                "client_id": settings.discord_client_id,
                "client_secret": settings.discord_client_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.discord_redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_res.status_code != 200:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "OAuth token exchange failed")
        access = token_res.json().get("access_token")

        user_res = await client.get(
            f"{DISCORD_API}/users/@me",
            headers={"Authorization": f"Bearer {access}"},
        )
        if user_res.status_code != 200:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Failed to fetch Discord user")

    discord_user = user_res.json()
    discord_id = discord_user["id"]
    username = discord_user.get("global_name") or discord_user.get("username", "Pilot")

    user = await get_or_create_user_by_discord(db, discord_id, username)
    await db.commit()

    jwt_token = create_access_token(
        subject=discord_id,
        extra={"user_id": str(user.id), "role": user.role.value},
    )
    redirect_url = f"{settings.frontend_url}/auth/callback?token={jwt_token}"
    return RedirectResponse(redirect_url)


