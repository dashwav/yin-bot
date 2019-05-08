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
    # TODO migrate script
    return

def run():
    asyncio.run(migrate())

if __name__ == '__main__':
    run()