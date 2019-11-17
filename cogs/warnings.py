"""Generalized warning system."""

import discord
from discord.ext import commands

from .utils import checks, embeds
from .utils.functions import GeneralMember


class Warnings(commands.Cog):
    """Generalized warning system."""

    def __init__(self, bot):
        """Init method."""
        super().__init__()
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def warn(self, ctx):
        """Root command for warnings."""
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Command Error',
                description=f"Please use either"
                            f"`.warn minor` or `.warn major`",
                color=0x419400
            )
            await ctx.send(embed=local_embed, delete_after=5)

    @warn.command(aliases=['!'])
    async def major(self, ctx, member: GeneralMember, *, reason: str = None):
        """Issue a major warning."""
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
            return
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
    async def minor(self, ctx, member: GeneralMember, *, reason: str = None):
        """Issue a minor warning."""
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
            return
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

    @warn.command(aliases=['e'])
    async def edit(self, ctx, member: GeneralMember,
                   index: int = None, dtype: str = None, *,
                   reason: str = None):
        """Edit a warning."""
        if not reason or not index or not dtype:
            await ctx.send(
                "You need to supply the correct parameters <member, index (from 1), warning type, reason>, try again.",  # noqa
                delete_after=5)
            return
        if len(reason) > 500:
            await ctx.send(
                "Reason must be shorter than 500 char",
                delete_after=5
            )
            return
        dtype = True if dtype.lower() == 'major' else False
        try:
            count = await self.bot.pg_utils.set_single_warning(
                ctx.guild.id,
                member.id,
                reason,
                dtype,
                index,
                self.bot.logger
            )
            local_embed = embeds.WarningEditEmbed(member, dtype, reason, count)
            await ctx.send(embed=local_embed)
        except Exception as e:
            await ctx.send(embed=embeds.InternalErrorEmbed())
            self.bot.logger.warning(f'Error editing warnings for user: {e}')

    @warn.command(aliases=['rm', 'rem', 'remove', 'delete'])
    async def remove_warning(self, ctx, member: GeneralMember,
                             index: int = None):
        """Remove a warning from a user at selected index."""
        if member is None or index is None:
            await ctx.send(
                "You need to supply the correct parameters <member, index (from 1)>, try again.",  # noqa
                delete_after=5)
            return
        try:
            status = await self.bot.pg_utils.delete_single_warning(
                ctx.guild.id,
                member.id,
                index,
                self.bot.logger
            )
            if '0' in status:
                await ctx.send(
                    embed=embeds.CommandErrorEmbed(
                        'User has not recieved any warnings.'),
                    delete_after=3)
                return
            local_embed = embeds.WarningRmEmbed(member)
            await ctx.send(embed=local_embed)
        except Exception as e:
            await ctx.send(embed=embeds.InternalErrorEmbed())
            self.bot.logger.warning(f'Error removing warning for user: {e}')

    @commands.command(aliases=['infractions'])
    @commands.guild_only()
    async def warnings(self, ctx):
        """[warnings|infractions] <member|me> [recent=True]

        Return all the warnings a user has. You can just pass in me to get your own warnings in DM.
        """
        resolved = ctx.channel.permissions_for(ctx.author)
        if getattr(resolved, 'manage_roles', None) and not ctx.message.content.lower().endswith('warnings me'):
            recent = False if ctx.message.content.lower().endswith('false') else True
            await _warnings(self.bot, ctx, await GeneralMember.convert(self, ctx, ctx.message.content), ctx.guild.id, recent)
            return
        try:
            await ctx.author.create_dm()
            await _warnings(self.bot, ctx.author.dm_channel, ctx.author, ctx.guild.id, False)
        except Exception as e:
            self.bot.logger.warn("Failed to send dm.")

    @warnings.error
    async def warnings_error(self, ctx, error):
        """Specialized warning error."""
        self.bot.logger.warning(f'Error retrieving warnings for user {error}')


async def _warnings(bot, channel, member: GeneralMember, guild_id: int, recent: bool = True):
    """Return all the warnings a user has."""
    try:
        warnings = None
        moderations = None
        count = [await bot.pg_utils.get_warning_count(guild_id, member.id),  # noqa
                    await bot.pg_utils.get_moderation_count(guild_id, member.id)]  # noqa
        warnings = await bot.pg_utils.get_warnings(
            guild_id,
            member.id,
            bot.logger,
            recent=recent)
        moderations = await bot.pg_utils.get_moderation(
            guild_id,
            member.id,
            bot.logger,
            recent=recent)
    except Exception as e:
        await channel.send(embed=embeds.InternalErrorEmbed())
        bot.logger.warning(f'Error trying to get user warnings: {e}')
    try:
        local_embed = embeds.WarningListEmbed(
            member, warnings, bot.logger, count[0] > len(warnings))
        await channel.send(embed=local_embed)
        if moderations:
            mod_embed = embeds.ModerationListEmbed(
                member, moderations, bot.logger,
                count[1] > len(moderations))
            await channel.send(embed=mod_embed)
    except Exception as e:
        await channel.send(embed=embeds.InternalErrorEmbed())
        bot.logger.warning(f'Error trying to create/send user warnings: {e}')


def setup(bot):
    """General cog loading."""
    bot.add_cog(Warnings(bot))
