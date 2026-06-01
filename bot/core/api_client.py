from typing import Any

import httpx

from bot.core.config import get_settings

settings = get_settings()


class ApiClient:
    def __init__(self) -> None:
        self.base = settings.api_url.rstrip("/")
        self.headers = {"X-Bot-Key": settings.bot_api_key, "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        async with httpx.AsyncClient() as client:
            res = await client.request(
                method,
                f"{self.base}{path}",
                headers=self.headers,
                timeout=30.0,
                **kwargs,
            )
            if res.status_code >= 400:
                detail = res.json().get("detail", res.text) if res.content else res.text
                raise RuntimeError(str(detail))
            if res.status_code == 204:
                return None
            return res.json()

    async def ensure_user(self, discord_id: str, username: str) -> dict:
        return await self._request(
            "POST",
            "/api/bot/users/ensure",
            json={"discord_id": discord_id, "username": username},
        )

    async def get_balance(self, discord_id: str) -> dict:
        return await self._request("GET", f"/api/bot/users/{discord_id}/balance")

    async def work(self, discord_id: str, username: str) -> dict:
        return await self._request(
            "POST",
            "/api/bot/economy/work",
            json={"discord_id": discord_id, "username": username},
        )

    async def coinflip(self, discord_id: str, username: str, bet: int, choice: str) -> dict:
        return await self._request(
            "POST",
            "/api/bot/economy/coinflip",
            json={
                "discord_id": discord_id,
                "username": username,
                "bet": bet,
                "choice": choice,
            },
        )

    async def pay(self, from_id: str, to_id: str, amount: int) -> dict:
        return await self._request(
            "POST",
            "/api/bot/economy/pay",
            json={
                "from_discord_id": from_id,
                "to_discord_id": to_id,
                "amount": amount,
            },
        )

    async def clock_in(self, discord_id: str, username: str) -> dict:
        return await self._request(
            "POST",
            "/api/bot/duty/clockin",
            json={"discord_id": discord_id, "username": username},
        )

    async def clock_out(self, discord_id: str, username: str) -> dict:
        return await self._request(
            "POST",
            "/api/bot/duty/clockout",
            json={"discord_id": discord_id, "username": username},
        )

    async def list_flights(self) -> list[dict]:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base}/api/flights", timeout=30.0)
            res.raise_for_status()
            return res.json()
