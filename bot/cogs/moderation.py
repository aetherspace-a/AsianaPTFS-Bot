import discord
from discord import app_commands
from discord.ext import commands


def is_staff():
    async def predicate(interaction: discord.Interaction) -> bool:
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            return False
        return (
            interaction.user.guild_permissions.manage_messages
            or interaction.user.guild_permissions.kick_members
            or interaction.user.guild_permissions.administrator
        )

    return app_commands.check(predicate)


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Delete recent messages (staff)")
    @app_commands.describe(amount="Number of messages (1-100)")
    @is_staff()
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100],
    ):
        if not interaction.channel or not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Text channel only.", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"Deleted **{len(deleted)}** messages.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member (staff)")
    @app_commands.describe(member="Member to kick", reason="Reason")
    @is_staff()
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided",
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.kick(reason=reason)
            await interaction.followup.send(f"Kicked {member.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Missing permissions.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member (staff)")
    @app_commands.describe(member="Member to ban", reason="Reason")
    @is_staff()
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided",
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            await member.ban(reason=reason)
            await interaction.followup.send(f"Banned {member.mention}.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("Missing permissions.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))
