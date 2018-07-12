"""
This cog is the moderation toolkit this is for tasks such as
kicking/banning users.
"""
import discord
from discord.ext import commands
from .utils import helpers, checks, embeds
from .utils.enums import Action


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            m = await commands.MemberConverter().convert(ctx, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid'\
                                            'member or member ID.") from None
        else:
            can_execute = ctx.author.id == ctx.bot.owner_id or \
                          ctx.author == ctx.guild.owner or \
                          ctx.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this'
                                           ' user due to role hierarchy.')
            return m.id


class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        ban_list = await ctx.guild.bans()
        try:
            member_id = int(argument, base=10)
            entity = discord.utils.find(
                lambda u: u.user.id == member_id, ban_list)
        except ValueError:
            entity = discord.utils.find(
                lambda u: str(u.user) == argument, ban_list)

        if entity is None:
            raise commands.BadArgument("Not a valid previously-banned member.")
        return entity


class ActionReason(commands.Converter):
    async def convert(self, ctx, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(
                f'reason is too long ({len(argument)}/{reason_max})')
        return ret


class Moderation:
    """
    Main cog class for moderation tools (kicking, banning, unbanning)
    """
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.command()    
    @checks.has_permissions(ban_members=True)
    @commands.guild_only()
    async def logban(self, ctx, member: BannedMember, *,
                   reason: ActionReason = None):
        """
        Logs a right-click ban to modlog channels
        """
        if self.bot.server_settings[ctx.guild.id]['modlog_enabled']:
            try:
                confirm = await helpers.custom_confirm(ctx,
                    f'```\nUser: {member.user}\nReason: {reason}\n```'
                )
                if not confirm: 
                    return
                resp_mod = ctx.author
                ban_reason = reason if reason else member.reason
                local_embed = embeds.BanEmbed(member.user, resp_mod, ban_reason)
                mod_logs = await self.bot.pg_utils.get_modlogs(
                        ctx.guild.id)
                for channel_id in mod_logs:
                    await (self.bot.get_channel(channel_id)).send(
                        embed=local_embed)
            except Exception as e:
                self.bot.logger.warning(f'Issue posting to mod log: {e}')
        else:
            await ctx.send(f'No modlog channels detected', delete_after=3)

    @commands.command()    
    @checks.has_permissions(ban_members=True)
    @commands.guild_only()
    async def moderate(self, ctx, member: discord.Member, *,
                   reason: ActionReason = None):
        """
        Logs a punishment for a user
        """
        if self.bot.server_settings[ctx.guild.id]['modlog_enabled']:
            try:
                confirm = await helpers.custom_confirm(ctx,
                    f'```\nUser: {member}\nReason: {reason}\n```'
                )
                if not confirm: 
                    return
                local_embed = embeds.ModerationEmbed(member, ctx.author, reason)
                mod_logs = await self.bot.pg_utils.get_modlogs(
                        ctx.guild.id)
                for channel_id in mod_logs:
                    await (self.bot.get_channel(channel_id)).send(
                        embed=local_embed)
            except Exception as e:
                self.bot.logger.warning(f'Issue posting to mod log: {e}')
        else:
            await ctx.send(f'No modlog channels detected', delete_after=3)

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def footer(self, ctx):
        """
        Ban/kick footer command. If no subcommand is
        invoked, it will return the current ban/kick footer
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        ban_footer = await self.bot.pg_utils.get_ban_footer(
            ctx.guild.id,
            self.bot.logger
        )
        kick_footer = await self.bot.pg_utils.get_kick_footer(
            ctx.guild.id,
            self.bot.logger
        )
        footer_msg = f'**Ban Footer**:\n\n{ban_footer}\n\n**Kick Footer:**\n\n{kick_footer}'
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Current welcome message: ',
                description=footer_msg
            )
            await ctx.send(embed=local_embed)

    @footer.command(name='set_ban')
    async def set_ban_footer(self, ctx, *, footer_string):
        """
        Attempts to set kick/ban footer to string passed in
        """
        if not footer_string:
            local_embed = discord.Embed(
                title=f'No string detected, I need a string parameter to work',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        success = await self.bot.pg_utils.set_ban_footer(
            ctx.guild.id,
            footer_string,
            self.bot.logger
        )
        if success:
            desc = footer_string.replace(
                f'%user%', ctx.message.author.mention)
            local_embed = discord.Embed(
                title=f'Footer message set:',
                description=f'**Preview:**',
                color=0x419400
            )
            local_embed.set_footer(text=desc)
        else:
            local_embed = discord.Embed(
                title=f'Internal error occured, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)
        return

    @footer.command(name='set_kick')
    async def set_kick_footer(self, ctx, *, footer_string):
        """
        Attempts to set kick/ban footer to string passed in
        """
        if not footer_string:
            local_embed = discord.Embed(
                title=f'No string detected, I need a string parameter to work',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        success = await self.bot.pg_utils.set_kick_footer(
            ctx.guild.id,
            footer_string,
            self.bot.logger
        )
        if success:
            desc = footer_string.replace(
                f'%user%', ctx.message.author.mention)
            local_embed = discord.Embed(
                title=f'Footer message set:',
                description=f'**Preview:**',
                color=0x419400
            )
            local_embed.set_footer(text=desc)
        else:
            local_embed = discord.Embed(
                title=f'Internal error occured, please contact @dashwav#7785',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)
        return

    @commands.command()
    @checks.has_permissions(manage_messages=True)
    async def purge(self, ctx, *args,  mentions=None):
        """
        Purges a set number of messages.
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        deleted = []
        try:
            count = int(next(iter(args or []), 'fugg'))
        except ValueError:
            count = 100
        mentions = ctx.message.mentions
        await ctx.message.delete()
        if mentions:
            for user in mentions:
                try:
                    deleted += await ctx.channel.purge(
                        limit=count,
                        check=lambda x: x.author == user
                    )
                except discord.Forbidden as e:
                    return await ctx.send(
                        'I do not have sufficient permissions to purge.')
                except Exception as e:
                    self.bot.logger.warning(f'Error purging messages: {e}')
        else:
            try:
                deleted += await ctx.channel.purge(limit=count)
            except discord.Forbidden as e:
                return await ctx.send(
                    'I do not have sufficient permissions to purge.')
            except Exception as e:
                    self.bot.logger.warning(f'Error purging messages: {e}')

    @commands.command()
    @checks.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *,
                   reason: ActionReason = None):
        """
        Kicks a user.
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        if reason is None:
                await ctx.send(
                    "You need to supply a reason, try again.",
                    delete_after=5)
                return
        confirm = await helpers.confirm(ctx, member, reason)
        if confirm:
            embed = await self.create_embed('Kick', ctx.guild, ctx.guild.id, reason)
            try:
                try:
                    await member.create_dm()
                    await member.dm_channel.send(embed=embed)
                except Exception as e:
                    self.bot.logger.warning(f'Error messaging user!: {e}')
                await member.kick(reason=f'by: {ctx.author} for: {reason}')
                await ctx.send('\N{OK HAND SIGN}', delete_after=3)
            except Exception as e:
                self.bot.logger.warning(f'Error kicking user!: {e}')
                await ctx.send('❌', delete_after=3)
                return
            if self.bot.server_settings[ctx.guild.id]['modlog_enabled']:
                try:
                    local_embed = embeds.KickEmbed(member, ctx.author, reason)
                    mod_logs = await self.bot.pg_utils.get_modlogs(
                            ctx.guild.id)
                    for channel_id in mod_logs:
                        await (self.bot.get_channel(channel_id)).send(
                            embed=local_embed)
                except Exception as e:
                    self.bot.logger.warning(f'Issue posting to mod log: {e}')
        else:
            await ctx.send("Cancelled kick", delete_after=3)

    @commands.command()
    @checks.has_permissions(ban_members=True)
    async def ban(self, ctx, member_id: MemberID, *,
                  reason: ActionReason = None):
        """
        Bans a user.
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        if reason is None:
                await ctx.send(
                    "You need to supply a reason, try again.",
                    delete_after=5)
                return
        member = await self.bot.get_user_info(member_id)
        confirm = await helpers.confirm(ctx, member, reason)
        if confirm:
            embed = await self.create_embed('Ban', ctx.guild, ctx.guild.id, reason)
            try:
                try:
                    await member.create_dm()
                    await member.dm_channel.send(embed=embed)
                except Exception as e:
                    self.bot.logger.warning(f'Error messaging user!: {e}')
                await ctx.guild.ban(
                    discord.Object(id=member_id),
                    delete_message_days=0,
                    reason=f'by: {ctx.author} for: {reason}')
                await ctx.send('\N{OK HAND SIGN}', delete_after=3)
            except Exception as e:
                self.bot.logger.warning(f'Error banning user!: {e}')
                await ctx.send('❌', delete_after=3)
                return
            if self.bot.server_settings[ctx.guild.id]['modlog_enabled']:
                try:
                    local_embed = embeds.BanEmbed(member, ctx.author, reason)
                    mod_logs = await self.bot.pg_utils.get_modlogs(
                            ctx.guild.id)
                    for channel_id in mod_logs:
                        await (self.bot.get_channel(channel_id)).send(
                            embed=local_embed)
                except Exception as e:
                    self.bot.logger.warning(f'Issue posting to mod log: {e}')
        else:
            await ctx.send("Cancelled ban", delete_after=3)

    @commands.command()
    @checks.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *,
                    reason: ActionReason = None):
        """
        Unbans a user.
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        if reason is None:
                await ctx.send(
                    "You need to supply a reason, try again.",
                    delete_after=5)
                return
        confirm = await helpers.confirm(ctx, member.user, reason)
        if confirm:
            try:
                await ctx.guild.unban(
                    member.user,
                    reason=f'by: {ctx.author} for: {reason}')
                await ctx.send('\N{OK HAND SIGN}', delete_after=3)
            except Exception as e:
                self.bot.logger.warning(f'Error unbanning user!: {e}')
                await ctx.send('❌', delete_after=3)
                return
            self.bot.logger.info(f'Successfully unbanning {member}')
            if self.bot.server_settings[ctx.guild.id]['modlog_enabled']:
                try:
                    local_embed = embeds.UnBanEmbed(member.user, ctx.author, reason)
                    mod_logs = await self.bot.pg_utils.get_modlogs(
                            ctx.guild.id)
                    for channel_id in mod_logs:
                        await (self.bot.get_channel(channel_id)).send(
                            embed=local_embed)
                except Exception as e:
                    self.bot.logger.warning(f'Issue posting to mod log: {e}')
        else:
            await ctx.send("Cancelled unban", delete_after=3)

    async def create_embed(self, command_type, server_name, server_id, reason):
        try:
            embed = discord.Embed(title=f'❗ {command_type} Reason ❗', type='rich')
            footer = 'This is an automated message'
            if command_type.lower() == 'ban':
                command_type = 'bann'
                footer = await self.bot.pg_utils.get_ban_footer(
                    server_id,
                    self.bot.logger)
            elif command_type.lower() == 'kick':
                footer = await self.bot.pg_utils.get_kick_footer(
                    server_id,
                    self.bot.logger)
            elif command_type.lower() == 'unban':
                command_type = 'unbann'
            embed.description = f'\nYou were {command_type.lower()}ed '\
                                f'from **{server_name}**.'
            embed.add_field(name='Reason:', value=reason)
            embed.set_footer(text=footer)
            return embed
        except Exception as e:
            self.bot.logger.warning(f'Error creating embed for {command_type.lower()}: {e}')
        


def setup(bot):
    bot.add_cog(Moderation(bot))
