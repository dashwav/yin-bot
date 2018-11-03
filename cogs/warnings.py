"""
Wow look a warning system, what an original idea.
Loosely (moreso in some places) based off of Mee6's warning
"""
import discord
from discord.ext import commands
from .utils import checks, embeds


class Warnings:
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def warn(self, ctx):
        """
        Base command for warning system
        """
        if not await checks.is_channel_blacklisted(self, ctx):
            return
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Command Error',
                description=f"Please use either"
                            f"`.warn minor` or `.warn major`",
                color=0x419400
            )
            await ctx.send(embed=local_embed, delete_after=5)

    @warn.command(aliases=['!'])
    async def major(self, ctx, member: discord.Member, *, reason: str=None):
        """
        Gives a major warning
        """
        if reason is None:
                await ctx.send(
                    "You need to supply a reason, try again.",
                    delete_after=5)
                return
        if len(reason) > 500:
            await ctx.send(
                "Reason must be shorter than 500 char",
                delete_after=5
            )
        try:
            count = await self.bot.pg_utils.add_warning(
                ctx.guild.id,
                member.id,
                reason,
                True,
                self.bot.logger
            )
            local_embed = embeds.WarningAddEmbed(member, True, reason, count)
            await ctx.send(embed=local_embed)
        except Exception as e:
            await ctx.send(embed=embeds.InternalErrorEmbed())
            self.bot.logger.warning(f'Error trying to warn user: {e}')

    @warn.command(aliases=['?'])
    async def minor(self, ctx, member: discord.Member, *, reason: str=None):
        """
        Gives a minor warning
        """
        if reason is None:
                await ctx.send(
                    "You need to supply a reason, try again.",
                    delete_after=5)
                return
        if len(reason) > 500:
            await ctx.send(
                "Reason must be shorter than 500 char",
                delete_after=5
            )
        try:
            count = await self.bot.pg_utils.add_warning(
                ctx.guild.id,
                member.id,
                reason,
                False,
                self.bot.logger
            )
            local_embed = embeds.WarningAddEmbed(member, False, reason, count)
            await ctx.send(embed=local_embed)
        except Exception as e:
            await ctx.send(embed=embeds.InternalErrorEmbed())
            self.bot.logger.warning(f'Error trying to warn user: {e}')

    @warn.command(aliases=['rem', 'remove'])
    async def remove_warning(self, ctx, member: discord.Member, index: int):
        """
        This command removes a warning from a user at selected index
        """
        return

    @commands.command(aliases=['infractions'])
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def warnings(self, ctx, member: discord.Member):
        """
        Returns all the warnings a user has gotten
        """
        if not await checks.is_channel_blacklisted(self, ctx):
            return
        try:
            warnings = None
            moderations = None
            warnings = await self.bot.pg_utils.get_warnings(
                ctx.guild.id,
                member.id,
                self.bot.logger)
            moderations = await self.bot.pg_utils.get_moderation(
                ctx.guild.id,
                member.id,
                self.bot.logger)
            local_embed = embeds.WarningListEmbed(
                member, warnings, self.bot.logger)
            await ctx.send(embed=local_embed)
            if moderations:
                mod_embed = embeds.ModerationListEmbed(
                    member, moderations, self.bot.logger)
                await ctx.send(embed=mod_embed)
        except Exception as e:
            await ctx.send(embed=embeds.InternalErrorEmbed())
            self.bot.logger.warning(f'Error trying to get user warnings: {e}')

    @warnings.error
    async def warnings_error(self, ctx, error):
        self.bot.logger.warnign(f'Error retrieving warnings for user {error}')