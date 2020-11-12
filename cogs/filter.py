"""Cog for filtering, primarily discord links, but maybe more later."""
import re

import discord
from discord.ext import commands
from .utils import checks, embeds


class Filter(commands.Cog):
    """Filtering of misc chats."""

    """It should be noted, this cog is called after
    run.py (obviously) so blacklisting
    cannot be done at this level, else it misses the help commands."""
    def __init__(self, bot):
        """Init method."""
        super().__init__()
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def invites(self, ctx):
        """Enables/Disables autodeletion of invites."""
        if ctx.invoked_subcommand is None:
            allowed = self.bot.server_settings[ctx.guild.id]["invites_allowed"]
            local_embed = discord.Embed(
                title=f'Invites are:',
                description=f"{'Allowed' if allowed else 'Disallowed'}",
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @invites.command(aliases=['enable'])
    async def allow(self, ctx):
        """Disables autodeletion of invites."""
        try:
            await self.bot.pg_utils.set_invites_allowed(
                ctx.guild.id, True)
        except Exception as e:
            local_embed = embeds.InternalErrorEmbed()
            self.bot.logger.warning(f'Error setting invites allowed: {e})')
            await ctx.send(embed=local_embed)
        self.bot.server_settings[ctx.guild.id]['invites_allowed'] = True
        local_embed = discord.Embed(
                title=f'Invites are now:',
                description=f'Allowed',
                color=0x419400
            )
        await ctx.send(embed=local_embed)

    @invites.command(aliases=['disable', 'delete'])
    async def disallow(self, ctx):
        """Enable autodeletion of invites."""
        try:
            await self.bot.pg_utils.set_invites_allowed(
                ctx.guild.id, False)
        except Exception as e:
            local_embed = embeds.InternalErrorEmbed()
            self.bot.logger.warning(f'Error setting invites disallowed: {e})')
            await ctx.send(embed=local_embed)
            return
        self.bot.server_settings[ctx.guild.id]['invites_allowed'] = False
        local_embed = discord.Embed(
                title=f'Invites are now:',
                description=f'Disallowed',
                color=0x419400
            )
        await ctx.send(embed=local_embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """General message catcher for filtering."""
        if isinstance(message.channel, discord.DMChannel):
            return
        try:
            if self.bot.server_settings[message.guild.id]['invites_allowed']:
                return
            if message.author.guild_permissions.manage_messages:
                return
            regexp = re.compile(
                r'(discord.gg\/)[a-zA-Z0-9]{0,7}|'
                r'(discordapp.com\/invite\/)[a-zA-Z0-9]{0,7}'
            )
            if bool(regexp.search(message.content)):
                await message.delete()
        except AttributeError:
            pass


def setup(bot):
    """General cog loading."""
    bot.add_cog(Filter(bot))
