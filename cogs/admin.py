"""
Basic bot administration commands
"""
import discord
from discord.ext import commands
from .utils import checks


class Admin:

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def prefix(self, ctx):
        """
        Either returns current prefix or sets new one
        """
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Current prefix is: '
                f'\'{self.bot.server_settings[ctx.guild.id]["prefix"]}\'',
                description=' ',
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @prefix.command()
    async def change(self, ctx, prefix):
        """
        sets the prefix for the server
        """
        if len(prefix.strip()) > 2:
            local_embed = discord.Embed(
                title=f'Prefix must be less than or equal to two characters',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        try:
            success = await self.bot.postgres_controller.set_prefix(
                ctx.guild.id,
                prefix,
                self.bot.logger
            )
            if success:
                self.bot.server_settings[ctx.guild.id]['prefix'] = prefix
                local_embed = discord.Embed(
                    title=f'Server prefix set to \'{prefix}\'',
                    description=' ',
                    color=0x419400
                )
        except Exception as e:
            local_embed = discord.Embed(
                title=f'Internal issue, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def modlog(self, ctx):
        """
        Either returns current prefix or sets new one
        """
        if ctx.invoked_subcommand is None:
            desc = ''
            modlogs = await self.bot.postgres_controller.get_modlogs(
                ctx.guild.id)
            for channel in ctx.guild.channels:
                if channel.id in modlogs:
                    desc += f'{channel.name} \n'
            local_embed = discord.Embed(
                title=f'Current modlog list is: ',
                description=desc,
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @modlog.command()
    async def add(self, ctx, *, channels):
        """
        sets the prefix for the server
        """
        added_channels = []
        desc = ''
        channel_mentions = ctx.message.channel_mentions
        if not channel_mentions:
            local_embed = discord.Embed(
                title=f'No channel mentions detected, try again.',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        try:
            for channel in channel_mentions:
                success = await \
                    self.bot.postgres_controller.add_modlog_channel(
                        ctx.guild.id, channel.id, self.bot.logger
                    )
                if success:
                    added_channels.append(channel.name)
            if added_channels:
                for channel in added_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels added to modlog list:',
                    description=desc,
                    color=0x419400
                )
                self.bot.server_settings[ctx.guild.id]['modlog_enabled'] = True
            else:
                self.bot.logger.info(f'slktjsaj')
                local_embed = discord.Embed(
                    title=f'Internal error, please contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding channels {e}')
            local_embed = discord.Embed(
                title=f'Internal issue, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)

    @modlog.command(aliases=['rem'])
    async def remove(self, ctx, *, channels):
        """
        Removes a channel from the modlog list
        """
        removed_channels = []
        absent_channels = []
        desc = ''
        channel_mentions = ctx.message.channel_mentions
        if not channel_mentions:
            local_embed = discord.Embed(
                title=f'No channel mentions detected, try again.',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        try:
            for channel in channel_mentions:
                try:
                    success = False
                    success = await \
                        self.bot.postgres_controller.rem_modlog_channel(
                            ctx.guild.id, channel.id, self.bot.logger
                        )
                except ValueError:
                    absent_channels.append(channel.name)
                if success:
                    removed_channels.append(channel.name)
            if removed_channels:
                for channel in removed_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels removed from modlog list:',
                    description=desc,
                    color=0x419400
                )
                modlogs = await self.bot.postgres_controller.get_modlogs(
                    ctx.guild.id)
                if not modlogs:
                    self.bot.server_settings[ctx.guild.id]['modlog_enabled']\
                        = False
                if absent_channels:
                    desc = ''
                    for channel in absent_channels:
                        desc += f'{channel}\n'
                    local_embed.add_field(
                        name='Channels not in modlog list :',
                        value=desc
                    )
            elif absent_channels:
                desc = ''
                for channel in absent_channels:
                    desc += f'{channel}\n'
                local_embed = discord.Embed(
                    title=f'Channels not in modlog list: ',
                    description=desc,
                    color=0x651111
                )
            else:
                local_embed = discord.Embed(
                    title=f'Internal error, please contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.warning(f'Issue: {e}')
            local_embed = discord.Embed(
                title=f'Internal issue, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)


def setup(bot):
    bot.add_cog(Admin(bot))
