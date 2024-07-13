import logging
import os

from pauperformance_bot.constant.pauperformance.myr import (
    APPLICATION_NAME,
    DEFAULT_LOGGING_FILE,
    PAUPERFORMANCE_BOT_DIR,
)

LOG_FORMAT = (
    "%(levelname)s:%(asctime)s:%(module)s:%(funcName)s():L%(lineno)d: %(message)s"
    # "%(message)s"
)
# configure root logger
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
# logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
# configure app logger
logger = logging.getLogger(APPLICATION_NAME)
# logger.setLevel(logging.DEBUG)
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
