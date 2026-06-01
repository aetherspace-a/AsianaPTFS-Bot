import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import get_settings


class BrandingColors(BaseModel):
    primary: str
    secondary: str
    accent: str
    background: str = "#0F0F14"
    surface: str = "#1E1E2A"
    text: str = "#F5F5F7"
    text_muted: str = "#9CA3AF"
    success: str = "#22C55E"
    warning: str = "#F59E0B"
    error: str = "#EF4444"


class BrandingLogos(BaseModel):
    main: str
    icon: str
    banner: str
    discord_thumbnail: str = ""


class BrandingSocialLinks(BaseModel):
    discord: str = ""
    website: str = ""
    roblox_group: str = ""
    instagram: str = ""
    youtube: str = ""


class BrandingConfig(BaseModel):
    airline_name: str
    airline_icao: str
    airline_iata: str = ""
    tagline: str = ""
    colors: BrandingColors
    logos: BrandingLogos
    social_links: BrandingSocialLinks
    discord: dict[str, Any] = Field(default_factory=dict)
    economy: dict[str, Any] = Field(default_factory=dict)
    flights: dict[str, Any] = Field(default_factory=dict)
    pilot_ranks: list[dict[str, Any]] = Field(default_factory=list)
    pirep: dict[str, Any] = Field(default_factory=dict)


@lru_cache
def load_branding(path: Path | None = None) -> BrandingConfig:
    settings = get_settings()
    branding_path = path or settings.branding_path
    with branding_path.open(encoding="utf-8") as f:
        data = json.load(f)
    return BrandingConfig.model_validate(data)
