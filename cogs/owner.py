"""
Misc commands that I want to run
"""
import traceback
import discord
from discord.ext import commands


class Owner():
    """
    Cog with misc owner commands
    """

    def __init__(self, bot):
        """
        init for cog class
        """
        super().__init__()
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def set_playing(self, ctx, *, game=None):
        if game:
            await self.bot.change_presence(game=discord.Game(name=game))
        ctx.delete()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def change_username(self, ctx, *, new_username: str):
        """
        Changes bot username
        """
        bot_user = self.bot.user
        try:
            await bot_user.edit(username=new_username)
            await ctx.send('\N{OK HAND SIGN}', delete_after=3)
        except Exception as e:
            await ctx.send('❌', delete_after=3)
            self.bot.logger.warning(f'Error changing bots username: {e}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def add_server(self, ctx):
        """
        Adds a server to the db
        """
        try:
            await self.bot.postgres_controller.add_server(ctx.guild.id)
            self.bot.server_settings[ctx.guild.id] = {
                'prefix': '-',
                'modlog_enabled': False
            }
            await ctx.send('\N{OK HAND SIGN}', delete_after=3)
            await ctx.message.delete()
        except Exception as e:
            await ctx.send('❌', delete_after=3)
            self.bot.logger.warning(f'Error adding server to db: {e}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def echo(self, ctx, channel, *, message):
        """
        Echoes a string into a different channel
        :params channel: channel to echo into
        :params message: message to echo
        """
        if not ctx.message.channel_mentions:
            return await ctx.send(
                f'<command> <channel mention> <message> u idiot')
        try:
            for channel in ctx.message.channel_mentions:
                await channel.send(f'{message}')
        except Exception as e:
            ctx.send('Error when trying to send fam')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception as e:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')
