"""
Handling the auto assignable roles and such
"""

import discord
from discord import AuditLogAction
from discord.ext import commands
from .utils import checks, embeds
from datetime import datetime, timedelta


class Roles():
    """
    Cog to handle the ability of users to
    add roles to themselves through use of a command
    """

    def __init__(self, bot):
        """
        Init class
        """
        super().__init__()
        self.bot = bot

    @commands.command(aliases=['prunerole'])
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def cleanrole(self, ctx, *, role_name):
        """
        (Testing) Removes all members from a certain role
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        found_role = None
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if not found_role:
            await ctx.send(embed=discord.Embed(
                title='Role cleaned:',
                description=f'Successfully removed {count} users from {found_role.name}',
                color=0x419400
	    ))
            return
        count = 0
        for user in found_role.members:
            try:
                local_roles = user.roles.copy()
                local_roles.remove(found_role)
                await user.edit(roles=local_roles)
                count += 1
            except Exception as e:
                self.bot.logger.warning(f'Issue cleaning role: {e}')
        await ctx.send(embed=discord.Embed(
            title='Role cleaned:',
            description=f'Successfully removed {count} users from {found_role.name}',
            color=0x419400
	))

    @commands.command()
    @commands.guild_only()
    async def iam(self, ctx, *, role_name):
        """
        Adds self-assignable role to user
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        found_role = None
        users_roles = ctx.message.author.roles.copy()
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if found_role:
            for role in users_roles:
                if role == found_role:
                    local_embed = embeds.RoleDuplicateUserEmbed(
                        ctx.message.author, found_role.name
                    )
                    await ctx.send(embed=local_embed)
                    return
            assignable = await self.bot.pg_utils.is_role_assignable(
                ctx.guild.id, found_role.id)
            if assignable:
                users_roles.append(found_role)
                try:
                    await ctx.author.edit(roles=users_roles)
                    local_embed = embeds.SelfRoleAddedEmbed(
                        ctx.message.author, found_role.name
                    )
                    await ctx.send(embed=local_embed, delete_after=3)
                    await ctx.message.delete()
                    return
                except discord.Forbidden:
                    local_embed = embeds.ForbiddenEmbed(
                        'self-assign role'
                    )
            else:
                local_embed = embeds.SelfRoleNotAssignableEmbed(
                    found_role.name
                )
        else:
            pass
        await ctx.send(embed=local_embed)

    @commands.command()
    @commands.guild_only()
    async def iamnot(self, ctx, *, role_name):
        """
        Removes self-assignable role from user
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        found_role = None
        users_roles = ctx.message.author.roles.copy()
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role1= role
        if not found_role1:
            return
        for role in users_roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if not found_role:
            local_embed = embeds.RoleNotRemovedEmbed(
                ctx.message.author, role_name
            )
            await ctx.send(embed=local_embed)
            return
        assignable_roles = await \
            self.bot.pg_utils.get_assignable_roles(
                ctx.guild.id)
        if found_role.id in assignable_roles:
            users_roles.remove(found_role)
            await ctx.message.author.edit(roles=users_roles)
            local_embed = embeds.SelfRoleRemovedEmbed(
                ctx.message.author, found_role.name
            )
            await ctx.send(embed=local_embed, delete_after=5)
            await ctx.message.delete()
        else:
            local_embed = embeds.SelfRoleNotAssignableEmbed(
                role_name
            )
            await ctx.send(embed=local_embed)

    @commands.group(aliases=['ar'])
    @commands.guild_only()
    @checks.admin_or_permissions(manage_roles=True)
    async def assignableroles(self, ctx):
        """
        manages servers assignable roles
        """
        if not await checks.is_channel_blacklisted(self,ctx):
            return
        if ctx.invoked_subcommand is None:
            message = ' \n'
            assignable_roles = []
            assignable_role_ids = await \
                self.bot.pg_utils.get_assignable_roles(ctx.guild.id)
            for role in ctx.guild.roles:
                if role.id in assignable_role_ids:
                    assignable_roles.append(role)
            for role in assignable_roles:
                message += f'{role.name}\n'
            local_embed = discord.Embed(
                title='Current self-assignable roles:',
                description=message,
                color=0x419400
            )
            await ctx.send(embed=local_embed)

    @assignableroles.command()
    async def add(self, ctx, *, role_name):
        """
        Adds a role to the servers assignable roles list
        """
        found_role = None
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if found_role:
            if not ctx.message.author.\
                    top_role >= found_role:
                local_embed = discord.Embed(
                    title=f'You can\'t add a role that is a higher '
                          'level than your highest role',
                    description=' ',
                    color=0x651111
                )
                await ctx.send(embed=local_embed)
                return
            success = await self.bot.pg_utils.add_assignable_role(
                ctx.guild.id, found_role.id, self.bot.logger)
            if success:
                local_embed = discord.Embed(
                    title=f'Added {found_role.name} to self-assignable roles',
                    description=' ',
                    color=0x419400
                )
            else:
                local_embed = discord.Embed(
                    title=f'Internal error when adding {found_role.name} to '
                          'self-assignable roles, contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
        else:
            local_embed = discord.Embed(
                title=f'Couldn\'t find role {role_name}',
                description=' ',
                color=0x651111
            )
        await ctx.send(embed=local_embed)

    @assignableroles.command()
    async def remove(self, ctx, *, role_name):
        """
        Removes a role from the serves assignable roles list
        """
        found_role = None
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if found_role:
            try:
                success = await \
                    self.bot.pg_utils.remove_assignable_role(
                        ctx.guild.id, found_role.id, self.bot.logger)
            except ValueError:
                local_embed = discord.Embed(
                    title=f'{found_role.name} is already'
                          ' not on the self-assignable list',
                    description=' ',
                    color=0x651111
                )
                await ctx.send(embed=local_embed)
                return
            if success:
                local_embed = discord.Embed(
                    title=f'Removed {found_role.name} '
                          'from self-assignable roles',
                    description=' ',
                    color=0x419400
                )
            else:
                local_embed = discord.Embed(
                    title=f'Internal error occured,'
                          ' please contact @dashwav#7785',
                    description=' ',
                    color=0x651111
                )
            await ctx.send(embed=local_embed)
        else:
            local_embed = discord.Embed(
                title=f'Couldn\'t find role {role_name}',
                description=' ',
                color=0x651111
            )
            await ctx.send(embed=local_embed)


def setup(bot):
    bot.add_cog(Roles(bot))
