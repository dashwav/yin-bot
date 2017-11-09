"""
Cog to handle voice role + channel creation
"""
import discord
from .utils import checks, embeds
from discord.ext import commands


class Voice():
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.logger = bot.logger

    @commands.group(aliases=['vcrole'])
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def voiceroles(self, ctx):
        """
        Returns whether voice_roles are enabled for the server
        """
        if ctx.invoked_subcommand is None:
            desc = ''
            vcrole_enabled = await\
                self.bot.postgres_controller.get_voice_enabled(ctx.guild.id)
            desc = 'Enabled' if vcrole_enabled else 'Disabled'
            local_embed = discord.Embed(
                title=f'Voice channel roles are:',
                description=f'**{desc}**',
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @voiceroles.command()
    async def add(self, ctx, *, role_name):
        """
        Sets voiceroles to enabled for server and creates the
        role if it doesn't exits
        """
        if ctx.author.voice.channel is None:
            local_embed = discord.Embed(
                title=f'You must be in a voice channel to use this command',
                description=f' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        voice_channel = ctx.author.voice.channel
        if not role_name:
            local_embed = discord.Embed(
                title=f'Please input a role name!',
                description=f'`voiceroles add rolename`',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        found_role = None
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if not found_role:
            local_embed = discord.Embed(
                title=f'Couldn\'t find role {role_name}',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        try:
            await self.bot.postgres_controller.add_role_channel(
                ctx.guild.id, voice_channel.id, found_role.id)
        except Exception as e:
            self.bot.logger.warning(f'Error adding role/channel: {e}')
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
            return
        vcroles_enabled = await\
            self.bot.postgres_controller.get_voice_enabled(ctx.guild.id)
        if not vcroles_enabled:
            await self.bot.postgres_controller.set_voice_enabled(
                ctx.guild.id, True)
        local_embed = discord.Embed(
            title=f'Added voice role to channel',
            description=f'**Voice Role:** {found_role .name}\n'
                        f'**Channel:** {voice_channel.name}',
            color=0x419400
        )
        await ctx.send(embed=local_embed)

    @voiceroles.command()
    async def remove(self, ctx, *, role_name):
        """
        Removes the given role from the voice channel.
        """
        if ctx.author.voice.channel is None:
            local_embed = discord.Embed(
                title=f'You must be in a voice channel to use this command',
                description=f' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        voice_channel = ctx.author.voice.channel
        if not role_name:
            local_embed = discord.Embed(
                title=f'Please input a role name!',
                description=f'`voiceroles remove rolename`',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        found_role = None
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if not found_role:
            local_embed = discord.Embed(
                title=f'Couldn\'t find role {role_name}',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)
            return
        try:
            await self.bot.postgres_controller.rem_role_channel(
                ctx.guild.id, voice_channel.id, found_role.id, self.bot.logger)
        except Exception as e:
            self.bot.logger.warning(f'Error removing role/channel: {e}')
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
            return
        local_embed = discord.Embed(
            title=f'Removed voice role from channel',
            description=f'**Voice Role:** {found_role .name}\n'
                        f'**Channel:** {voice_channel.name}',
            color=0x419400
        )
        await ctx.send(embed=local_embed)

    @voiceroles.command()
    async def disable(self, ctx):
        """
        Disables all voice roles for server
        """
        vcrole_enabled = await\
            self.bot.postgres_controller.get_voice_enabled(ctx.guild.id)
        if not vcrole_enabled:
            local_embed = discord.Embed(
                title=f'Voice channel roles are already disabled!',
                description=' ',
                color=0x419400
            )
            await ctx.send(embed=local_embed)
            return
        try:
            await self.bot.postgres_controller.set_voice_enabled(
                ctx.guild.id, False
            )
            await self.bot.postgres_controller.purge_voice_roles(
                ctx.guild.id
            )
            local_embed = discord.Embed(
                title=f'Voice channel roles are now disabled!',
                description=f' ',
                color=0x419400
            )
            await ctx.send(embed=local_embed)
        except Exception as e:
            self.bot.logger.warning(f'Error deleting voice role: {e}')

    async def on_voice_state_update(self, member, before, after):
        """
        Checks if a user has recently joined or left a voice channel and adds
        role if necessary
        """
        vc_enabled = await self.bot.postgres_controller.get_voice_enabled(
            member.guild.id)
        if not vc_enabled:
            return
        user_roles = member.roles
        if before.channel is None and after.channel:
            vc_roles = await self.bot.postgres_controller.get_channel_roles(
                member.guild.id, after.channel.id
            )
            for vc_role in vc_roles:
                found_role = None
                for role in member.guild.roles:
                    if role.id == vc_role:
                        found_role = role
                if not found_role:
                    self.logger.warning(
                        f'Couldn\'t find {vc_role} in guild {member.guild.id}')
                    continue
                user_roles.append(found_role)
            await member.edit(roles=set(user_roles))
        elif after.channel is None and before.channel:
            vc_roles = await self.bot.postgres_controller.get_channel_roles(
                member.guild.id, before.channel.id
            )
            for vc_role in vc_roles:
                for role in user_roles:
                    if role.id == vc_role:
                        try:
                            user_roles.remove(role)
                        except ValueError as e:
                            self.logger.warning(
                                f'{vc_role} not found in {user_roles}')
            await member.edit(roles=set(user_roles))
        else:
            vc_roles = await self.bot.postgres_controller.get_channel_roles(
                member.guild.id, before.channel.id
            )
            for vc_role in vc_roles:
                for role in user_roles:
                    if role.id == vc_role:
                        try:
                            user_roles.remove(role)
                        except ValueError as e:
                            self.logger.warning(
                                f'{vc_role} not found in {user_roles}')
            vc_roles = await self.bot.postgres_controller.get_channel_roles(
                member.guild.id, after.channel.id
            )
            for vc_role in vc_roles:
                found_role = None
                for role in member.guild.roles:
                    if role.id == vc_role:
                        found_role = role
                if not found_role:
                    self.logger.warning(
                        f'Couldn\'t find {vc_role} in guild {member.guild.id}')
                    continue
                user_roles.append(found_role)
            await member.edit(roles=set(user_roles))


def setup(bot):
    bot.add_cog(Voice(bot))
