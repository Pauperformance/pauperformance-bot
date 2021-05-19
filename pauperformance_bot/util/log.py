import logging
import os

from pauperformance_bot.constants import (
    APPLICATION_NAME,
    DEFAULT_LOGGING_FILE,
    PAUPERFORMANCE_BOT_DIR,
)

LOG_FORMAT = (
    "%(levelname)s:%(asctime)s:%(module)s:%(funcName)s:"
    "L%(lineno)d: %(message)s"
)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(APPLICATION_NAME)
os.makedirs(PAUPERFORMANCE_BOT_DIR, exist_ok=True)
file_handler = logging.FileHandler(DEFAULT_LOGGING_FILE)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(file_handler)


def get_application_logger(cli_group=None):
    return (
        logging.getLogger("{}.{}".format(APPLICATION_NAME, cli_group))
        if cli_group
        else logger
    )
