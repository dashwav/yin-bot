"""General purpose discord bot with a focus on doing moderation simply and well."""  # noqa

import subprocess
import datetime
from time import time, sleep

import yappi
import gila
import discord
from logging import Formatter, StreamHandler, getLogger
from discord.ext.commands import Bot

from cogs.utils.db_utils import PostgresController
from cogs.utils import embeds


class Yinbot(Bot):
    """Actual bot class."""

    def __init__(self, config, logger,
                 pg_utils: PostgresController,
                 server_settings: dict, blacklist: list = []):
        """Init for bot class."""
        try:
            self.commit = f"-{subprocess.check_output(['git', 'describe', '--always']).strip().decode()}"  # noqa
        except Exception:
            self.commit = ''
        file = open('.version', 'r')
        self.version = file.read()
        self.pg_utils = pg_utils
        self.server_settings = {}
        self.start_time = int(time())
        self.botcogs = [x.lower() for x in config['cogs']]
        self.credentials = config['token']
        self.guild_id = config['guild_id']
        self.bot_owner_id = config['owner_id']
        self.base_voice = config['base_voice']
        self.logger = logger
        self.blchannels = blacklist

        intents = discord.Intents.default()
        if config.get("prod"):
            intents.members = True
            intents.presences = False
        super().__init__(
            command_prefix=self.get_pre,
            case_insensitive=True,
            intents=intents,
        )

    @classmethod
    async def get_instance(cls):
        """Async method to initialize the pg_utils class."""
        config = gila.Gila()
        config.set_default("log_level", "INFO")
        config.set_config_file('config/config.yml')
        config.read_config_file()
        config = config.all_config()
        logger = getLogger('yinbot')
        console_handler = StreamHandler()
        console_handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s %(name)s: %(message)s')
        )
        logger.addHandler(console_handler)
        logger.setLevel(config.get("log_level"))
        postgres_cred = config.get("postgres_credentials")
        pg_utils = None
        while not pg_utils:
            try:
                pg_utils = await PostgresController.get_instance(
                    logger=logger, connect_kwargs=postgres_cred)
            except Exception as e:
                logger.critical(
                    'Error initializing DB - trying again in 5 seconds')
                logger.debug(f'Error: {e}')
                sleep(5)
        server_settings = await pg_utils.get_server_settings()
        blchannels = await pg_utils.get_all_blacklist_channels()
        return cls(config, logger, pg_utils, server_settings, blchannels)

    async def get_pre(self, bot, message):
        """Gather Prefix."""
        try:
            return self.server_settings[message.guild.id]['prefix']
        except Exception as e:
            self.logger.info(f'{e}')
            return '-'

    def start_bot(self, cogs):
        """Actually start the bot."""
        self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        yappi.start()
        self.run(self.credentials)

    async def on_ready(self):
        """Gather settings."""
        try:
            self.server_settings = {}
            self.server_settings = \
                await self.pg_utils.get_server_settings()
            self.logger.info(f'\nServers: {len(self.server_settings)}')
        except Exception as e:
            self.logger.warning(f'issue getting server settings: {e}')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        self.logger.info(f'\nLogged in as\n{self.user.name} v{self.version}{self.commit}'  # noqa
                         f'\n{self.user.id}\n------')

    async def on_message(self, ctx):
        """On all messages."""
        if ctx.author.bot:
            return
        elif isinstance(ctx.guild, type(None)):
            return
        elif self.user in ctx.mentions:
            await ctx.channel.send(
                embed=embeds.MentionHelpEmbed(
                    await self.get_pre(self, ctx)
                    )
                )
        elif ctx.channel.id not in self.blchannels:
            await self.process_commands(ctx)
        else:
            permis = False
            is_owner = await self.is_owner(ctx.author)
            if is_owner:
                permis = True
            if not permis:
                resolved = ctx.channel.permissions_for(ctx.author)
                if getattr(resolved, 'administrator', None) or getattr(resolved, 'kick_members', None):  # noqa
                    permis = True
            if permis:
                await self.process_commands(ctx)
            return
        return
