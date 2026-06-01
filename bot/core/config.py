from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

MONOREPO_ROOT = Path(__file__).resolve().parents[2]


class BotSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    discord_bot_token: str = ""
    api_url: str = "http://localhost:8000"
    bot_api_key: str = "dev-bot-key-change-me"
    frontend_url: str = "http://localhost:3000"
    branding_path: Path = MONOREPO_ROOT / "branding.json"


@lru_cache
def get_settings() -> BotSettings:
    return BotSettings()
