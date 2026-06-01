import asyncio
import tempfile
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands
from gtts import gTTS

from bot.core.branding import load_branding


class VoiceCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="announce",
        description="TTS boarding/landing announcement in your voice channel",
    )
    @app_commands.describe(
        flight_number="Flight number e.g. OZ204",
        announcement_type="boarding or landing",
    )
    @app_commands.choices(announcement_type=[
        app_commands.Choice(name="boarding", value="boarding"),
        app_commands.Choice(name="landing", value="landing"),
    ])
    async def announce(
        self,
        interaction: discord.Interaction,
        flight_number: str,
        announcement_type: str,
    ):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message(
                "Join a voice channel first.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)
        branding = load_branding()
        airline = branding["airline_name"]
        ann = announcement_type

        if ann == "boarding":
            text = (
                f"Good afternoon. This is an announcement for {airline}. "
                f"Flight {flight_number} is now boarding. "
                f"Passengers with boarding passes, please proceed to the gate."
            )
        else:
            text = (
                f"Ladies and gentlemen, welcome to your destination. "
                f"{airline} flight {flight_number} has landed. "
                f"Please remain seated with your seatbelt fastened until the aircraft has come to a complete stop."
            )

        channel = interaction.user.voice.channel
        if not isinstance(channel, discord.VoiceChannel):
            await interaction.followup.send("Invalid voice channel.", ephemeral=True)
            return

        vc: discord.VoiceClient | None = None
        tmp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = Path(tmp.name)
            gTTS(text, lang="en").save(str(tmp_path))

            vc = await channel.connect()
            audio = discord.FFmpegPCMAudio(str(tmp_path))
            finished = asyncio.Event()

            def after_play(err):
                if err:
                    print(f"Playback error: {err}")
                finished.set()

            vc.play(audio, after=after_play)
            await finished.wait()
            await interaction.followup.send(
                f"Played **{ann}** announcement for **{flight_number}**.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(f"Announcement failed: {e}", ephemeral=True)
        finally:
            if vc and vc.is_connected():
                await vc.disconnect()
            if tmp_path and tmp_path.exists():
                tmp_path.unlink(missing_ok=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(VoiceCog(bot))
