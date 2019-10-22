"""Cog for giving out useful info: bot invite link, stats, ping, etc."""
import discord
import datetime
from discord.ext import commands
from .utils import embeds

DISCORD = 'https://discordapp.com/invite/svU3Mdd'


class Info(commands.Cog):
    """Cog for general info."""

    def __init__(self, bot):
        """Init method."""
        self.bot = bot
        super().__init__()

    @commands.command()
    async def invite(self, ctx):
        """Print out a clickable link to invite yin."""
        await ctx.send(embed=embeds.InviteEmbed())

    @commands.command()
    async def uptime(self, ctx):
        """Print out uptime of bot."""
        now = datetime.datetime.utcnow()
        uptime = now - self.bot.uptime
        await ctx.send(f'Uptime: {uptime}')

    @commands.command()
    async def support(self, ctx):
        """Link support server."""
        await ctx.send(embed=embeds.SupportEmbed())

    @commands.command()
    async def stats(self, ctx):
        """Print out stats embed."""
        now = datetime.datetime.utcnow()
        uptime = now - self.bot.uptime
        total_servers = len(self.bot.guilds)
        total_users = len(self.bot.users)
        version_number = self.bot.version
        commit = self.bot.commit
        local_embed = discord.Embed(
            title=f'__Stats__',
            description=f'Total Servers: {total_servers}\n'
                        f'Total Users: {total_users}\n'
                        f'Uptime: {uptime}\n'
        )
        local_embed.set_footer(text=f'yinbot v{version_number}{commit}')
        await ctx.send(embed=local_embed)


def setup(bot):
    """General cog loading."""
    bot.add_cog(Info(bot))
