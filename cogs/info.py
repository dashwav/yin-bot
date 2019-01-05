"""
Cog for giving out useful info: bot invite link, stats, ping, etc
"""
import discord
import datetime
from .utils import embeds
from discord.ext import commands

DISCORD = 'https://discordapp.com/invite/svU3Mdd'


class Info():

    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @commands.command()
    async def invite(self, ctx):
        """
        Prints out a clickable link to invite yin
        """
        await ctx.send(embed=embeds.InviteEmbed())

    @commands.command()
    async def uptime(self, ctx):
        """
        Prints out uptime of bot
        """
        now = datetime.datetime.utcnow()
        uptime = now - self.bot.uptime
        await ctx.send(f'Uptime: {uptime}')

    @commands.command()
    async def support(self, ctx):
        """
        Links support server
        """
        await ctx.send(embed=embeds.SupportEmbed())

    @commands.command()
    async def stats(self, ctx):
        """
        Prints out stats embed
        """
        now = datetime.datetime.utcnow()
        uptime = now - self.bot.uptime
        total_servers = len(self.bot.guilds)
        total_users = len(self.bot.users)
        version_number = self.bot.version
        local_embed = discord.Embed(
            title=f'__Stats__',
            description=f'Total Servers: {total_servers}\n'
                        f'Total Users: {total_users}\n'
                        f'Uptime: {uptime}\n'
        )
        local_embed.set_footer(text=f'yinbot v{version_number}')
        await ctx.send(embed=local_embed)
