"""
Database utility functions.
"""
from datetime import datetime
from json import dumps, loads
from typing import Optional
from .enums import Change, Action
try:
    from asyncpg import Record, InterfaceError, create_pool
    from asyncpg.pool import Pool
except ImportError:
    Record = None
    Pool = None
    print('asyncpg not installed, PostgresSQL function not available.')


def parse_record(record: Record) -> Optional[tuple]:
    """
    Parse a asyncpg Record object to a tuple of values
    :param record: the asyncpg Record object
    :return: the tuple of values if it's not None, else None
    """
    try:
        return tuple(record.values())
    except AttributeError:
        return None


async def make_tables(pool: Pool, schema: str):
    """
    Make tables used for caching if they don't exist.
    :param pool: the connection pool.
    :param schema: the schema name.
    """
    await pool.execute('CREATE SCHEMA IF NOT EXISTS {};'.format(schema))

    moderation = """
    CREATE TABLE IF NOT EXISTS {}.moderation (
      serverid BIGINT,
      modid BIGINT,
      targetid BIGINT,
      action SMALLINT,
      logtime TIMESTAMP DEFAULT current_timestamp,
      PRIMARY KEY (serverid, modid, targetid, action)
    );
    """.format(schema)

    servers = """
    CREATE TABLE IF NOT EXISTS {}.servers (
      serverid BIGINT,
      assignableroles varchar ARRAY,
      filterwordswhite varchar ARRAY,
      filterwordsblack varchar ARRAY,
      blacklistchannels integer ARRAY,
      r9kchannels integer ARRAY,
      addtime TIMESTAMP DEFAULT current_timestamp,
      PRIMARY KEY (serverid)
    );""".format(schema)

    await pool.execute(moderation)
    await pool.execute(servers)


class PostgresController():
    """
    We will use the schema 'yinbot' for the db
    """
    __slots__ = ('pool', 'schema', 'logger')

    def __init__(self, pool: Pool, logger, schema: str = 'yinbot'):
        self.pool = pool
        self.schema = schema
        self.logger = logger

    @classmethod
    async def get_instance(cls, logger=None, connect_kwargs: dict = None,
                           pool: Pool = None, schema: str = 'yinbot'):
        """
        Get a new instance of `PostgresController`
        This method will create the appropriate tables needed.
        :param logger: the logger object.
        :param connect_kwargs:
            Keyword arguments for the
            :func:`asyncpg.connection.connect` function.
        :param pool: an existing connection pool.
        One of `pool` or `connect_kwargs` must not be None.
        :param schema: the schema name used. Defaults to `minoshiro`
        :return: a new instance of `PostgresController`
        """
        assert logger, (
            'Please provide a logger to the data_controller'
        )
        assert connect_kwargs or pool, (
            'Please either provide a connection pool or '
            'a dict of connection data for creating a new '
            'connection pool.'
        )
        if not pool:
            try:
                pool = await create_pool(**connect_kwargs)
                logger.info('Connection pool made.')
            except InterfaceError as e:
                logger.error(str(e))
                raise e
        logger.info('Creating tables...')
        await make_tables(pool, schema)
        logger.info('Tables created.')
        return cls(pool, logger, schema)

    async def insert_rolechange(self, server_id: int, user_id: int,
                                changetype: Change):
        """
        Inserts into the roles table a new rolechange
        :param user_id: the id of the user changed
        :param changetype: The type of change that occured
        """
        sql = """
        INSERT INTO {}.roles VALUES ($1, $2, $3);
        """.format(self.schema)

        await self.pool.execute(sql, user_id, changetype.Value)

    async def insert_modaction(self, server_id: int, mod_id: int,
                               target_id: int, action_type: Action):
        """
        Inserts into the roles table a new rolechange
        :param mod_id: the id of the mod that triggered the action
        :param target_id: the id of user that action was performed on
        :param action_type: The type of change that occured
        """
        sql = """
        INSERT INTO {}.moderation VALUES ($1, $2, $3);
        """.format(self.schema)

        await self.pool.execute(
            sql, server_id, mod_id, target_id, action_type.Value)

    async def add_server(self, server_id: int):
        """
        Inserts into the server table a new server
        :param server_id: the id of the server added
        """
        sql = """
        INSERT INTO {}.servers VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (serverid)
        DO nothing;
        """.format(self.schema)

        await self.pool.execute(sql, server_id, [], [], [], [], [])

    async def add_whitelist_word(self, server_id: int, word: str):
        """
        Adds a word that is allowed on the whitelist channels
        :param server_id: the id of the server to add the word to
        :param word: word to add
        """
        return

    async def add_message(self, message):
        """
        Adds a message to the database
        :param message: the discord message object to add
        """
        sql = """
        INSERT INTO {}.messages VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (messageid)
        DO nothing;
        """.format(self.schema)
        await self.pool.execute(
            sql,
            message.guild.id,
            message.id,
            message.author.id,
            message.channel.id,
            message.author.bot,
            message.pinned,
            message.clean_content,
            message.created_at
        )

    async def add_blacklist_word(self, server_id: int, word: str):
        """
        Adds a word that is not allowed on the server
        :param server_id: the id of the server to add the word to
        :param word: word to add
        """
        return

    async def add_whitelist_channel(self, server_id: int, channel_id: int):
        """
        Adds a channel that will delete all but the messages containing a
        string in the 'whitelist' column of the server row
        :param server_id: the id of the server to add the word to
        :param word: word to add
        """
        return

    async def add_r9k_channel(self, server_id: int, channel_id: int):
        """
        this would be a cool thing to have
        """
        return
