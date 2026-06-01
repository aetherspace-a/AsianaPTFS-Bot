import discord
from discord import app_commands
from discord.ext import commands

from bot.core.api_client import ApiClient
from bot.core.branding import embed_color, embed_footer, load_branding
from bot.core.config import get_settings


class FlightsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api = ApiClient()
        self.settings = get_settings()

    @app_commands.command(name="flights", description="List upcoming flights")
    async def flights(self, interaction: discord.Interaction):
        await interaction.response.defer()
        branding = load_branding()
        try:
            flights = await self.api.list_flights()
            upcoming = [f for f in flights if f.get("status") != "Landed"][:10]
            embed = discord.Embed(
                title=f"{branding['airline_name']} — Upcoming Flights",
                color=embed_color(),
            )
            if not upcoming:
                embed.description = "No upcoming flights scheduled."
            else:
                for f in upcoming:
                    dep = f["departure_time"][:16].replace("T", " ")
                    embed.add_field(
                        name=f"{f['flight_number']} [{f['status']}]",
                        value=f"{f['departure']} → {f['arrival']}\n{dep}",
                        inline=False,
                    )
            embed.set_footer(text=embed_footer())
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"Failed to fetch flights: {e}")

    @app_commands.command(name="book", description="Get link to book a flight on the web")
    async def book(self, interaction: discord.Interaction):
        branding = load_branding()
        embed = discord.Embed(
            title="Book a flight",
            description=(
                f"Visit the **{branding['airline_name']}** portal to search flights, "
                f"pick your seat, and pay with WON.\n\n"
                f"**{self.settings.frontend_url}/flights**"
            ),
            color=embed_color(),
        )
        embed.set_footer(text=embed_footer())
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(FlightsCog(bot))
