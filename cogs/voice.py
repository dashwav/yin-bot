"""
Cog to handle voice role + channel creation
"""
import discord
from .utils import checks, embeds
from discord.ext import commands


class Voice():
    def __init__(self, bot):
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
    async def enable(self, ctx):
        """
        Sets voiceroles to enabled for server and creates the
        role if it doesn't exits
        """
        vcrole_enabled = await\
            self.bot.postgres_controller.get_voice_enabled(ctx.guild.id)
        if vcrole_enabled:
            local_embed = discord.Embed(
                title=f'Voice channel roles are already enabled!',
                description=' ',
                color=0x419400
            )
            await ctx.send(embed=local_embed)
            return
        vcrole = await self.bot.postgres_controller.get_voice_role(
            ctx.guild.id
        )
        vcrole_exists = False
        for role in ctx.guild.roles:
            if vcrole == role.id:
                vcrole = role
                vcrole_exists = True
        if vcrole_exists:
            await self.bot.postgres_controller.set_voice_enabled(
                ctx.guild.id, True)
            local_embed = discord.Embed(
                title=f'Voice channel roles are now enabled!',
                description=f'**Voice Role:** {vcrole.name}',
                color=0x419400
            )
            await ctx.send(embed=local_embed)
            return
        try:
            new_role = await ctx.guild.create_role(
                name=self.bot.base_voice,
            )
        except discord.Forbidden:
            local_embed = embeds.ForbiddenEmbed('voiceroles enable')
            await ctx.send(embed=local_embed)
            return
        except Exception as e:
            self.bot.logger.warning(f'Error creating role {e}')
        try:
            await self.bot.postgres_controller.set_voice_role(
                ctx.guild.id, new_role.id)
        except Exception as e:
            local_embed = embeds.InternalErrorEmbed()
            await ctx.send(embed=local_embed)
            return
        await self.bot.postgres_controller.set_voice_enabled(
            ctx.guild.id, True)
        local_embed = discord.Embed(
            title=f'Voice channel roles are now enabled!',
            description=f'**Voice Role:** {new_role.name}',
            color=0x419400
        )
        await ctx.send(embed=local_embed)

    @voiceroles.command()
    async def disable(self, ctx):
        """
        Disables voice role, and deletes role
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
        await self.bot.postgres_controller.set_voice_enabled(
            ctx.guild.id, False
        )
        vcrole = await self.bot.postgres_controller.get_voice_role(
            ctx.guild.id
        )
        vcrole_exists = False
        for role in ctx.guild.roles:
            if vcrole == role.id:
                vcrole = role
                vcrole_exists = True
        if not vcrole_exists:
            local_embed = discord.Embed(
                title=f'Voice channel roles are now disabled!',
                description=f' ',
                color=0x419400
            )
            await ctx.send(embed=local_embed)
            return
        try:
            await vcrole.delete(reason='Disabling voice+text - Yinbot')
            local_embed = discord.Embed(
                title=f'Voice channel roles are now disabled!',
                description=f'Roles deleted: {vcrole.name}',
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
        vc_role = await self.bot.postgres_controller.get_voice_role(
            member.guild.id)
        vc_role_exists = False
        for role in member.guild.roles:
            if vc_role == role.id:
                vc_role = role
                vc_role_exists = True
        if not vc_role_exists:
            return
        user_roles = member.roles
        if before.channel is None and after.channel:
            user_roles.append(vc_role)
            await member.edit(roles=user_roles)
        elif after.channel is None and before.channel:
            try:
                user_roles.remove(vc_role)
            except ValueError as e:
                pass
            await member.edit(roles=user_roles)


def setup(bot):
    bot.add_cog(Voice(bot))
