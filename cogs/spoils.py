"""
A cog that handles posting a large embed to block out spoils.
"""
import discord
import asyncio
from datetime import datetime, timedelta
from discord.ext import commands
from .utils import checks


class Spoils():
    """
    Class that creates a task to run every minute and check for
    time since last post
    """
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.wait_time = bot.wait_time
        self.embed = discord.Embed(title='Clear Spoilers', type='rich')
        description = '👻 👻 👻\_\_\_👻 👻 👻'
        for i in range(1, 64):
            description += '\n '
        description += '\_\_\_\n👻 👻 👻 *Spooooky* Spoilers above 👻 👻 👻'
        self.embed.description = description
        # create the background task and run it in the background
        try:
            self.bg_task = self.bot.loop.create_task(self.my_background_task())
        except Exception as e:
            self.log.warning(f"Error starting task {e}")

    @commands.command()
    @checks.has_permissions(manage_roles=True)
    async def tenfeettaller(self, ctx):
        try:
            await ctx.send(embed=self.embed)
            await ctx.message.delete()
        except Exception as e:
            self.bot.logger.warning(f'Issue building wall: {e}')

    @commands.command()
    @checks.has_permissions(manage_roles=True)
    async def wall(self, ctx):
        try:
            await ctx.send(embed=self.embed)
            await ctx.message.delete()
        except Exception as e:
            self.bot.logger.warning(f'Issue building wall: {e}')

    async def my_background_task(self):
        await self.bot.wait_until_ready()
        self.bot.logger.info("Starting spoiler task")
        while not self.bot.is_closed():
            for channel_id in self.bot.spoiler_channels:
                try:
                    channel = self.bot.get_channel(channel_id)
                except Exception as e:
                    self.bot.logger.warning(
                        f'Error getting channel {channel_id}: {e}')
                if channel:
                    async for message in channel.history(limit=1):
                        if not message.author.bot:
                            last_post = datetime.utcnow() - message.created_at
                            if last_post > timedelta(seconds=self.wait_time):
                                try:
                                    await channel.send(embed=self.embed)
                                except Exception as e:
                                    self.bot.logger.warning(
                                        f'Error posting to channel'
                                        f' {channel_id}: {e}')
                else:
                    self.bot.logger.warning(
                        f'Couldn\'t find channel: {channel_id}: {e}')
            await asyncio.sleep(60)
