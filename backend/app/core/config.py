from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Monorepo root (parent of backend/)
MONOREPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Asiana PTFS VA API"
    debug: bool = False

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/asiana_va"
    )

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7

    discord_client_id: str = ""
    discord_client_secret: str = ""
    discord_redirect_uri: str = "http://localhost:8000/api/auth/discord/callback"
    discord_bot_token: str = ""
    discord_guild_id: str = ""
    discord_role_trainee: str = ""
    discord_role_first_officer: str = ""
    discord_role_captain: str = ""
    discord_role_senior_captain: str = ""

    bot_api_key: str = "dev-bot-key-change-me"
    frontend_url: str = "http://localhost:3000"
    api_base_url: str = "http://localhost:8000"

    branding_path: Path = MONOREPO_ROOT / "branding.json"
    assets_path: Path = MONOREPO_ROOT / "assets"
    boarding_passes_path: Path = MONOREPO_ROOT / "storage" / "boarding_passes"
    discord_webhook_url: str = ""
    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
