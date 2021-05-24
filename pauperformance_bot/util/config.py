import configparser

from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import pretty_str, now

logger = get_application_logger()


def read_config(config_file_path):
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option  # preserve case
    config.read(config_file_path)
    logger.debug(f"Read configuration file: {config}")
    return config


def read_archetype_config(config_file_path):
    config = read_config(config_file_path)
    values = {
        **config["values"],
        "last_update_date": pretty_str(now()),
    }
    list_fields = ["aliases", "mana", "type", "staples", "frequents"]
    for field in list_fields:
        values[field] = _parse_list_value(config["values"][field])
    return values


def _parse_list_value(raw_value):
    return [value.strip(" ") for value in raw_value.split(",")]
