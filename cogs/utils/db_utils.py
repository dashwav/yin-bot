"""
Database utility functions.
"""
from typing import Optional
from .enums import Action
import datetime

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

    vplust = f"""
    CREATE TABLE IF NOT EXISTS {schema}.roles (
        serverid BIGINT references {schema}.servers(serverid),
        roleid BIGINT,
        channels BIGINT ARRAY,
        PRIMARY KEY(roleid)
    );"""

    servers = f"""
    CREATE TABLE IF NOT EXISTS {schema}.servers (
      serverid BIGINT,
      prefix varchar(2),
      voice_enabled boolean DEFAULT FALSE,
      invites_allowed boolean DEFAULT TRUE,
      voice_logging boolean DEFAULT FALSE,
      voice_channels bigint ARRAY,
      modlog_enabled boolean DEFAULT FALSE,
      modlog_channels bigint ARRAY,
      welcome_message text,
      welcome_channels bigint ARRAY,
      logging_enabled boolean DEFAULT FALSE,
      logging_channels bigint ARRAY,
      assignableroles bigint ARRAY,
      blacklist_channels bigint ARRAY,
      ban_footer text,
      kick_footer text,
      addtime TIMESTAMP DEFAULT current_timestamp,
      PRIMARY KEY (serverid)
    );"""

    warnings = f"""
    CREATE TABLE IF NOT EXISTS {schema}.warnings(
      serverid BIGINT,
      userid BIGINT,
      indexid INT,
      reason text,
      major BOOLEAN DEFAULT FALSE,
      logtime TIMESTAMP DEFAULT current_timestamp,
      PRIMARY KEY (serverid, userid, indexid)
    );"""

    moderation = f"""
    CREATE TABLE IF NOT EXISTS {schema}.moderation (
      serverid BIGINT,
      moderatorid BIGINT,
      userid BIGINT,
      indexid INT,
      action INT,
      reason text,
      logtime TIMESTAMP DEFAULT current_timestamp,
      PRIMARY KEY (serverid, userid, indexid)
    );"""

    slowchannels = f"""
    CREATE TABLE IF NOT EXISTS {schema}.slowmode (
      serverid BIGINT,
      channelid BIGINT,
      interval INT,
      logtime TIMESTAMP DEFAULT current_timestamp,
      PRIMARY KEY (serverid, channelid)
    );"""

    await pool.execute(servers)
    await pool.execute(vplust)
    await pool.execute(warnings)
    await pool.execute(moderation)
    await pool.execute(slowchannels)


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

    async def add_server(self, guild_id: int):
        """
        Inserts into the server table a new server
        :param guild_id: the id of the server added
        """
        sql = """
        INSERT INTO {}.servers VALUES
        ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15, $16, $17)
        ON CONFLICT (serverid)
        DO nothing;
        """.format(self.schema)

        await self.pool.execute(
            sql,
            guild_id,
            '-',
            False,
            True,
            False,
            [],
            False,
            [],
            f'Welcome %user%!',
            [],
            False,
            [],
            [],
            [],
            f'This is an automated message',
            f'This is an automated message',
            datetime.datetime.now()
            )

    async def get_server_settings(self):
        """
        Returns the custom prefix for the server
        """
        prefix_dict = {}
        sql = """
        SELECT serverid, prefix, modlog_enabled,
        logging_enabled, invites_allowed
        FROM {}.servers;
        """.format(self.schema)
        val_list = await self.pool.fetch(sql)
        for row in val_list:
            print(row)
            prefix_dict[row['serverid']] = {
                'prefix': row['prefix'],
                'modlog_enabled': row['modlog_enabled'],
                'logging_enabled': row['logging_enabled'],
                'invites_allowed': row['invites_allowed']
                }
        return prefix_dict

    async def get_server(self, server_id: int, logger):
        """
        Returns all server settings
        :param server_id: server to find info on
        """
        sql = """
        SELECT * FROM {}.servers
        WHERE serverid = $1
        """.format(self.schema)
        try:
            return await self.pool.fetchrow(sql, server_id)
        except Exception as e:
            logger.warning(f'Error getting server settings {e}')
            return False

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

    async def remove_assignable_role(
            self, guild_id: int, role_id: int, logger):
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

    async def set_welcome_message(self, guild_id: int, message: str, logger):
        """
        Sets the welcome message for a server
        :param guild_id: Guild to update message for
        :param message: string to insert
        """
        sql = """
        UPDATE {}.servers
        SET welcome_message = $1
        WHERE serverid = $2
        """.format(self.schema)

        try:
            await self.pool.execute(sql, message, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Issue setting welcome_message: {e}')
            return False

    async def get_welcome_message(self, guild_id: int, logger):
        """
        Returns the welcome message string if it exists
        :param guild_id: guild to get welcome message for
        """
        sql = """
        SELECT welcome_message from {}.servers
        WHERE serverid = $1
        """.format(self.schema)
        try:
            message = await self.pool.fetchrow(sql, guild_id)
            return message['welcome_message']
        except Exception as e:
            logger.warning(f'Error while getting welcome message: {e}')
            return None

    async def set_ban_footer(self, guild_id: int, message: str, logger):
        """
        Sets the ban footer for a server
        :param guild_id: Guild to update footer for
        :param message: string to insert
        """
        sql = """
        UPDATE {}.servers
        SET ban_footer = $1
        WHERE serverid = $2
        """.format(self.schema)

        try:
            await self.pool.execute(sql, message, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Issue setting ban footer: {e}')
            return False

    async def get_ban_footer(self, guild_id: int, logger):
        """
        Returns the ban footer string if it exists
        :param guild_id: guild to get footer for
        """
        sql = """
        SELECT ban_footer from {}.servers
        WHERE serverid = $1
        """.format(self.schema)
        try:
            message = await self.pool.fetchrow(sql, guild_id)
            return message['ban_footer']
        except Exception as e:
            logger.warning(f'Error while getting ban footer: {e}')
            return None

    async def set_kick_footer(self, guild_id: int, message: str, logger):
        """
        Sets the ban footer for a server
        :param guild_id: Guild to update footer for
        :param message: string to insert
        """
        sql = """
        UPDATE {}.servers
        SET kick_footer = $1
        WHERE serverid = $2
        """.format(self.schema)

        try:
            await self.pool.execute(sql, message, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Issue setting kick footer: {e}')
            return False

    async def get_kick_footer(self, guild_id: int, logger):
        """
        Returns the ban footer string if it exists
        :param guild_id: guild to get footer for
        """
        sql = """
        SELECT kick_footer from {}.servers
        WHERE serverid = $1
        """.format(self.schema)
        try:
            message = await self.pool.fetchrow(sql, guild_id)
            return message['kick_footer']
        except Exception as e:
            logger.warning(f'Error while getting kick footer: {e}')
            return None

    async def add_welcome_channel(
            self, guild_id: int, channel_id: int, logger):
        """
        Adds a channel to the welcome channel array for the server
        :param guild_id: guild to add channel to
        :param channel_id: channel to add
        """
        sql = """
        UPDATE {}.servers
        SET welcome_channels = (SELECT array_agg(distinct e)
        FROM unnest(array_append(welcome_channels,$1::bigint)) e)
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_welcome_channel(
            self, guild_id: int, channel_id: int, logger):
        """
        Removes a channel from the modlog array
        :param guild_id: guild to remove modlog channel from
        :param channel_id: channel id to remove
        """
        channel_list = await self.get_welcome_channels(guild_id, logger)
        channel_list.remove(channel_id)
        sql = """
        UPDATE {}.servers
        SET welcome_channels = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_list, guild_id)
        except Exception as e:
            logger.warning(f'Error removing modlog channel: {e}')
            return False
        return True

    async def get_welcome_channels(self, guild_id: int, logger):
        """
        Retrieves and returns the welcome channel list
        :param guild_id: guild to retrieve channels for
        """
        sql = """
        SELECT welcome_channels FROM {}.servers
        WHERE serverid = $1;
        """.format(self.schema)
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def add_logger_channel(self, guild_id: int, channel_id: int, logger):
        """
        Adds a channel to the modlog channel array for the server
        :param guild_id: guild to add channel to
        :param channel_id: channel to add
        """
        sql = """
        UPDATE {}.servers
        SET logging_channels = (SELECT array_agg(distinct e)
        FROM unnest(array_append(logging_channels,$1::bigint)) e)
        WHERE serverid = $2;
        """.format(self.schema)
        boolsql = """
        UPDATE {}.servers
        SET logging_enabled = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            await self.pool.execute(boolsql, True, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_logger_channel(self, guild_id: int, channel_id: int, logger):
        """
        Removes a channel from the modlog array
        :param guild_id: guild to remove modlog channel from
        :param channel_id: channel id to remove
        """
        channel_list = await self.get_logger_channels(guild_id)
        channel_list.remove(channel_id)
        sql = """
        UPDATE {}.servers
        SET logging_channels = $1
        WHERE serverid = $2;
        """.format(self.schema)
        boolsql = """
        UPDATE {}.servers
        SET logging_enabled = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_list, guild_id)
            if not channel_list:
                await self.pool.execute(boolsql, False, guild_id)
        except Exception as e:
            logger.warning(f'Error removing logging channel: {e}')
            return False
        return True

    async def get_logger_channels(self, guild_id: int):
        """
        Returns a list of channel ids for posting mod actions
        :param guild_id: guild to search roles for
        """
        sql = """
        SELECT logging_channels FROM {}.servers
        WHERE serverid = $1;
        """.format(self.schema)
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def get_voice_enabled(self, guild_id: int):
        """
        Returns the boolean voice_enabled for given server
        """
        sql = """
        SELECT voice_enabled FROM {}.servers
        WHERE serverid = $1;
        """.format(self.schema)
        return await self.pool.fetchval(sql, guild_id)

    async def get_voice_logging(self, guild_id: int):
        """
        Returns the boolean voice_enabled for given server
        """
        sql = """
        SELECT voice_logging FROM {}.servers
        WHERE serverid = $1;
        """.format(self.schema)
        return await self.pool.fetchval(sql, guild_id)

    async def add_voice_channel(self, guild_id: int, channel_id: int, logger):
        """
        Adds a channel to the voice channel array for the server
        :param guild_id: guild to add channel to
        :param channel_id: channel to add
        """
        sql = """
        UPDATE {}.servers
        SET voice_channels = (SELECT array_agg(distinct e)
        FROM unnest(array_append(voice_channels,$1::bigint)) e)
        WHERE serverid = $2;
        """.format(self.schema)
        boolsql = """
        UPDATE {}.servers
        SET voice_logging = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            await self.pool.execute(boolsql, True, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_voice_channel(self, guild_id: int, channel_id: int, logger):
        """
        Removes a channel from the modlog array
        :param guild_id: guild to remove modlog channel from
        :param channel_id: channel id to remove
        """
        channel_list = await self.get_voice_channels(guild_id)
        channel_list.remove(channel_id)
        sql = """
        UPDATE {}.servers
        SET voice_channels = $1
        WHERE serverid = $2;
        """.format(self.schema)
        boolsql = """
        UPDATE {}.servers
        SET voice_logging = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_list, guild_id)
            if not channel_list:
                await self.pool.execute(boolsql, False, guild_id)
        except Exception as e:
            logger.warning(f'Error removing logging channel: {e}')
            return False
        return True

    async def get_voice_channels(self, guild_id: int):
        """
        Returns a list of channel ids for posting mod actions
        :param guild_id: guild to search roles for
        """
        sql = """
        SELECT voice_channels FROM {}.servers
        WHERE serverid = $1;
        """.format(self.schema)
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    async def get_server_roles(self, guild_id: int):
        """
        Returns a list of enabled voice roles for a guild
        """
        sql = """
        SELECT roleid FROM {}.roles
        WHERE serverid = $1;
        """.format(self.schema)
        role_list = []
        records = await self.pool.fetch(sql, guild_id)
        for rec in records:
            role_list.append(rec['roleid'])
        return role_list

    async def get_role_channels(self, guild_id: int, role_id: int):
        """
        Returns a list of channels for a given role
        """
        sql = """
        SELECT channels FROM {}.roles
        WHERE serverid = $1 AND roleid = $2;
        """.format(self.schema)
        return await self.pool.fetchval(sql, guild_id, role_id)

    async def get_channel_roles(self, guild_id: int, channel_id: int):
        """
        Returns a list of roles that have a channel_id in them
        """
        sql = """
        SELECT roleid FROM {}.roles
        WHERE serverid = $1 AND $2::bigint = ANY(channels);
        """.format(self.schema)
        records = await self.pool.fetch(sql, guild_id, channel_id)
        role_list = []
        for rec in records:
            role_list.append(rec['roleid'])
        return role_list

    async def add_role_channel(self, guild_id: int, channel_id: int, role_id):
        """
        Adds a given channel_id to a given roleod
        :param guild_id: guild to pull role from
        """
        channel_array = [channel_id]
        sql = """
        INSERT INTO {}.roles VALUES ($1, $2, $3)
        ON CONFLICT (roleid) DO UPDATE
        SET channels = (SELECT array_agg(distinct e)
        FROM unnest(array_append({}.roles.channels,$4::bigint)) e);
        """.format(self.schema, self.schema)
        await self.pool.execute(
            sql, guild_id, role_id, channel_array, channel_id)
        return True

    async def rem_role_channel(
            self, guild_id: int, channel_id: int, role_id, logger):
        """
        Removes a channel from the roles channel array
        :param guild_id: guild to remove modlog channel from
        :param channel_id: channel id to remove
        """
        channel_list = await self.get_role_channels(guild_id, role_id)
        channel_list.remove(channel_id)
        sql = """
        UPDATE {}.roles
        SET channels = $1
        WHERE serverid = $2 AND roleid = $3;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_list, guild_id, role_id)
        except Exception as e:
            logger.warning(f'Error removing role channel: {e}')
            return False
        return True

    async def add_voice_role(self, guild_id: int, role_id: int):
        """
        Sets the role id for the given guild
        :param guild_id: guild to set role for
        :param role_id: role to add to guild
        """
        sql = """
        INSERT INTO {}.roles VALUES ($1, $2, $3)
        ON CONFLICT (roleid)
        DO nothing;
        """.format(self.schema)
        await self.pool.execute(sql, guild_id, role_id, [])

    async def purge_voice_roles(self, guild_id: int):
        """
        Removes all roles from a given server.
        """
        sql = """
        DELETE FROM {}.roles
        WHERE serverid = $1;
        """.format(self.schema)
        await self.pool.execute(sql, guild_id)

    async def set_voice_enabled(self, guild_id: int, value: bool):
        """
        Setsthe variable voice_enabled for a given server
        :param guild_id: guild to set voice_enabled
        :param value: boolean to set variable to
        """
        sql = """
        UPDATE {}.servers
        SET voice_enabled = $1
        WHERE serverid = $2;
        """.format(self.schema)
        await self.pool.execute(sql, value, guild_id)

    async def set_invites_allowed(self, guild_id: int, value: bool):
        """
        Setsthe variable voice_enabled for a given server
        :param guild_id: guild to set voice_enabled
        :param value: boolean to set variable to
        """
        sql = """
        UPDATE {}.servers
        SET invites_allowed = $1
        WHERE serverid = $2;
        """.format(self.schema)
        await self.pool.execute(sql, value, guild_id)

    async def add_blacklist_channel(
            self, guild_id: int, channel_id: int, logger):
        """
        Adds a channel to the blacklist channel array for the server
        :param guild_id: guild to add channel to
        :param channel_id: channel to add
        """
        sql = """
        UPDATE {}.servers
        SET blacklist_channels = (SELECT array_agg(distinct e)
        FROM unnest(array_append(blacklist_channels,$1::bigint)) e)
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_id, guild_id)
            return True
        except Exception as e:
            logger.warning(f'Error adding channel to server {guild_id}: {e}')
            return False

    async def rem_blacklist_channel(
            self, guild_id: int, channel_id: int, logger):
        """
        Removes a channel from the blacklist channel array
        :param guild_id: guild to remove modlog channel from
        :param channel_id: channel id to remove
        """
        channel_list = await self.get_blacklist_channels(guild_id)
        channel_list.remove(channel_id)
        sql = """
        UPDATE {}.servers
        SET blacklist_channels = $1
        WHERE serverid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, channel_list, guild_id)
        except Exception as e:
            logger.warning(f'Error removing modlog channel: {e}')
            return False
        return True

    async def get_blacklist_channels(self, guild_id: int):
        """
        Returns a list of channel ids for posting mod actions
        :param guild_id: guild to search roles for
        """
        sql = """
        SELECT blacklist_channels FROM {}.servers
        WHERE serverid = $1;
        """.format(self.schema)
        channel_list = await self.pool.fetchval(sql, guild_id)
        return channel_list

    """
    Moderations
    """

    async def get_modaction_indexes(self, guild_id, user_id):
        """
        Returns a count of modactions a user has
        :param guild_id: guild to search modactions
        :param user_id: user id to count for
        """
        sql = """
        SELECT indexid FROM {}.moderation
        WHERE serverid = $1 AND userid = $2;
        """.format(self.schema)
        sql_i = await self.pool.fetch(sql, guild_id, user_id)
        return list(map(lambda m: m['indexid'], sql_i))

    async def get_moderation_count(self, guild_id, user_id):
        """
        Returns a count of moderations a user has
        :param guild_id: guild to search moderations
        :param user_id: user id to count for
        """
        sql = """
        SELECT COUNT(userid) FROM {}.moderation
        WHERE serverid = $1 AND userid = $2;
        """.format(self.schema)
        return await self.pool.fetchval(sql, guild_id, user_id)

    async def insert_modaction(self, guild_id: int, mod_id: int,
                               target_id: int, reason: str,
                               action_type: Action):
        """
        Inserts into the roles table a new rolechange
        :param mod_id: the id of the mod that triggered the action
        :param target_id: the id of user that action was performed on
        :param action_type: The type of change that occured
        """
        sql = """
        INSERT INTO {}.moderation VALUES ($1, $2, $3, $4, $5, $6);
        """.format(self.schema)

        moderations = await self.get_moderation_count(guild_id, target_id)
        all_modac_i = await self.get_modaction_indexes(guild_id, target_id)
        if all_modac_i:
            index = max(all_modac_i) + 1
        else:
            index = 1

        await self.pool.execute(
            sql, 
            guild_id,
            mod_id,
            target_id,
            index,
            action_type.value,
            reason
        )

    async def get_moderation(self, guild_id: int, user_id: int, logger, recent=False):
        """
        Returns all moderation that a user has been done to
        :param guild_id: guild to search moderations
        :param user_id: user id to count for
        """
        if recent:
            sql = """
            SELECT * FROM {}.moderation
            WHERE serverid = $1 AND userid = $2 AND (logtime >= DATE_TRUNC('month', now()) - INTERVAL '3 month');
            """.format(self.schema)
        else:
            sql = """
            SELECT * FROM {}.moderation
            WHERE serverid = $1 AND userid = $2;
            """.format(self.schema)
        try:
            return await self.pool.fetch(sql, guild_id, user_id)
        except Exception as e:
            logger.warning(f'Error retrieving moderations {e}')
            return False

    async def get_single_modaction(self, guild_id: int, user_id: int, index: int, logger):
        """
        Returns a single modaction a user has on a server given the index
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        :param index: index to pull
        """
        sql = """
        SELECT * FROM {}.moderation
        WHERE serverid = $1 AND userid = $2 AND indexid = $3;
        """.format(self.schema)
        try:
            return await self.pool.fetch(sql, guild_id, user_id, index)
        except Exception as e:
            logger.warning(f'Error retrieving moderation action {e}')
            return False

    async def set_single_modaction(self, guild_id: int, user_id: str,
                                   mod_id: int, reason: str,
                                   action_type: Action, index: int, logger):
        """
        Set a single modaction a user has on a server given the index
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        :param index: index to pull
        :param reason: reason for moderation
        """
        sql = """
        UPDATE {}.moderation
        SET reason=$1, moderatorid=$2, action=$3 WHERE serverid = $4 AND userid = $5 AND indexid = $6;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, reason, mod_id, action_type.value, guild_id, user_id, index)
        except Exception as e:
            logger.warning(f'Error retrieving moderation action {e}')
        return await self.get_moderation_count(guild_id, user_id)

    async def delete_single_modaction(self, guild_id: int, user_id: str,
                                    index: int, logger):
        """
        Delete a single modaction a user has on a server given the index
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        :param index: index to pull
        """
        sql = """
        DELETE FROM {}.moderation
        WHERE serverid = $1 AND userid = $2 AND indexid = $3;
        """.format(self.schema)
        try:
            return await self.pool.execute(sql, guild_id, user_id, index)
        except Exception as e:
            logger.warning(f'Error deleting moderation action {e}')
            return False

    """
    Warnings
    """

    async def get_warning_count(self, guild_id, user_id):
        """
        Returns a count of infractions a user has
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        """
        sql = """
        SELECT COUNT(userid) FROM {}.warnings
        WHERE serverid = $1 AND userid = $2;
        """.format(self.schema)
        return await self.pool.fetchval(sql, guild_id, user_id)

    async def get_warning_indexes(self, guild_id, user_id):
        """
        Returns a count of infractions a user has
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        """
        sql = """
        SELECT indexid FROM {}.warnings
        WHERE serverid = $1 AND userid = $2;
        """.format(self.schema)
        sql_i = await self.pool.fetch(sql, guild_id, user_id)
        return list(map(lambda m: m['indexid'], sql_i))

    async def add_warning(
            self, guild_id: int, user_id: str,
            reason: str, major: bool, logger):
        """
        Takes a userid and string and inserts it into the guild's
        warning log
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        :param reason: reason for warning
        :param major: whether warning is a major/minor warning
        """
        infraction_count = await self.get_warning_count(guild_id, user_id)
        all_warn_i = await self.get_warning_indexes(guild_id, user_id)
        if all_warn_i:
            index = max(all_warn_i) + 1
        else:
            index = 1

        sql = """
        INSERT INTO {}.warnings VALUES ($1, $2, $3, $4, $5);
        """.format(self.schema)
        try:
            await self.pool.execute(
                sql,
                guild_id,
                user_id,
                index,
                reason,
                major
            )
            return infraction_count
        except Exception as e:
            logger.warning(f'Error inserting warning into db: {e}')
            return False

    async def get_single_warning(self, guild_id: int, user_id: int, index: int, logger):
        """
        Returns a single warnings a user has on a server given the index
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        :param index: index to pull
        """
        sql = """
        SELECT * FROM {}.warnings
        WHERE serverid = $1 AND userid = $2 AND indexid = $3;
        """.format(self.schema)
        try:
            return await self.pool.fetch(sql, guild_id, user_id, index)
        except Exception as e:
            logger.warning(f'Error retrieving warning {e}')
            return False

    async def set_single_warning(self, guild_id: int, user_id: str,
                                 reason: str, major: bool, index: int, logger):
        """
        Set a single warnings a user has on a server given the index
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        :param index: index to pull
        :param reason: reason for warning
        :param major: whether warning is a major/minor warning
        """
        sql = """
        UPDATE {}.warnings
        SET reason=$1, major=$2 WHERE serverid = $3 AND userid = $4 AND indexid = $5;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, reason, major, guild_id, user_id, index)
        except Exception as e:
            logger.warning(f'Error retrieving warnings {e}')
        return await self.get_warning_count(guild_id, user_id)

    async def delete_single_warning(self, guild_id: int, user_id: str,
                                    index: int, logger):
        """
        Delete a single warnings a user has on a server given the index
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        :param index: index to pull
        """
        sql = """
        DELETE FROM {}.warnings
        WHERE serverid = $1 AND userid = $2 AND indexid = $3;
        """.format(self.schema)
        try:
            return await self.pool.execute(sql, guild_id, user_id, index)
        except Exception as e:
            logger.warning(f'Error deleting warning {e}')
            return False

    async def get_warnings(self, guild_id: int, user_id: int, logger, recent = False):
        """
        Returns all warnings a user has on a server
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        """
        if recent:
            f = '%Y-%m-%d'
            sql = """
            SELECT * FROM {}.warnings
            WHERE serverid = $1 AND userid = $2 AND (logtime >= DATE_TRUNC('month', now()) - INTERVAL '3 month') ORDER BY indexid;
            """.format(self.schema)
        else:
            sql = """
            SELECT * FROM {}.warnings
            WHERE serverid = $1 AND userid = $2 ORDER BY indexid;
            """.format(self.schema)
        try:
            return await self.pool.fetch(sql, guild_id, user_id)
        except Exception as e:
            logger.warning(f'Error retrieving warnings {e}')
            return False

    async def add_slowmode_channel(
            self, server_id: int, channel_id: int, time: int, logger):
        """
        Adds a channel to the slowmode db
        :param server_id: server to add channel for
        :param channel_id: channel to add
        :param time: time in seconds to set slowmode for
        """
        sql = """
        INSERT INTO {}.slowmode VALUES ($1, $2, $3);
        """.format(self.schema)
        try:
            await self.pool.execute(sql, server_id, channel_id, time)
            return True
        except Exception as e:
            logger.warning(f'Error adding slowmode channel to database: {e}')
            return False

    async def rem_slowmode_channel(
            self, server_id: int, channel_id: int, logger):
        """
        Removes a channel from the slowmode db
        :param server_id: server to add channel for
        :param channel_id: channel to add
        """
        sql = """
        DELETE FROM {}.slowmode
        WHERE serverid = $1 AND channelid = $2;
        """.format(self.schema)
        try:
            await self.pool.execute(sql, server_id, channel_id)
            return True
        except Exception as e:
            logger.warning(f'Error removing slowmode channel to database: {e}')
            return False

    async def get_slowmode_channels(self, logger):
        """
        Returns all slowmode channels
        """
        sql = """
        SELECT * FROM {}.slowmode;
        """.format(self.schema)
        try:
            ret_channels = {}
            channels = await self.pool.fetch(sql)
            for channel in channels:
                ret_channels[channel['channelid']] = channel['interval']
            return ret_channels
        except Exception as e:
            logger.warning(f'Error retrieving slowmode channels {e}')
            return False
