import asyncio
import yaml
import sys

import subprocess
import datetime
from logging import Formatter, INFO, StreamHandler, getLogger
from cogs.utils.db_utils import PostgresController
from time import time, sleep

async def get_postgres():
    """
    async method to initialize the pg_utils class
    """
    with open("config/config.yml", 'r') as yml_config:
        config = yaml.load(yml_config)
    print(config['postgres_credentials'])
    logger = getLogger('migration')
    console_handler = StreamHandler()
    console_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s')
    )
    logger.addHandler(console_handler)
    logger.setLevel(INFO)
    postgres_cred = config['postgres_credentials']
    pg_utils = None
    while not pg_utils:
        try:
            pg_utils = await PostgresController.get_instance(
                logger=logger, connect_kwargs=postgres_cred)
        except Exception as e:
            logger.critical(
                f'Error initializing DB - trying again in 5 seconds')
            logger.debug(f'Error: {e}')
            sleep(5)
    return (pg_utils, logger)

async def migrate():
    pg_utils, logger = await get_postgres()
    print(await pg_utils.get_server_settings())

    get_servers_sql = f"""
    SELECT * FROM yinbot.servers;
    """

    get_voice_roles = f"""
    SELECT * FROM yinbot.roles;
    """

    servers = await pg_utils.pool.fetch(get_servers_sql)
    roles = await pg_utils.pool.fetch(get_voice_roles)
    errors = 0
    for row in servers:
        try:
            for channel in row['modlog_channels']:
                await pg_utils.add_modlog_channel(row['serverid'], channel, logger)
            for channel in row['welcome_channels']:
                await pg_utils.add_welcome_channel(row['serverid'], channel, logger)
            for channel in row['logging_channels']:
                await pg_utils.add_logger_channel(row['serverid'], channel, logger)
            for channel in row['blacklist_channels']:
                await pg_utils.add_blacklist_channel(row['serverid'], channel, logger)
            for role in row['assignableroles']:
                await pg_utils.add_assignable_role(row['serverid'], role, logger)
            for channel in row['voice_channels']:
                await pg_utils.add_voice_channel(row['serverid'], channel, logger)
        except Exception as e:
            errors += 1
            print(e)
    for row in roles:
        try:
            for channel in row['channels']:
                await pg_utils.add_role_channel(row['serverid'], channel, row['roleid']) 
        except Exception as e:
            errors += 1
            print(e)

    if not errors == 0:
        logger.critical("Errors when migrating, skipping destructive actions")
        return
    
    drop_unnecessary_columns = f"""
    ALTER TABLE yinbot.servers
    DROP COLUMN voice_channels,
    DROP COLUMN modlog_channels,
    DROP COLUMN welcome_channels,
    DROP COLUMN logging_channels,
    DROP COLUMN assignableroles,
    DROP COLUMN blacklist_channels;
    """

    drop_old_voice_table = f"""
    DROP TABLE yinbot.roles;
    """

    add_temp_table = f"""
    ALTER TABLE yinbot.servers ADD COLUMN addtime_t TIMESTAMP;
    """

    update_temp_table = f"""
    UPDATE yinbot.servers set addtime_t = addtime;
    """

    drop_old_table = f"""
    ALTER TABLE yinbot.servers DROP COLUMN addtime;
    """

    rename_temp_table = f"""
    ALTER TABLE yinbot.servers RENAME COLUMN addtime_t TO addtime;
    """
    try:
        await pg_utils.pool.execute(drop_unnecessary_columns)
        await pg_utils.pool.execute(drop_old_voice_table)
        await pg_utils.pool.execute(add_temp_table)
        await pg_utils.pool.execute(update_temp_table)
        await pg_utils.pool.execute(drop_old_table)
        await pg_utils.pool.execute(rename_temp_table)
    except Exception as e:
        logger.critical("Error doing final migration:")
        logger.critical(e)
    return

def run():
    asyncio.run(migrate())

if __name__ == '__main__':
    run()