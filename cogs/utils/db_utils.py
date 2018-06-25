"""
Database utility functions.
"""
from typing import Optional
from .enums import Action
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
      ban_footer text,
      kick_footer text,
      welcome_channels bigint ARRAY,
      logging_enabled boolean DEFAULT FALSE,
      logging_channels bigint ARRAY,
      assignableroles bigint ARRAY,
      blacklist_channels bigint ARRAY,
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
      userid BIGINT,
      moderatorid BIGINT,
      ban BOOLEAN,
      reason text,
      logtime TIMESTAMP DEFAULT current_timestamp,
      PRIMARY KEY (serverid, userid, indexid)
    );"""

    await pool.execute(servers)
    await pool.execute(vplust)
    await pool.execute(warnings)
    await pool.execute(moderation)


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
        INSERT INTO {}.servers VALUES
        ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
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
            f'This is an automated message',
            f'This is an automated message',
            [],
            False,
            [],
            [],
            [],
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
            return await self.fetchrow(sql, server_id)
        except:
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

    async def add_blacklist_channel(self, guild_id: int, channel_id: int, logger):
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

    async def rem_blacklist_channel(self, guild_id: int, channel_id: int, logger):
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

    async def add_warning(
        self, guild_id: int, user_id: str, reason: str, major: bool, logger):
        """
        Takes a userid and string and inserts it into the guild's
        warning log
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        :param reason: reason for warning
        :param major: whether warning is a major/minor warning
        """
        infraction_count = await self.get_warning_count(guild_id, user_id)
        sql = """
        INSERT INTO {}.warnings VALUES ($1, $2, $3, $4, $5);
        """.format(self.schema)
        try:
            await self.pool.execute(
                sql,
                guild_id,
                user_id,
                infraction_count + 1,
                reason,
                major
            )
            return infraction_count
        except Exception as e:
            logger.warning(f'Error inserting warning into db: {e}')
            return False

    async def get_warnings(self, guild_id: int, user_id: int, logger):
        """
        Returns all warnings a user has on a server
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        """
        sql = """
        SELECT * FROM {}.warnings
        WHERE serverid = $1 AND userid = $2;
        """.format(self.schema)
        try:
            return await self.pool.fetch(sql, guild_id, user_id)
        except Exception as e:
            logger.warning(f'Error retrieving warnings {e}')
            return False

    async def add_mod_action(self, guild_id: int, user_id: int,
                             mod_id: int, ban: bool, reason: str, logger):
        """
        Adds a new mod action to the database
        :param guild_id: guild to add mod action to
        :param user_id: user action was taken against
        :param mod_id: responsible moderator
        :param ban: whether action was a ban
        :param reason: reason for mod action
        """
        sql = """
        INSERT INTO {}.moderation VALUES ($1, $2, $3, $4, $5);
        """.format(self.schema)
        try:
            await self.pool.execute(sql, guild_id, user_id, mod_id,
                                    ban, reason)
            return True
        except Exception as e:
            logger.warning(f'Error adding mod action to database: {e}')
            return False


    async def get_all_mod_actions(self, guild_id: int, user_id: int, logger):
        """
        Returns all modActions a user has on a server
        :param guild_id: guild to search infractions
        :param user_id: user id to count for
        """
        sql = """
        SELECT * FROM {}.moderation
        WHERE serverid = $1 AND userid = $2;
        """.format(self.schema)
        try:
            return await self.pool.fetch(sql, guild_id, user_id)
        except Exception as e:
            logger.warning(f'Error retrieving warnings {e}')
            return False

