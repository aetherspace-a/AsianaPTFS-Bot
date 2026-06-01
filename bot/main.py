import asyncio
import logging
import sys
from pathlib import Path

# Allow `python bot/main.py` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import discord
from discord.ext import commands

from bot.core.config import get_settings
from bot.cogs import duty, economy, flights, moderation, voice

logging.basicConfig(level=logging.INFO)
settings = get_settings()


class AsianaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await economy.setup(self)
        await flights.setup(self)
        await duty.setup(self)
        await moderation.setup(self)
        await voice.setup(self)
        await self.tree.sync()
        logging.info("Slash commands synced")

    async def on_ready(self):
        logging.info("Logged in as %s (%s)", self.user, self.user.id if self.user else "?")


async def main():
    if not settings.discord_bot_token:
        raise SystemExit("DISCORD_BOT_TOKEN is required")
    bot = AsianaBot()
    await bot.start(settings.discord_bot_token)


if __name__ == "__main__":
    asyncio.run(main())
