"""
Handling the auto assignable roles and such
"""

import discord
from discord.ext import commands
from .utils import checks


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

    @commands.command()
    @commands.guild_only()
    async def iam(self, ctx, rolename):
        found_role = None
        users_roles = ctx.message.author.roles
        for role in users_roles:
            if role.name == rolename:
                return await ctx.send(
                    f'You already have the {rolename} role.')
        for role in ctx.guild.roles:
            if role.name == rolename:
                found_role = role
        if found_role:
            assignable = await self.bot.postgres_controller.is_role_assignable(
                ctx.guild.id, found_role.id)
            if assignable:
                users_roles.append(found_role)
                try:
                    await ctx.author.edit(roles=users_roles)
                except discord.Forbidden:
                    await ctx.send(
                        f'I don\'t have the necessary permissions to do this.')
            else:
                ctx.send(
                    f'{rolename} is not a self-assignable role.'
                )

    @commands.group(aliases=['ar'])
    @commands.guild_only()
    @checks.admin_or_permissions(manage_roles=True)
    async def assignableroles(self, ctx):
        """
        manages servers assignable roles
        """
        if ctx.invoked_subcommand is None:
            message = ' \n'
            assignable_roles = []
            assignable_role_ids = await \
                self.bot.postgres_controller.get_assignable_roles(ctx.guild.id)
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
    async def add(self, ctx, role_name):
        """
        Adds a role to the servers assignable roles list
        """
        found_role = None
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if found_role:
            await self.bot.postgres_controller.add_assignable_role(
                ctx.guild.id, found_role.id)
        else:
            ctx.send(f'Couldn\'t find a role with that name')

    @assignableroles.command()
    async def remove(self, ctx, role_name):
        """
        Removes a role from the serves assignable roles list
        """
        found_role = None
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if found_role:
            await self.bot.postgres_controller.remove_assignable_role(
                ctx.guild.id, found_role.id)
        else:
            ctx.send(f'Couldn\'t find a role with that name')
