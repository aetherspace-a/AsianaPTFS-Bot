from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DiscordOAuthCallback(BaseModel):
    code: str


class BotEconomyRequest(BaseModel):
    discord_id: str
    username: str | None = None


class BotWorkResponse(BaseModel):
    earned: int
    new_balance: int
    cooldown_seconds_remaining: int = 0


class BotGambleRequest(BaseModel):
    discord_id: str
    username: str | None = None
    bet: int
    choice: str = "heads"


class BotGambleResponse(BaseModel):
    won: bool
    payout: int
    new_balance: int
    result: str


class BotPayRequest(BaseModel):
    from_discord_id: str
    to_discord_id: str
    amount: int


class BotSyncRolesRequest(BaseModel):
    discord_id: str
    new_rank: str
    old_rank: str | None = None
