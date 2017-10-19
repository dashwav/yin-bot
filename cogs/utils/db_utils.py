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
      prefix varchar(2),
      modlog_enabled boolean DEFAULT FALSE,
      modlog_channels bigint ARRAY,
      assignableroles bigint ARRAY,
      filterwordswhite varchar ARRAY,
      filterwordsblack varchar ARRAY,
      blacklistchannels bigint ARRAY,
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

    async def insert_modaction(self, guild_id: int, mod_id: int,
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
            sql, guild_id, mod_id, target_id, action_type.Value)

    async def add_server(self, guild_id: int):
        """
        Inserts into the server table a new server
        :param guild_id: the id of the server added
        """
        sql = """
        INSERT INTO {}.servers VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (serverid)
        DO nothing;
        """.format(self.schema)

        await self.pool.execute(
            sql, guild_id, '-', False, [], [], [], [], [], [])

    async def get_server_settings(self):
        """
        Returns the custom prefix for the server
        """
        prefix_dict = {}
        sql = """
        SELECT serverid, prefix, modlog_enabled FROM {}.servers;
        """.format(self.schema)
        val_list = await self.pool.fetch(sql)
        for row in val_list:
            print(row)
            prefix_dict[row['serverid']] = {
                'prefix': row['prefix'],
                'modlog_enabled': row['modlog_enabled']
                }
        return prefix_dict

    async def add_whitelist_word(self, guild_id: int, word: str):
        """
        Adds a word that is allowed on the whitelist channels
        :param guild_id: the id of the server to add the word to
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

    async def add_blacklist_word(self, guild_id: int, word: str):
        """
        Adds a word that is not allowed on the server
        :param guild_id: the id of the server to add the word to
        :param word: word to add
        """
        return

    async def add_whitelist_channel(self, guild_id: int, channel_id: int):
        """
        Adds a channel that will delete all but the messages containing a
        string in the 'whitelist' column of the server row
        :param guild_id: the id of the server to add the word to
        :param word: word to add
        """
        return

    async def add_r9k_channel(self, guild_id: int, channel_id: int):
        """
        this would be a cool thing to have
        """
        return

    async def is_role_assignable(self, guild_id: int, role_id: int):
        """
        Checks to see if a role is in a servers auto assignable roles list
        :param guild_id: guild to look in
        :param role_id: role to check
        """
        sql = """
        SELECT * FROM {}.servers
        WHERE serverid = $1
        AND assignableroles @> $2;
        """.format(self.schema)

        row = await self.pool.fetchrow(sql, guild_id, [role_id])
        return True if row else False

    async def add_assignable_role(self, guild_id: int, role_id: int, logger):
        """
        Adds a role to the assignable roles array for the server
        :param guild_id: guild to add role to
        :param role_id: role to add
        """
        sql = """
        UPDATE {}.servers
        SET assignableroles = (SELECT array_agg(distinct e)
        FROM unnest(array_append(assignableroles,$1::bigint)) e)
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, role_id, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding role to server {guild_id}: {e}')
            return False

    async def remove_assignable_role(self, guild_id: int, role_id: int, logger):
        """
        Removes a role from the assignable roles array for the server
        :param guild_id: guild to remove role from
        :param role_id: role to remove
        """
        role_list = await self.get_assignable_roles(guild_id)
        role_list.remove(role_id)
        sql = """
        UPDATE {}.servers SET assignableroles = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, role_list, guild_id)
        except Exception as e:
            logger.warning(f'Error removing roles: {e}')
            return False
        return True

    async def get_assignable_roles(self, guild_id: int):
        """
        returns a list of assignable roles array for the server
        :param guild_id: guild to remove role from
        """
        sql = """
        SELECT assignableroles FROM {}.servers
        WHERE serverid = $1;
        """.format(self.schema)
        role_list = await self.pool.fetchval(sql, guild_id)
        return role_list

    async def add_modlog_channel(self, guild_id: int, channel_id: int, logger):
        """
        Adds a channel to the modlog channel array for the server
        :param guild_id: guild to add channel to
        :param channel_id: channel to add
        """
        sql = """
        UPDATE {}.servers
        SET modlog_channels = (SELECT array_agg(distinct e)
        FROM unnest(array_append(modlog_channels,$1::bigint)) e)
        WHERE serverid = $2;
        """.format(self.schema)
        boolsql = """
        UPDATE {}.servers
        SET modlog_enabled = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            await self.pool.execute(boolsql, True, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_modlog_channel(self, guild_id: int, channel_id: int, logger):
        """
        Removes a channel from the modlog array
        :param guild_id: guild to remove modlog channel from
        :param channel_id: channel id to remove
        """
        channel_list = await self.get_modlogs(guild_id)
        channel_list.remove(channel_id)
        sql = """
        UPDATE {}.servers
        SET modlog_channels = $1
        WHERE serverid = $2;
        """.format(self.schema)
        boolsql = """
        UPDATE {}.servers
        SET modlog_enabled = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_list, guild_id)
            if not channel_list:
                await self.pool.execute(boolsql, False, guild_id)
        except Exception as e:
            logger.warning(f'Error removing modlog channel: {e}')
            return False
        return True

    async def get_modlogs(self, guild_id: int):
        """
        Returns a list of channel ids for posting mod actions
        :param guild_id: guild to search roles for
        """
        sql = """
        SELECT modlog_channels FROM {}.servers
        WHERE serverid = $1;
        """.format(self.schema)
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def set_prefix(self, guild_id: int, prefix: str, logger):
        """
        Sets the command prefix for the server
        :param guild_id: guild to set prefix for
        :param prefix: prefix to set, limit 2 chars
        """
        sql = """
        UPDATE {}.servers
        SET prefix = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, prefix, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error setting prefix for {guild_id}: {e}')
            return False


