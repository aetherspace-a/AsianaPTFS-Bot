import logging

import httpx

from app.core.branding import load_branding
from app.core.config import get_settings
from app.models.pilot_rank import PilotRank

logger = logging.getLogger(__name__)
DISCORD_API = "https://discord.com/api/v10"


def _rank_role_map() -> dict[str, str]:
    branding = load_branding()
    discord_cfg = branding.discord or branding.model_dump().get("discord", {})
    roles = discord_cfg.get("rank_role_ids", {})
    settings = get_settings()
    # Env overrides: DISCORD_ROLE_TRAINEE, etc.
    env_map = {
        "Trainee": settings.discord_role_trainee,
        "First Officer": settings.discord_role_first_officer,
        "Captain": settings.discord_role_captain,
        "Senior Captain": settings.discord_role_senior_captain,
    }
    merged = dict(roles)
    for name, role_id in env_map.items():
        if role_id:
            merged[name] = role_id
    return merged


def _guild_id() -> str:
    settings = get_settings()
    if settings.discord_guild_id:
        return settings.discord_guild_id
    branding = load_branding()
    discord_cfg = branding.discord or branding.model_dump().get("discord", {})
    return str(discord_cfg.get("guild_id", ""))


async def sync_discord_rank_roles(
    discord_user_id: str,
    old_rank: PilotRank,
    new_rank: PilotRank,
) -> None:
    settings = get_settings()
    if not settings.discord_bot_token:
        logger.debug("Discord bot token not set; skipping role sync")
        return

    guild_id = _guild_id()
    if not guild_id:
        logger.debug("Discord guild ID not set; skipping role sync")
        return

    role_map = _rank_role_map()
    headers = {"Authorization": f"Bot {settings.discord_bot_token}"}
    member_url = f"{DISCORD_API}/guilds/{guild_id}/members/{discord_user_id}"

    async with httpx.AsyncClient() as client:
        member_res = await client.get(member_url, headers=headers, timeout=15.0)
        if member_res.status_code == 404:
            logger.warning("Discord member %s not found in guild", discord_user_id)
            return
        member_res.raise_for_status()
        current_roles = set(member_res.json().get("roles", []))

        old_role_id = role_map.get(old_rank.value)
        new_role_id = role_map.get(new_rank.value)

        if old_role_id and old_role_id in current_roles:
            current_roles.discard(old_role_id)
        if new_role_id:
            current_roles.add(new_role_id)

        patch_res = await client.patch(
            member_url,
            headers={**headers, "Content-Type": "application/json"},
            json={"roles": list(current_roles)},
            timeout=15.0,
        )
        if patch_res.status_code >= 400:
            logger.warning(
                "Discord role sync failed for %s: %s",
                discord_user_id,
                patch_res.text,
            )
        else:
            logger.info(
                "Synced Discord roles for %s: %s -> %s",
                discord_user_id,
                old_rank.value,
                new_rank.value,
            )
