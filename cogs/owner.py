"""Misc Owner Commands."""

import traceback
import yappi
import discord
from discord.ext import commands
from .utils import helpers


class Owner(commands.Cog):
    """Various owner commands."""

    def __init__(self, bot):
        """Init method."""
        super().__init__()
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def set_playing(self, ctx, *, game: str = None):
        """Set the playing status."""
        if game:
            await self.bot.change_presence(activity=discord.Game(game))
        ctx.delete()

    @commands.command(hidden=True)
    @commands.is_owner()
    async def change_username(self, ctx, *, new_username: str):
        """Change the bot username."""
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
        """Add a server to the db."""
        try:
            await self.bot.pg_utils.add_server(ctx.guild.id)
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
    async def auto_fix_servers(self, ctx, *, test: str = None):
        """Fix servers that are not in the database."""
        wrong_guilds = []
        for server in self.bot.guilds:
            try:
                server_settings = await self.bot.pg_utils.get_server(
                    server.id, self.bot.logger
                )
            except Exception as e:
                self.bot.logger.warning(f'Issues getting servers: {e}')
                await ctx.send('❌', delete_after=3)
            if not server_settings:
                wrong_guilds.append(server)
        if test:
            local_embed = discord.Embed(
                name='Discord Server Check',
                value=f'There are {len(wrong_guilds)} that are not '
                      'correctly represented in the database'
            )
            current_s = '----\n'
            wrong_s = '----\n'
            for key, server_s in self.bot.server_settings.items():
                current_s += f'{key}\n'
            for server in wrong_guilds:
                wrong_s += f'{server.id}\n'
            local_embed.add_field(name='current_servers', value=current_s)
            local_embed.add_field(name='wrong_servers', value=wrong_s)
            await ctx.send(embed=local_embed)
            return
        confirm = await helpers.custom_confirm(
            ctx,
            f'```This will edit {len(wrong_guilds)} in the database.'
            f'This is an irreversable action, are you sure?```'
        )
        if not confirm:
            return
        for server in wrong_guilds:
            try:
                await self.bot.pg_utils.add_server(server.id)
            except Exception as e:
                self.bot.logger.warning(f'Error adding server to db: {e}')
                await ctx.send('❌', delete_after=3)
                return
        await ctx.send('\N{OK HAND SIGN}', delete_after=3)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def echo(self, ctx, channel, *, message):
        """Echo a string into a different channel."""
        """
        :params channel: channel to echo into
        :params message: message to echo."""
        if not ctx.message.channel_mentions:
            return await ctx.send(
                f'<command> <channel mention> <message> u idiot')
        try:
            for channel in ctx.message.channel_mentions:
                await channel.send(f'{message}')
        except Exception:
            ctx.send('Error when trying to send fam')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def perf(self, ctx):
        """Print callgrind file to callgrind.out."""
        try:
            yappi.get_func_stats().save('callgrind.out', 'CALLGRIND')
            await ctx.send(":okansdf")
        except Exception as e:
            await ctx.send(f"Error doing that: {e}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, module):
        """Load a module."""
        try:
            self.bot.load_extension(module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, module):
        """Unload a module."""
        try:
            self.bot.unload_extension(module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, *, module):
        """Reload a module."""
        try:
            self.bot.unload_extension(module)
            self.bot.load_extension(module)
        except Exception:
            await ctx.send(f'```py\n{traceback.format_exc()}\n```')
        else:
            await ctx.send('\N{OK HAND SIGN}')


def setup(bot):
    """General cog loading."""
    bot.add_cog(Owner(bot))
