import configparser
import glob
from itertools import count
from typing import Optional

from pauperformance_bot.constant.flags import get_language_flag
from pauperformance_bot.constant.myr import MyrFileSystem
from pauperformance_bot.entity.api.archetype import Resource
from pauperformance_bot.entity.api.miscellanea import Newspauper
from pauperformance_bot.entity.api.phd import PhDSheet
from pauperformance_bot.entity.config.archetype import (
    ArchetypeConfig,
    DiscordResource,
    SideboardResource,
)
from pauperformance_bot.entity.config.phd import PhDConfig
from pauperformance_bot.exceptions import PauperformanceException
from pauperformance_bot.service.mtg.scryfall import ScryfallService
from pauperformance_bot.util.config import read_newspauper_config
from pauperformance_bot.util.entities import auto_repr, auto_str
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
    def _parse_list_value(raw_value) -> Optional[list[str]]:
        return (
            [value.strip(" ") for value in raw_value.split(",")] if raw_value else None
        )

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

    def list_phd_sheets(
        self,
        scryfall_service: ScryfallService = ScryfallService(),
    ) -> list[PhDSheet]:
        config_dir = self.myr_file_system.RESOURCES_CONFIG_PHDS_DIR
        logger.info(f"Reading PhD sheets from {config_dir}...")
        phd_sheets: list[PhDSheet] = [
            self.get_phd_sheet(config_file, scryfall_service)
            for config_file in glob.glob(f"{config_dir}/*.ini")
        ]
        logger.info(f"Read {len(phd_sheets)} PhD sheets from {config_dir}.")
        return phd_sheets

    def get_phd_sheet(
        self,
        config_file_path: str,
        scryfall_service: ScryfallService = ScryfallService(),
    ) -> PhDSheet:
        config = self._read_config_file(config_file_path)
        values = config["values"]

        if card_url := values["favorite_pauper_card_url"]:
            card = scryfall_service.get_card_from_url(card_url)
            favorite_pauper_card_name = card["name"]
            favorite_pauper_card_image_url = card["image_uris"]["large"].rsplit(
                "?", maxsplit=1
            )[0]
        else:
            favorite_pauper_card_name = None
            favorite_pauper_card_image_url = None

        if card_url := values["favorite_flavor_text_url"]:
            card = scryfall_service.get_card_from_url(card_url)
            favorite_flavor_text_name = card["name"]
            favorite_flavor_text_image_url = card["image_uris"]["large"].rsplit(
                "?", maxsplit=1
            )[0]
            favorite_flavor_text_lines = card["flavor_text"]
        else:
            favorite_flavor_text_name = None
            favorite_flavor_text_image_url = None
            favorite_flavor_text_lines = None

        if card_url := values["favorite_artwork_url"]:
            card = scryfall_service.get_card_from_url(card_url)
            favorite_artwork_name = card["name"]
            favorite_artwork_image_url = card["image_uris"]["large"].rsplit(
                "?", maxsplit=1
            )[0]
        else:
            favorite_artwork_name = None
            favorite_artwork_image_url = None

        favorite_artist_gallery_url = (
            scryfall_service.get_artist_gallery_search_url(artist_name)
            if (artist_name := values["favorite_artist_name"])
            else None
        )

        phd_sheet: PhDSheet = PhDSheet(
            name=values["name"],
            bio=values["bio"],
            mtgo_name=values["mtgo_name"],
            twitch_channel_url=values["twitch_channel_url"],
            youtube_channel_url=values["youtube_channel_url"],
            favorite_format=values["favorite_format"],
            favorite_pauper_archetype=values["favorite_pauper_archetype"],
            favorite_pauper_card_name=favorite_pauper_card_name,
            favorite_pauper_card_url=values["favorite_pauper_card_url"],
            favorite_pauper_card_image_url=favorite_pauper_card_image_url,
            favorite_flavor_text_name=favorite_flavor_text_name,
            favorite_flavor_text_url=values["favorite_flavor_text_url"],
            favorite_flavor_text_image_url=favorite_flavor_text_image_url,
            favorite_flavor_text_lines=favorite_flavor_text_lines,
            favorite_artwork_name=favorite_artwork_name,
            favorite_artwork_url=values["favorite_artwork_url"],
            favorite_artwork_image_url=favorite_artwork_image_url,
            favorite_artist_name=values["favorite_artist_name"],
            favorite_artist_gallery_url=favorite_artist_gallery_url,
            favorite_magic_quote_lines=values["favorite_magic_quote_lines"],
        )
        logger.info(f"Read PhD sheet {phd_sheet}.")
        return phd_sheet

    def list_phds(
        self,
    ) -> list[PhDConfig]:
        config_dir = self.myr_file_system.RESOURCES_CONFIG_PHDS_DIR
        logger.info(f"Reading PhDs from {config_dir}...")
        phds: list[PhDConfig] = [
            self.get_phd(config_file)
            for config_file in glob.glob(f"{config_dir}/*.ini")
        ]
        logger.info(f"Read {len(phds)} PhDs from {config_dir}.")
        return phds

    def get_phd(
        self,
        config_file_path: str,
    ) -> PhDConfig:
        config = self._read_config_file(config_file_path)
        values = config["values"]
        dev = config["dev"]

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
        discord_id = int(discord_id) if (discord_id := dev["discord_id"]) else None

        phd: PhDConfig = PhDConfig(
            name=values["name"],
            mtgo_name=values["mtgo_name"],
            twitch_login_name=twitch_login_name,
            youtube_channel_id=youtube_channel_id,
            default_youtube_language=dev["default_youtube_language"],
            discord_id=discord_id,
            deckstats_name=dev["deckstats_name"],
            deckstats_id=dev["deckstats_id"],
        )
        logger.info(f"Read PhD {phd}.")
        return phd

    def get_pauperformance_phd(self) -> PhDConfig:
        return next(phd for phd in self.list_phds() if phd.name == "Pauperformance")

    def list_archetypes(self) -> list[ArchetypeConfig]:
        config_dir = self.myr_file_system.RESOURCES_CONFIG_ARCHETYPES_DIR
        logger.info(f"Reading archetypes from {config_dir}...")
        archetypes = [
            self.get_archetype(config_file)
            for config_file in glob.glob(f"{config_dir}/*.ini")
        ]
        logger.info(f"Read {len(archetypes)} archetypes from {config_dir}.")
        return archetypes

    def get_archetype(self, config_file_path: str) -> ArchetypeConfig:
        config = self._read_config_file(config_file_path)

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

        logger.debug(f"We should now parse this {config}...")
        return ArchetypeConfig(
            name=config["values"]["name"],
            aliases=self._parse_list_value(config["values"]["aliases"]),
            family=config["values"]["family"],
            dominant_mana=self._parse_list_value(config["values"]["mana"]),
            game_type=self._parse_list_value(config["values"]["type"]),
            description=config["values"]["description"],
            reference_decks=list(references.values()),
            resource_sideboard=resource_sideboard,
            resources_discord=resources_discord,
            resources=resources,
        )

    def get_newspauper(self) -> Newspauper:
        config_file_path = self.myr_file_system.RESOURCES_CONFIG_NEWSPAUPER
        logger.info(f"Reading Newspauper from {config_file_path}...")
        config = read_newspauper_config(config_file_path)
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

    def get_archetype_name_from_alias(self, name):
        for archetype in self.list_archetypes():
            if archetype.name == name:
                return name
            if archetype.aliases:
                for alias in archetype.aliases:
                    if alias == name:
                        return archetype.name
        raise PauperformanceException(f"Unable to find archetype for alias {name}")
