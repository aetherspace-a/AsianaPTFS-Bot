import logging
from datetime import UTC, datetime

import httpx

from app.core.branding import load_branding
from app.core.config import get_settings
from app.models.flight import Flight, FlightStatus

logger = logging.getLogger(__name__)
settings = get_settings()

STATUS_MESSAGES: dict[FlightStatus, str] = {
    FlightStatus.SCHEDULED: "has been scheduled",
    FlightStatus.BOARDING: "is now **boarding** — please proceed to your gate",
    FlightStatus.IN_AIR: "has departed and is **in the air**",
    FlightStatus.LANDED: "has **landed** at its destination",
}


def _hex_to_int(hex_color: str) -> int:
    return int(hex_color.lstrip("#"), 16)


async def notify_flight_status_change(
    flight: Flight,
    previous_status: FlightStatus,
    new_status: FlightStatus,
    *,
    updated_by: str | None = None,
) -> None:
    if not settings.discord_webhook_url:
        logger.debug("Discord webhook URL not configured; skipping notification")
        return
    if previous_status == new_status:
        return

    branding = load_branding()
    color_hex = branding.discord.get("embed_color_hex", branding.colors.primary)
    footer = branding.discord.get("embed_footer_text", branding.airline_name)
    airline = branding.airline_name

    dep_time = flight.departure_time
    if isinstance(dep_time, datetime):
        dep_str = dep_time.strftime("%Y-%m-%d %H:%M UTC")
    else:
        dep_str = str(dep_time)

    status_line = STATUS_MESSAGES.get(new_status, f"status is now **{new_status.value}**")
    description = (
        f"**{airline}** flight **{flight.flight_number}** {status_line}.\n\n"
        f"**Route:** {flight.departure} → {flight.arrival}\n"
        f"**Departure:** {dep_str}\n"
    )
    if flight.aircraft:
        description += f"**Aircraft:** {flight.aircraft}\n"
    description += f"\n_{previous_status.value} → {new_status.value}_"
    if updated_by:
        description += f"\n\nUpdated by **{updated_by}**"

    embed = {
        "title": f"✈️ Flight Update — {flight.flight_number}",
        "description": description,
        "color": _hex_to_int(color_hex),
        "footer": {"text": footer},
        "timestamp": datetime.now(UTC).isoformat(),
    }

    payload = {
        "username": f"{airline} Flight Updates",
        "embeds": [embed],
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(
                settings.discord_webhook_url,
                json=payload,
                timeout=10.0,
            )
            res.raise_for_status()
    except Exception as exc:
        logger.warning("Failed to send Discord webhook: %s", exc)
