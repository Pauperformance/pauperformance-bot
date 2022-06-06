import configparser
from itertools import count

from deprecated import deprecated

from pauperformance_bot.constant.flags import get_language_flag
from pauperformance_bot.exceptions import PauperformanceException
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


def read_config(config_file_path):
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = lambda option: option  # preserve case
    config.read(config_file_path)
    logger.debug(f"Read configuration file: {config_file_path}")
    return config


@deprecated(reason="Migrated")
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
    resources = _read_sequential_resources(config, "resource")
    servers = _read_sequential_resources(config, "discord")
    for server in servers:
        server["author"] = '<i class="fa-brands fa-discord"></i>'
        server["date"] = "~"

    if "sideboard" in config:
        resources.append(
            {
                "url": config["sideboard"]["url"],
                "name": "**Sideboard Guide**",
                "author": '<i class="fa-solid fa-book"></i>',
                "language": "🇬🇧",
                "date": "~",
            }
        )

    return {
        "values": values,
        "references": references,
        "resources": resources + servers,
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
        "resources": _read_sequential_resources(config, "resource"),
    }


@deprecated(reason="Migrated")
def _read_sequential_resources(config, key):
    resources = []
    for i in count(1):
        if f"{key}{i}" in config:
            resources.append(
                {
                    **config[f"{key}{i}"],
                }
            )
        else:
            break
    return _format_and_sort_resources(resources)


@deprecated(reason="Migrated")
def _format_and_sort_resources(resources):
    for resource in resources:
        resource["language"] = get_language_flag(resource["language"])
    return sorted(
        resources,
        key=lambda r: r.get("date", "") + r["name"],
        reverse=True,
    )


@deprecated(reason="Migrated")
def _parse_list_value(raw_value):
    return [value.strip(" ") for value in raw_value.split(",")] if raw_value else []
