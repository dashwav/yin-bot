"""
This cog will handle logging all server actions to a specific channel
"""
import discord
from discord.ext import commands
from .utils import checks
from .utils import embeds


class Logging():

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.logger = bot.logger

    @commands.group(aliases=['ldbc', 'get_these_errors_outta_here'])
    @checks.is_owner()
    async def log_db_cleaning(self, ctx):
        """
        Cleans a deleted channel from the voice log and server log databases.
        """
        embed_title = f'Database Cleaning Tool'
        if ctx.subcommand_passed is None:
            local_embed = discord.Embed(
                title = embed_title,
                description = f'Check the console for channel '\
                f'errors and pass them as so:\n'\
                f'ldbc *channel snowflake id*',
                color = 0xCCCCCC
            )
            await ctx.send(embed=local_embed)
            return
        remove_id = ctx.subcommand_passed
        was_log_removed = False
        was_voice_removed = False
        for guild in self.bot.guilds:
            log_channel = await self.bot.pg_utils.get_logger_channels(guild.id)
            voice_channel = await self.bot.pg_utils.get_voice_channels(guild.id)
            for remove_id in log_channel:
                await self.bot.pg_utils.rem_logger_channel(
                    guild.id, remove_id, self.bot.logger
                )
                was_log_removed = True
            for remove_id in voice_channel:
                await self.bot.pg_utils.rem_voice_channel(
                    guild_id, remove_id, self.bot.logger
                )
                was_voice_removed = True
        if was_log_removed or was_voice_removed
            local_embed = discord.Embed(
            title = embed_title,
            description = f'Channel was removed from database',
            color = 0x419400
            )
            await ctx.send(embed=local_embed)
            return
        local_embed = discord.Embed(
            title = embed_title,
            description = f'Channel not found in database, '\
            f'or you did not give a valid channel id',
            color = 0x651111
            )
        await ctx.send(embed=local_embed)
    
    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def logging(self, ctx):
        """
        Enables and disables logging to channel.
        """
        if not await checks.is_channel_blacklisted(self, ctx):
            return
        if ctx.invoked_subcommand is None:
            desc = ''
            modlogs = await self.bot.pg_utils.get_logger_channels(
                ctx.guild.id)
            for channel in ctx.guild.channels:
                if channel.id in modlogs:
                    desc += f'{channel.name} \n'
            local_embed = discord.Embed(
                title=f'Current log channel list is: ',
                description=desc,
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @logging.command()
    async def enable(self, ctx):
        """
        Adds channel to the log channel list.
        """
        added_channels = []
        desc = ''
        try:
            success = await \
                self.bot.pg_utils.add_logger_channel(
                    ctx.guild.id, ctx.message.channel.id, self.bot.logger
                )
            if success:
                added_channels.append(ctx.message.channel.name)
            if added_channels:
                for channel in added_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels added to log channel list:',
                    description=desc,
                    color=0x419400
                )
                self.bot.server_settings[ctx.guild.id]['logging_enabled']\
                    = True
            else:
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

    @logging.command(aliases=['rem'])
    async def disable(self, ctx):
        """
        Removes channel from the log channel list
        """
        removed_channels = []
        absent_channels = []
        desc = ''
        try:
            try:
                success = False
                success = await \
                    self.bot.pg_utils.rem_logger_channel(
                        ctx.guild.id, ctx.message.channel.id, self.bot.logger
                    )
            except ValueError as e:
                absent_channels.append(ctx.message.channel.name)
            if success:
                removed_channels.append(ctx.message.channel.name)
            if removed_channels:
                for channel in removed_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels removed from log channel list:',
                    description=desc,
                    color=0x419400
                )
                logs = await self.bot.pg_utils.get_logger_channels(
                    ctx.guild.id)
                if not logs:
                    self.bot.server_settings[ctx.guild.id]['logging_enabled']\
                        = False
                if absent_channels:
                    desc = ''
                    for channel in absent_channels:
                        desc += f'{channel}\n'
                    local_embed.add_field(
                        name='Channels not in log channel list :',
                        value=desc
                    )
            elif absent_channels:
                desc = ''
                for channel in absent_channels:
                    desc += f'{channel}\n'
                local_embed = discord.Embed(
                    title=f'Channels not in log channel list: ',
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

    @commands.group(aliases=['vclogs', 'prescence_logging'])
    @commands.guild_only()
    @checks.is_admin()
    async def voice_logging(self, ctx):
        """
        Enables and disables logging to channel.
        """
        if not await checks.is_channel_blacklisted(self, ctx):
            return
        if ctx.invoked_subcommand is None:
            desc = ''
            voicelogs = await self.bot.pg_utils.get_voice_channels(
                ctx.guild.id)
            for channel in ctx.guild.channels:
                if channel.id in voicelogs:
                    desc += f'{channel.name} \n'
            local_embed = discord.Embed(
                title=f'Current voice log channel list is: ',
                description=desc,
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @voice_logging.command(name='enable')
    async def _enable(self, ctx):
        """
        Adds channel to the voice log channel list.
        """
        added_channels = []
        desc = ''
        try:
            success = await \
                self.bot.pg_utils.add_voice_channel(
                    ctx.guild.id, ctx.message.channel.id, self.bot.logger
                )
            if success:
                added_channels.append(ctx.message.channel.name)
            if added_channels:
                for channel in added_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels added to voice log channel list:',
                    description=desc,
                    color=0x419400
                )
            else:
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

    @voice_logging.command(name='disable', aliases=['rem'])
    async def _disable(self, ctx):
        """
        Removes channel from the voice log channel list.
        """
        removed_channels = []
        absent_channels = []
        desc = ''
        try:
            try:
                success = False
                success = await \
                    self.bot.pg_utils.rem_voice_channel(
                        ctx.guild.id, ctx.message.channel.id, self.bot.logger
                    )
            except ValueError as e:
                absent_channels.append(ctx.message.channel.name)
            if success:
                removed_channels.append(ctx.message.channel.name)
            if removed_channels:
                for channel in removed_channels:
                    desc += f'{channel} \n'
                local_embed = discord.Embed(
                    title=f'Channels removed from voice log channel list:',
                    description=desc,
                    color=0x419400
                )
                if absent_channels:
                    desc = ''
                    for channel in absent_channels:
                        desc += f'{channel}\n'
                    local_embed.add_field(
                        name='Channels not in voice log channel list :',
                        value=desc
                    )
            elif absent_channels:
                desc = ''
                for channel in absent_channels:
                    desc += f'{channel}\n'
                local_embed = discord.Embed(
                    title=f'Channels not in voice log channel list: ',
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

    async def on_member_ban(self, guild, user):
        """
        sends message on user ban
        """
        if self.bot.server_settings[guild.id]['logging_enabled']:
            channels = await self.bot.pg_utils.get_logger_channels(
                guild.id)
            local_embed = embeds.LogBanEmbed(user)
            for channel in channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed = local_embed)
                except Exception as e:
                    self.bot.logger.info(
                        f'Error logging user ban in channel {channel}'
                        f', error: {e}'
                    )
                    
    async def on_member_join(self, member):
        """
        Sends message on a user join
        """
        if self.bot.server_settings[member.guild.id]['logging_enabled']:
            channels = await self.bot.pg_utils.get_logger_channels(
                member.guild.id)
            local_embed = embeds.JoinEmbed(member)
            for channel in channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed = local_embed)
                except Exception as e:
                    self.bot.logger.info(
                        f'Error logging user join in channel {channel}'
                        f', error: {e}'
                    )

    async def on_member_remove(self, member):
        """
        Sends message on a user leaving
        """
        if self.bot.server_settings[member.guild.id]['logging_enabled']:
            channels = await self.bot.pg_utils.get_logger_channels(
                member.guild.id)
            local_embed = embeds.LeaveEmbed(member)
            for channel in channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed = local_embed)
                except Exception as e:
                    self.bot.logger.info(
                        f'Error logging user leave in channel {channel}'
                        f', error: {e}'
                    )

    async def on_message_edit(self, before, after):
        """
        sends message on a user editing messages
        """
        try:
            if self.bot.server_settings[before.guild.id]['logging_enabled']:
                if not before.content.strip() != after.content.strip():
                    return
                channels = await self.bot.pg_utils.get_logger_channels(
                    before.guild.id)
                try:
                    local_embed = embeds.MessageEditEmbed(
                        before.author,
                        before.channel.name,
                        before.content,
                        after.content
                    )
                    for channel in channels:
                        ch = self.bot.get_channel(channel)
                        await ch.send(embed=local_embed)
                except Exception as e:
                    self.bot.logger.warning(
                        f'Issue logging message edit in channel {channel}'
                        f', error: {e}'
                    )
        except AttributeError:
            pass

    async def on_message_delete(self, message):
        """
        sends message on a user editing messages
        """
        if self.bot.server_settings[message.guild.id]['logging_enabled']:
            if message.author.bot:
                return
            channels = await self.bot.pg_utils.get_logger_channels(
                message.guild.id)
            try:
                local_embed = embeds.MessageDeleteEmbed(
                    message.author,
                    message.channel.name,
                    message.content,
                )
                for channel in channels:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed=local_embed)
            except Exception as e:
                self.bot.logger.warning(
                    f'Issue logging message delete in channel {channel}'
                    f', error: {e}'
                )

    async def on_member_update(self, before, after):
        """
        sends message on a user role or name update
        """
        if not self.bot.server_settings[before.guild.id]['logging_enabled']:
            return
        user_mutuals = []
        for guild in self.bot.guilds:
            if before in guild.members:
                user_mutuals.append(guild.id)
        extended_channels = []
        for guild_id in user_mutuals:
            extended_channels.extend(
                await self.bot.pg_utils.get_logger_channels(
                    guild_id))
        channels = await self.bot.pg_utils.get_logger_channels(
                before.guild.id)
        if before.roles != after.roles:
            role_diff = set(after.roles) - (set(before.roles))
            for role in role_diff:
                local_embed = embeds.RoleAddEmbed(
                    after,
                    role.name
                )
                for channel in channels:
                    try:
                        ch = self.bot.get_channel(channel)
                        await ch.send(embed=local_embed)
                    except Exception as e:
                        self.bot.logger.info(
                            f'Error logging role change'
                            f' in channel {channel}, error: {e}'
                        )
            role_diff = set(before.roles) - (set(after.roles))
            for role in role_diff:
                local_embed = embeds.RoleRemoveEmbed(
                    after,
                    role.name
                )
                for channel in channels:
                    try:
                        ch = self.bot.get_channel(channel)
                        await ch.send(embed=local_embed)
                    except Exception as e:
                        self.bot.logger.info(
                            f'Error logging role remove in'
                            f' channel {channel}, error: {e}'
                        )
        if before.name != after.name:
            local_embed = embeds.UsernameUpdateEmbed(
                after, before.name, after.name)
            for channel in extended_channels:
                try:
                    ch = self.bot.get_channel(channel)
                    await ch.send(embed=local_embed)
                except Exception as e:
                    self.bot.logger.info(
                        f'Error logging name change'
                        f' in channel {channel}, error {e}'
                    )  

    async def on_voice_state_update(self, member, before, after):
        """
        Sends a message on user vc update
        """
        vc_logging = await self.bot.pg_utils.get_voice_logging(
            member.guild.id)
        if not vc_logging:
            return
        vc_channels = await self.bot.pg_utils.get_voice_channels(
            member.guild.id
        )
        if before.channel is None and after.channel:
            local_embed = embeds.VoiceChannelStateEmbed(
                member, after.channel, 'joined'
            )
            for channel in vc_channels:
                try:
                    channel = self.bot.get_channel(channel)
                    await channel.send(embed=local_embed)
                except Exception as e:
                    self.bot.logger.info(
                        f'Error logging voice join in'
                        f' channel {channel}, error: {e}'
                    )
        elif after.channel is None and before.channel:
            local_embed = embeds.VoiceChannelStateEmbed(
                member, before.channel, 'left'
            )
            for channel in vc_channels:
                try:
                    channel = self.bot.get_channel(channel)
                    await channel.send(embed=local_embed)
                except Exception as e:
                    self.bot.logger.info(
                        f'Error logging voice leave in'
                        f' channel {channel}, error: {e}'
                    )
        elif before.channel != after.channel:
            local_embed = embeds.VoiceChannelMoveEmbed(
                member, before.channel, after.channel
            )
            for channel in vc_channels:
                try:
                    channel = self.bot.get_channel(channel)
                    await channel.send(embed=local_embed)
                except Exception as e:
                    self.bot.logger.info(
                        f'Error logging voice move in'
                        f' channel {channel}, error: {e}'
                    )
                    
    async def on_guild_channel_delete(channel):
        """
        attempts to remove deleted channel from the logging databases
        """
        server_del = channel.guild.id
        try:
            success = false
            success = await \
                self.bot.pg_utils.rem_logger_channel(
                    server_del, channel, self.bot.logger
                )
        if success:
            self.bot.logger.info(
                f'Channel deleted from server {server_del}'
                f', removed from log db'
            )
        try:
            success = false
            success = await \
                self.bot.pg_utils.rem_voice_channel(
                    server_del, channel, self.bot.logger
                )
        if success:
            self.bot.logger.info(
                f'Channel deleted from server {server_del}'
                f', removed from log db'
            )
            
            
def setup(bot):
    bot.add_cog(Logging(bot))
