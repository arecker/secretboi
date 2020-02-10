import os
import platform
import sys
import time

from .log import make_logger
from .config import Config
from .vault import Client

logger = make_logger(__name__)


def main():
    logger.info('starting secretboi, python (%s) %s', platform.python_version(), sys.executable)
    config = Config.from_env(env=os.environ)

    logger.info('creating new vault client')
    client = Client.from_config(config)

    logger.info('authenticating to vault')
    client.authenticate()

    logger.info('writing secrets')
    client.populate()

    if config.only_run_once:
        logger.info('ONLY_RUN_ONCE="1" specified, exiting...')
        sys.exit(0)

    logger.info('beginning watch/refresh loop')
    while True:
        logger.info('TODO: do stuff')
        time.sleep(5)
