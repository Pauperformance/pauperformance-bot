import logging
import os

from pauperformance_bot.constant.myr import APPLICATION_NAME, PAUPERFORMANCE_BOT_DIR, DEFAULT_LOGGING_FILE

LOG_FORMAT = (
    "%(levelname)s:%(asctime)s:%(module)s:%(funcName)s:"
    "L%(lineno)d: %(message)s"
)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
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
