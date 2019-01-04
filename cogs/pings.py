from discord.ext import commands
from discord.utils import find
from .utils import checks, embeds


class Pings():

    def __init__(self, bot):
        """
        init for cog class
        """
        super().__init__()
        self.bot = bot

    @commands.command(aliases=['pingy', 'ping_role'])
    @commands.guild_only()
    @checks.has_permissions(manage_roles=True)
    async def ping(self, ctx, *roles: commands.clean_content):
        """
        Pings all the roles passed into the command
        """
        if not roles:
            await ctx.send(
              embed=embeds.CommandErrorEmbed(
                "Please add at least one role to ping!"),
              delete_after=3)
            await ctx.message.delete()
            return
        guild_roles = ctx.guild.roles
        found_roles = []
        for role in roles:
            guild_role = find(
              lambda m: m.name.lower() == role.lower(), guild_roles)
            if not guild_role:
                continue
            found_roles.append(guild_role)
        if not found_roles:
            await ctx.send(
              embed=embeds.CommandErrorEmbed(
                "None of the inputs match roles on guild!"),
              delete_after=3)
            await ctx.message.delete()
            return
        mention_str = ""
        for role in found_roles:
            await role.edit(mentionable=True)
            mention_str += f'{role.mention} '
        await ctx.send(mention_str)
        await ctx.message.delete()
        for role in found_roles:
            await role.edit(mentionable=False)
