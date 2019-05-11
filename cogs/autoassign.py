"""
Handling the auto assignable roles
"""

import discord
from discord.ext import commands
from .utils import checks, embeds


class Roles(commands.Cog):
    """
    Cog to handle the ability of server owners
    to create a list of roles that should be added on guild join
    """

    def __init__(self, bot):
        """
        Init class
        """
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """
        Actually adds the autoassign roles
        """
        autoassign_roles = []
        autoassign_role_ids = await \
                self.bot.pg_utils.get_autoassign_roles(ctx.guild.id)
        for role in ctx.guild.roles:
            if role.id in autoassign_role_ids:
                autoassign_roles.append(role)
        await member.add_roles(autoassign_roles)
        
    @commands.group(aliases=['aar', 'autoassign'])
    @commands.guild_only()
    @checks.admin_or_permissions(manage_roles=True)
    async def autoassignroles(self, ctx):
        """
        Manages server's autoassign roles
        """
        if ctx.invoked_subcommand is None:
            message = ' \n'
            autoassign_roles = []
            autoassign_role_ids = await \
                self.bot.pg_utils.get_autoassign_roles(ctx.guild.id)
            for role in ctx.guild.roles:
                if role.id in autoassign_role_ids:
                    autoassign_roles.append(role)
            for role in autoassign_roles:
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
        Adds a role to the servers auto-assignable roles list
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
            success = await self.bot.pg_utils.add_autoassign_role(
                ctx.guild.id, found_role.id, self.bot.logger)
            if success:
                local_embed = discord.Embed(
                    title=f'Added {found_role.name} to auto-assignable roles',
                    description=' ',
                    color=0x419400
                )
            else:
                local_embed = discord.Embed(
                    title=f'Internal error when adding {found_role.name} to '
                          'auto-assignable roles, contact @dashwav#7785',
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
        Removes a role from the serves auto-assignable roles list
        """
        found_role = None
        for role in ctx.guild.roles:
            if role.name.lower() == role_name.lower():
                found_role = role
        if found_role:
            try:
                success = await \
                    self.bot.pg_utils.remove_autoassign_role(
                        ctx.guild.id, found_role.id, self.bot.logger)
            except ValueError:
                local_embed = discord.Embed(
                    title=f'{found_role.name} is already'
                          ' not on the auto-assignable list',
                    description=' ',
                    color=0x651111
                )
                await ctx.send(embed=local_embed)
                return
            if success:
                local_embed = discord.Embed(
                    title=f'Removed {found_role.name} '
                          'from auto-assignable roles',
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
