"""
This cog will be used for setting up both the welcome message for each
guild as well as the gateway channel/role
"""

import discord
from discord.ext import commands
from .utils import checks


class Gateway:

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    @checks.is_admin()
    async def welcome(self, ctx):
        """
        Welcome message command. If no subcommand is
        invoked, it will return the current welcome message
        """
        if ctx.invoked_subcommand is None:
            local_embed = discord.Embed(
                title=f'Current welcome message: '
            )