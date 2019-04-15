"""
Cog to allow slowmode in chat using asyncio.sleep
"""

import discord
import asyncio
from discord.ext import commands
from .utils import checks, embeds


class Slowmode(commands.Cog):
    """
    Main class wrapper
    """
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def on_message(self, message):
        try:
            if message.channel.id not in self.bot.slow_channels:
                return
            if message.author.bot:
                return
            try:
                self.bot.loop.create_task(self.slowmode_user(
                    message.author,
                    message.channel,
                    self.bot.slow_channels[message.channel.id]
                ))
            except Exception as e:
                self.bot.logger.warning(f'Error creating slowmode task: {e}')
        except AttributeError:
            pass

    async def slowmode_user(self, user, channel, interval):
        await self.remove_perms(user, channel)
        await asyncio.sleep(interval)
        await self.grant_perms(user, channel)

    async def remove_perms(self, user, channel):
        """
        removes a users perms on a channel
        """
        try:
            await channel.set_permissions(user, send_messages=False)
        except Exception as e:
            self.bot.logger.warning(f'{e}')

    async def grant_perms(self, user, channel):
        """
        Grants a users perms on a channel
        """
        try:
            await channel.set_permissions(user, overwrite=None)
        except Exception as e:
            self.bot.logger.warning(f'{e}')

    @commands.group()
    @commands.guild_only()
    @checks.has_permissions(manage_messages=True)
    async def slowmode(self, ctx):
        """
        Adds or removes a channel to slowmode list
        """
        if ctx.invoked_subcommand is None:
            return

    @slowmode.command(aliases=['add'], name='add_channel')
    async def _add_channel(self, ctx, interval=60):
        """
        Adds channel to slowmode list
        """
        added_channels = []
        desc = ''
        try:
            success = await \
                self.bot.pg_utils.add_slowmode_channel(
                    ctx.guild.id,
                    ctx.message.channel.id,
                    interval,
                    self.bot.logger
                )
            if success:
                added_channels.append(ctx.message.channel.name)
            if added_channels:
                for channel in added_channels:
                    desc += f'{channel} timeout: {interval} seconds.\n'
                local_embed = discord.Embed(
                    title=f'Channel added to slowmode list:',
                    description=desc,
                    color=0x419400
                )
                self.bot.slow_channels[ctx.message.channel.id] = interval
            else:
                local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding channels {e}')
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)

    @slowmode.command(aliases=['rem', 'remove', 'end'], name='rem_channel')
    async def __remove_channel(self, ctx):
        """
        Removes a channel from the slowmode list
        """
        removed_channels = []
        absent_channels = []
        desc = ''
        try:
            try:
                success = False
                success = await \
                    self.bot.pg_utils.rem_slowmode_channel(
                        ctx.guild.id, ctx.message.channel.id, self.bot.logger
                    )
            except ValueError:
                absent_channels.append(ctx.message.channel.name)
            if success:
                removed_channels.append(ctx.message.channel.name)
            if removed_channels:
                for channel in removed_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels removed from slowmode list:',
                    description=desc,
                    color=0x419400
                )
                slow_channels_n = \
                    await self.bot.pg_utils.get_slowmode_channels(
                        ctx.guild.id)
                self.bot.slow_channels = slow_channels_n
                if absent_channels:
                    desc = ''
                    for channel in absent_channels:
                        desc += f'{channel}\n'
                    local_embed.add_field(
                        name='Channels not in slowmode list :',
                        value=desc
                    )
            elif absent_channels:
                desc = ''
                for channel in absent_channels:
                    desc += f'{channel}\n'
                local_embed = discord.Embed(
                    title=f'Channels not in slowmode list: ',
                    description=desc,
                    color=0x651111
                )
            else:
                local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue: {e}')
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
