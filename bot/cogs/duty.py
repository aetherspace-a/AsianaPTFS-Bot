import discord
from discord import app_commands
from discord.ext import commands

from bot.core.api_client import ApiClient
from bot.core.branding import embed_color, embed_footer


class DutyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api = ApiClient()

    @app_commands.command(name="clockin", description="Start your staff duty shift")
    async def clockin(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = await self.api.clock_in(
                str(interaction.user.id),
                interaction.user.display_name,
            )
            embed = discord.Embed(
                title="Clocked In",
                description="Your duty shift has started. Thank you for serving!",
                color=0x22C55E,
            )
            embed.add_field(
                name="Started",
                value=data["clock_in"][:19].replace("T", " "),
                inline=False,
            )
            embed.set_footer(text=embed_footer())
            await interaction.followup.send(embed=embed, ephemeral=True)
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)

    @app_commands.command(name="clockout", description="End your staff duty shift")
    async def clockout(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = await self.api.clock_out(
                str(interaction.user.id),
                interaction.user.display_name,
            )
            seconds = data.get("duration_seconds") or 0
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            embed = discord.Embed(
                title="Clocked Out",
                description=f"Shift duration: **{hours}h {mins}m**",
                color=embed_color(),
            )
            embed.set_footer(text=embed_footer())
            await interaction.followup.send(embed=embed, ephemeral=True)
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(DutyCog(bot))
