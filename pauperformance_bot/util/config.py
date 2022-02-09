import configparser
from itertools import count

from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import now, pretty_str

logger = get_application_logger()


def read_config(config_file_path):
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option  # preserve case
    config.read(config_file_path)
    logger.debug(f"Read configuration file: {config_file_path}")
    return config


def read_archetype_config(config_file_path):
    config = read_config(config_file_path)
    values = {
        **config["values"],
    }
    list_fields = ["aliases", "mana", "type"]
    for field in list_fields:
        values[field] = _parse_list_value(config["values"][field])
    resources = []
    for i in count(1):
        if f"resource{i}" in config:
            resources.append(
                {
                    **config[f"resource{i}"],
                }
            )
        else:
            break
    return {
        "values": values,
        "resources": resources,
    }


def read_family_config(config_file_path):
    config = read_config(config_file_path)
    values = {
        **config["values"],
        "last_update_date": pretty_str(now()),
    }
    return values


def _parse_list_value(raw_value):
    return (
        [value.strip(" ") for value in raw_value.split(",")]
        if raw_value
        else []
    )
