import configparser
import glob
from functools import lru_cache
from itertools import count

from pauperformance_bot.constant.flags import get_language_flag
from pauperformance_bot.constant.pauperformance.myr import MyrFileSystem
from pauperformance_bot.entity.api.archetype import Resource
from pauperformance_bot.entity.api.creator import CreatorSheet
from pauperformance_bot.entity.api.miscellanea import Changelog, Newspauper
from pauperformance_bot.entity.config.archetype import (
    ArchetypeConfig,
    ChangelogEntry,
    DiscordResource,
    SideboardResource,
)
from pauperformance_bot.entity.config.creator import CreatorConfig
from pauperformance_bot.exceptions import PauperformanceException
from pauperformance_bot.util.config import read_config_with_sequential_resources
from pauperformance_bot.util.decorators import auto_repr, auto_str
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


@auto_repr
@auto_str
class ConfigReader:
    def __init__(self, myr_file_system: MyrFileSystem = MyrFileSystem()):
        self.myr_file_system: MyrFileSystem = myr_file_system

    @staticmethod
    def _read_config_file(config_file_path):
        logger.debug(f"Reading configuration file {config_file_path}...")
        config = configparser.ConfigParser(allow_no_value=True)
        config.optionxform = lambda option: option  # preserve case
        config.read(config_file_path)
        logger.debug(f"Read configuration file {config_file_path}.")
        return config

    @staticmethod
    def _parse_list_value(raw_value) -> list[str]:
        return [value.strip(" ") for value in raw_value.split(",")] if raw_value else []

    @staticmethod
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
        for resource in resources:
            resource["language"] = get_language_flag(resource["language"])
        return sorted(
            resources,
            key=lambda r: r.get("date", "") + r.get("name"),
            reverse=True,
        )

    def list_creator_sheets(self) -> list[CreatorSheet]:
        config_dir = self.myr_file_system.RESOURCES_CONFIG_CREATORS_DIR
        logger.info(f"Reading creator sheets from {config_dir}...")
        creator_sheets: list[CreatorSheet] = [
            self.get_creator_sheet(config_file)
            for config_file in glob.glob(f"{config_dir}/*.ini")
        ]
        logger.info(f"Read {len(creator_sheets)} creator sheets from {config_dir}.")
        return creator_sheets

    def get_creator_sheet(
        self,
        config_file_path: str,
    ) -> CreatorSheet:
        config = self._read_config_file(config_file_path)
        values = config["values"]
        creator_sheet: CreatorSheet = CreatorSheet(
            name=values["name"],
            mtgo_name=values["mtgo_name"],
            mtgo_name2=values["mtgo_name2"],
            twitch_channel_url=values["twitch_channel_url"],
            youtube_channel_url=values["youtube_channel_url"],
        )
        logger.debug(f"Read creator sheet {creator_sheet}.")
        return creator_sheet

    def list_creators(
        self,
    ) -> list[CreatorConfig]:
        config_dir = self.myr_file_system.RESOURCES_CONFIG_CREATORS_DIR
        logger.info(f"Reading creators from {config_dir}...")
        creators: list[CreatorConfig] = [
            self.get_creator(config_file)
            for config_file in glob.glob(f"{config_dir}/*.ini")
        ]
        logger.info(f"Read {len(creators)} creators from {config_dir}.")
        return creators

    def get_creator(
        self,
        config_file_path: str,
    ) -> CreatorConfig:
        config = self._read_config_file(config_file_path)
        values = config["values"]

        twitch_login_name = (
            url.rsplit("/", maxsplit=1)[-1]
            if (url := values["twitch_channel_url"])
            else None
        )
        youtube_channel_id = (
            url.rsplit("/", maxsplit=1)[-1]
            if (url := values["youtube_channel_url"])
            else None
        )
        creator: CreatorConfig = CreatorConfig(
            name=values["name"],
            mtgo_name=values["mtgo_name"],
            mtgo_name2=values["mtgo_name2"],
            twitch_login_name=twitch_login_name,
            youtube_channel_id=youtube_channel_id,
        )
        logger.debug(f"Read creator {creator}.")
        return creator

    def get_pauperformance_creator(self) -> CreatorConfig:
        return next(c for c in self.list_creators() if c.name == "Pauperformance")

    @lru_cache(maxsize=1)
    def list_archetypes(self) -> list[ArchetypeConfig]:
        config_dir = self.myr_file_system.RESOURCES_CONFIG_ARCHETYPES_DIR
        logger.info(f"Reading archetypes from {config_dir}...")
        archetypes = [
            self.get_archetype(config_file)
            for config_file in sorted(glob.glob(f"{config_dir}/*.ini"))
        ]
        logger.info(f"Read {len(archetypes)} archetypes from {config_dir}.")
        return archetypes

    def get_archetype(self, config_file_path: str) -> ArchetypeConfig:
        config = self._read_config_file(config_file_path)
        must_have_cards: list[str] = config["values"]["must_have_cards"].split("\n")
        must_have_cards.remove("")
        must_not_have_cards: list[str] = config["values"]["must_not_have_cards"].split(
            "\n"
        )
        must_not_have_cards.remove("")

        # read references and perform quick integrity check
        references = {**config["references"]}
        for key, value in references.items():
            if key not in value:
                raise PauperformanceException(
                    f"p12e code: {key} does not match value for deck {value}."
                )

        resource_sideboard = None
        if "sideboard" in config:
            resource_sideboard = SideboardResource(link=config["sideboard"]["url"])

        resources_discord = [
            DiscordResource(
                name=server["name"],
                link=server["url"],
                language=server["language"],
            )
            for server in self._read_sequential_resources(config, "discord")
        ]

        resources = [
            Resource(
                name=resource["name"],
                link=resource["url"],
                language=resource["language"],
                author=resource["author"],
                date=resource["date"],
            )
            for resource in self._read_sequential_resources(config, "resource")
        ]

        return ArchetypeConfig(
            name=config["values"]["name"],
            aliases=self._parse_list_value(config["values"]["aliases"]),
            family=config["values"]["family"],
            dominant_mana=self._parse_list_value(config["values"]["mana"]),
            game_type=self._parse_list_value(config["values"]["type"]),
            description=config["values"]["description"],
            must_have_cards=must_have_cards,
            must_not_have_cards=must_not_have_cards,
            reference_decks=list(references.values()),
            resource_sideboard=resource_sideboard,
            resources_discord=resources_discord,
            resources=resources,
        )

    def get_newspauper(self) -> Newspauper:
        config_file_path = self.myr_file_system.RESOURCES_CONFIG_NEWSPAUPER
        logger.info(f"Reading Newspauper from {config_file_path}...")
        config = read_config_with_sequential_resources(config_file_path)
        news: list[Resource] = [
            Resource(
                name=resource["name"],
                link=resource["url"],
                language=resource["language"],
                author=resource["author"],
                date=resource["date"],
            )
            for resource in config["resources"]
        ]
        newspauper: Newspauper = Newspauper(
            news=news,
        )
        logger.debug(f"Newspauper: {newspauper}")
        logger.info(f"Read Newspauper from {config_file_path}.")
        return newspauper

    def get_changelog(self) -> Changelog:
        config_file_path = self.myr_file_system.RESOURCES_CONFIG_CHANGELOG
        logger.info(f"Reading Changelog from {config_file_path}...")
        config = read_config_with_sequential_resources(config_file_path)
        changes: list[ChangelogEntry] = [
            ChangelogEntry(
                text=resource["text"],
                date=resource["date"],
                scope=resource["scope"],
                link=resource["link"],
            )
            for resource in config["resources"]
        ]
        changelog: Changelog = Changelog(
            changes=changes,
        )
        logger.debug(f"Changelog: {changelog}")
        logger.info(f"Read Changelog from {config_file_path}.")
        return changelog

    def get_archetype_name_from_alias(self, name):
        for archetype in self.list_archetypes():
            if archetype.name == name:
                return name
            if archetype.aliases:
                for alias in archetype.aliases:
                    if alias == name:
                        return archetype.name
        raise PauperformanceException(f"Unable to find archetype for alias {name}")
