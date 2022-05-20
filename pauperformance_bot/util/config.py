import configparser
from itertools import count

from pauperformance_bot.constant.flags import get_language_flag
from pauperformance_bot.exceptions import PauperformanceException
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


def read_config(config_file_path):
    config = configparser.ConfigParser()
    config.optionxform = lambda option: option  # preserve case
    config.read(config_file_path)
    logger.debug(f"Read configuration file: {config_file_path}")
    return config


def read_archetype_config(config_file_path):
    config = read_config(config_file_path)
    # read values
    values = {
        **config["values"],
    }
    list_fields = ["aliases", "mana", "type"]
    for field in list_fields:
        values[field] = _parse_list_value(config["values"][field])
    # read references
    references = {**config["references"]}
    # quick integrity check
    for key, value in references.items():
        if key not in value:
            raise PauperformanceException(
                f"p12e code: {key} does not match value for deck {value}."
            )
    # read resources
    resources = _read_sequential_resources(config)
    return {
        "values": values,
        "references": references,
        "resources": resources,
    }


def read_family_config(config_file_path):
    config = read_config(config_file_path)
    values = {
        **config["values"],
    }
    return values


def read_newspauper_config(config_file_path):
    config = read_config(config_file_path)
    return {
        "resources": _read_sequential_resources(config),
    }


def _read_sequential_resources(config):
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
    return _format_and_sort_resources(resources)


def _format_and_sort_resources(resources):
    for resource in resources:
        resource["language"] = get_language_flag(resource["language"])
    return sorted(
        resources,
        key=lambda r: r["date"],
        reverse=True,
    )


def _parse_list_value(raw_value):
    return [value.strip(" ") for value in raw_value.split(",")] if raw_value else []
