"""Basic bot administration commands."""
import discord
from discord.ext import commands
from .utils import checks, embeds


class Admin(commands.Cog):
    """Cogs for admins."""

    def __init__(self, bot):
        """Init method."""
        super().__init__()
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def prefix(self, ctx):
        """Either returns current prefix or sets new one."""
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
        """Set the prefix for the server."""
        if len(prefix.strip()) > 2:
            local_embed = discord.Embed(
                title=f'Prefix must be less than or equal to two characters',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed, delete_after=3)
            return
        try:
            success = await self.bot.pg_utils.set_prefix(
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
                await ctx.send(embed=local_embed, delete_after=3)
        except Exception:
            local_embed = embeds.InternalErrorEmbed()
            ctx.send(local_embed)

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def modlog(self, ctx):
        """Add or remove a channel to modlog list."""
        if ctx.invoked_subcommand is None:
            desc = ''
            modlogs = await self.bot.pg_utils.get_modlogs(
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

    @modlog.command(aliases=['add'])
    async def add_channel(self, ctx):
        """Add channel to modlog list."""
        added_channels = []
        desc = ''
        try:
            success = await \
                self.bot.pg_utils.add_modlog_channel(
                    ctx.guild.id, ctx.message.channel.id, self.bot.logger
                )
            if success:
                added_channels.append(ctx.message.channel.name)
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
                local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding channels {e}')
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)

    @modlog.command(aliases=['rem', 'remove'])
    async def remove_channel(self, ctx):
        """Remove a channel from the modlog list."""
        removed_channels = []
        absent_channels = []
        desc = ''
        try:
            try:
                success = False
                success = await \
                    self.bot.pg_utils.rem_modlog_channel(
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
                    title=f'Channels removed from modlog list:',
                    description=desc,
                    color=0x419400
                )
                modlogs = await self.bot.pg_utils.get_modlogs(
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
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)

    @commands.group(aliases=['bl'])
    @commands.guild_only()
    @checks.is_admin()
    async def blacklist(self, ctx):
        """Add or remove a channel to blacklist channel list."""
        if ctx.invoked_subcommand is None:
            desc = ''
            modlogs = await self.bot.pg_utils.get_blacklist_channels(
                ctx.guild.id)
            for channel in ctx.guild.channels:
                if channel.id in modlogs:
                    desc += f'{channel.name} \n'
            local_embed = discord.Embed(
                title=f'Channels in blacklist:',
                description=f'{desc}',
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @blacklist.command()
    async def add(self, ctx):
        """Add channel to blacklist."""
        added_channels = []
        desc = ''
        try:
            success = await \
                self.bot.pg_utils.add_blacklist_channel(
                    ctx.guild.id, ctx.message.channel.id, self.bot.logger
                )
            if success:
                added_channels.append(ctx.message.channel.name)
                self.bot.blchannels.append(ctx.message.channel.id)
            if added_channels:
                for channel in added_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels added to blacklist:',
                    description=desc,
                    color=0x419400
                )
            else:
                self.bot.logger.info(f'error')
                local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.info(f'Error adding channels {e}')
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)

    @blacklist.command(aliases=['rem'])
    async def remove(self, ctx):
        """Remove a channel from the blacklist."""
        removed_channels = []
        absent_channels = []
        desc = ''
        try:
            try:
                success = False
                success = await \
                    self.bot.pg_utils.rem_blacklist_channel(
                        ctx.guild.id, ctx.message.channel.id, self.bot.logger
                    )
            except ValueError:
                absent_channels.append(ctx.message.channel.name)
            if success:
                removed_channels.append(ctx.message.channel.name)
                if ctx.message.channel.id in self.bot.blchannels:
                    del self.bot.blchannels[self.bot.blchannels.index(ctx.message.channel.id)]  # noqa
            if removed_channels:
                for channel in removed_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels removed from blacklist:',
                    description=desc,
                    color=0x419400
                )
                if absent_channels:
                    desc = ''
                    for channel in absent_channels:
                        desc += f'{channel}\n'
                    local_embed.add_field(
                        name='Channels not in blacklist:',
                        value=desc
                    )
            elif absent_channels:
                desc = ''
                for channel in absent_channels:
                    desc += f'{channel}\n'
                local_embed = discord.Embed(
                    title=f'Channels not in blacklist: ',
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


def setup(bot):
    """General cog loading."""
    bot.add_cog(Admin(bot))
