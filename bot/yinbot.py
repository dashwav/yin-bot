"""
General purpose discord bot with a focus on doing moderation simply and well
"""
import yaml
import datetime
from discord.ext.commands import Bot
from time import time
from logging import Formatter, INFO, StreamHandler, getLogger
from cogs.utils.db_utils import PostgresController


class Yinbot(Bot):
    """
    actual bot class
    """
    def __init__(self, config, logger,
                 postgres_controller: PostgresController,
                 server_settings: dict):
        """
        init for bot class
        """
        self.postgres_controller = postgres_controller
        self.server_settings = {}
        self.start_time = int(time())
        self.credentials = config['token']
        self.guild_id = config['guild_id']
        self.bot_owner_id = config['owner_id']
        self.mod_log = config['mod_log']
        self.wait_time = config['default_wait_time']
        self.logger = logger
        super().__init__(command_prefix=self.get_pre)

    @classmethod
    async def get_instance(cls):
        """
        async method to initialize the postgres_controller class
        """
        with open("config/config.yml", 'r') as yml_config:
            config = yaml.load(yml_config)
        logger = getLogger('yinbot')
        console_handler = StreamHandler()
        console_handler.setFormatter(Formatter(
            '%(asctime)s %(levelname)s %(name)s: %(message)s')
        )
        logger.addHandler(console_handler)
        logger.setLevel(INFO)
        postgres_cred = config['postgres_credentials']
        postgres_controller = await PostgresController.get_instance(
            logger=logger, connect_kwargs=postgres_cred)
        server_settings = await postgres_controller.get_server_settings()
        return cls(config, logger, postgres_controller, server_settings)

    async def get_pre(self, bot, message):
        try:
            return self.server_settings[message.guild.id]['prefix'] 
        except Exception as e:
            self.logger.info(f'{e}')
            return '-'

    def start_bot(self, cogs):
        """
        actually start the bot
        """
        for cog in cogs:
            self.add_cog(cog)
        self.run(self.credentials)

    async def on_ready(self):
        try:
            self.server_settings = {}
            self.server_settings = \
                await self.postgres_controller.get_server_settings()
            self.logger.info(f'{self.server_settings}')
        except Exception as e:
            self.logger.warning(f'issue getting server settings: {e}')
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        self.logger.info(f'\nLogged in as\n{self.user.name}'
                         f'\n{self.user.id}\n------')
