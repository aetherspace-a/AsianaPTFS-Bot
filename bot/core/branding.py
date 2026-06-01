import json
from functools import lru_cache
from pathlib import Path

from bot.core.config import get_settings


@lru_cache
def load_branding() -> dict:
    settings = get_settings()
    with settings.branding_path.open(encoding="utf-8") as f:
        return json.load(f)


def embed_color() -> int:
    branding = load_branding()
    hex_color = branding.get("discord", {}).get(
        "embed_color_hex",
        branding.get("colors", {}).get("primary", "#E31E24"),
    )
    return int(hex_color.lstrip("#"), 16)


def embed_footer() -> str:
    branding = load_branding()
    return branding.get("discord", {}).get(
        "embed_footer_text",
        f"{branding.get('airline_name', 'VA')} Virtual Airline",
    )
