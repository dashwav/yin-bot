"""
Cog for filtering, primarily discord links, but maybe more later
"""
import discord
from discord.ext import commands
from .utils import checks, embeds
import re


class Filter:
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def invites(self, ctx):
        """
        Enables/Disables autodeletion of invites
        """
        if not await checks.is_channel_blacklisted(self, ctx):
            return
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
        """
        Disables autodeletion of invites
        """
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
        """
        Enables autodeletion of invites
        """
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

    async def on_message(self, message):
        try:
            if self.bot.server_settings[message.guild.id]['invites_allowed']:
                return
            if message.author.guild_permissions.manage_messages:
                return
            regexp = re.compile(
                r'(discord.gg\/)[a-zA-Z0-9]{0,7}'
            )
            regexp2 = re.compile(
                r'(discordapp.com\/invite\/)[a-zA-Z0-9]{0,7}'
            )
            if bool(regexp.search(message.content)):
                await message.delete()
            elif bool(regexp2.search(message.content)):
                await message.delete()
        except AttributeError:
            pass
