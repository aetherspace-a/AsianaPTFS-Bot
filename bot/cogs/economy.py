import discord
from discord import app_commands
from discord.ext import commands

from bot.core.api_client import ApiClient
from bot.core.branding import embed_color, embed_footer, load_branding


class EconomyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.api = ApiClient()

    @app_commands.command(name="work", description="Earn WON (cooldown applies)")
    async def work(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            data = await self.api.work(
                str(interaction.user.id),
                interaction.user.display_name,
            )
            branding = load_branding()
            sym = branding["economy"]["currency_symbol"]
            if data["earned"] == 0:
                mins = data["cooldown_seconds_remaining"] // 60
                await interaction.followup.send(
                    f"Cooldown active. Try again in **{mins}** minutes.",
                    ephemeral=True,
                )
                return
            await interaction.followup.send(
                f"You earned **{sym}{data['earned']:,}**! Balance: **{sym}{data['new_balance']:,}**",
                ephemeral=True,
            )
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)

    @app_commands.command(name="balance", description="Check your WON balance")
    async def balance(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            await self.api.ensure_user(
                str(interaction.user.id),
                interaction.user.display_name,
            )
            data = await self.api.get_balance(str(interaction.user.id))
            sym = load_branding()["economy"]["currency_symbol"]
            embed = discord.Embed(
                title="Balance",
                description=f"**{sym}{data['won_balance']:,}**",
                color=embed_color(),
            )
            embed.set_footer(text=embed_footer())
            await interaction.followup.send(embed=embed, ephemeral=True)
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)

    @app_commands.command(name="pay", description="Pay WON to another user")
    @app_commands.describe(user="Recipient", amount="Amount of WON")
    async def pay(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: app_commands.Range[int, 1, 1_000_000],
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            data = await self.api.pay(
                str(interaction.user.id),
                str(user.id),
                amount,
            )
            sym = load_branding()["economy"]["currency_symbol"]
            await interaction.followup.send(
                f"Paid **{sym}{amount:,}** to {user.mention}. Your balance: **{sym}{data['from_balance']:,}**",
                ephemeral=True,
            )
        except RuntimeError as e:
            await interaction.followup.send(str(e), ephemeral=True)

    @app_commands.command(name="coinflip", description="Gamble WON — heads or tails")
    @app_commands.describe(bet="WON to bet", choice="heads or tails")
    @app_commands.choices(choice=[
        app_commands.Choice(name="heads", value="heads"),
        app_commands.Choice(name="tails", value="tails"),
    ])
    async def coinflip(
        self,
        interaction: discord.Interaction,
        bet: app_commands.Range[int, 100, 10000],
        choice: str,
    ):
        await interaction.response.defer()
        try:
            data = await self.api.coinflip(
                str(interaction.user.id),
                interaction.user.display_name,
                bet,
                choice,
            )
            sym = load_branding()["economy"]["currency_symbol"]
            outcome = "won" if data["won"] else "lost"
            embed = discord.Embed(
                title="Coinflip",
                description=(
                    f"Result: **{data['result']}** — You **{outcome}**!\n"
                    f"Payout: **{sym}{abs(data['payout']):,}**\n"
                    f"Balance: **{sym}{data['new_balance']:,}**"
                ),
                color=0x22C55E if data["won"] else 0xEF4444,
            )
            embed.set_footer(text=embed_footer())
            await interaction.followup.send(embed=embed)
        except RuntimeError as e:
            await interaction.followup.send(str(e))


async def setup(bot: commands.Bot):
    await bot.add_cog(EconomyCog(bot))
