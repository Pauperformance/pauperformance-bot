import configparser
import glob

from pauperformance_bot.constant.myr import MyrFileSystem
from pauperformance_bot.constant.phds import PAUPERFORMANCE
from pauperformance_bot.entity.api.phd_sheet import PhDSheet
from pauperformance_bot.entity.phd import PhD
from pauperformance_bot.service.scryfall import ScryfallService
from pauperformance_bot.util.config import read_archetype_config
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
            favorite_pauper_card_name = ""
            favorite_pauper_card_image_url = ""

        if card_url := values["favorite_flavor_text_url"]:
            card = scryfall_service.get_card_from_url(card_url)
            favorite_flavor_text_name = card["name"]
            favorite_flavor_text_image_url = card["image_uris"]["large"].rsplit(
                "?", maxsplit=1
            )[0]
            favorite_flavor_text_lines = card["flavor_text"]
        else:
            favorite_flavor_text_name = ""
            favorite_flavor_text_image_url = ""
            favorite_flavor_text_lines = ""

        if card_url := values["favorite_artwork_url"]:
            card = scryfall_service.get_card_from_url(card_url)
            favorite_artwork_name = card["name"]
            favorite_artwork_image_url = card["image_uris"]["large"].rsplit(
                "?", maxsplit=1
            )[0]
        else:
            favorite_artwork_name = ""
            favorite_artwork_image_url = ""

        favorite_artist_gallery_url = (
            scryfall_service.get_artist_gallery_search_url(artist_name)
            if (artist_name := values["favorite_artist_name"])
            else ""
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
    ) -> list[PhD]:
        config_dir = self.myr_file_system.RESOURCES_CONFIG_PHDS_DIR
        logger.info(f"Reading PhDs from {config_dir}...")
        phds: list[PhD] = [PAUPERFORMANCE] + [
            self.get_phd(config_file)
            for config_file in glob.glob(f"{config_dir}/*.ini")
        ]
        logger.info(f"Read {len(phds)} PhDs from {config_dir}.")
        return phds

    def get_phd(
        self,
        config_file_path: str,
    ) -> PhD:
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

        phd: PhD = PhD(
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

    def list_archetypes(self):
        config_dir = self.myr_file_system.RESOURCES_CONFIG_ARCHETYPES_DIR
        logger.info(f"Reading archetypes from {config_dir}...")
        archetypes = [
            self.get_archetype(config_file)
            for config_file in glob.glob(f"{config_dir}/*.ini")
        ]
        logger.info(f"Read {len(archetypes)} archetypes from {config_dir}.")
        return archetypes

    def get_archetype(self, config_file_path: str):
        # TODO: create a proper Archetype class and use it.
        # TODO: ideally merge read_archetype_config with _read_config_file
        config = read_archetype_config(config_file_path)
        logger.debug(f"We should now parse this {config}...")
        # values = config["values"]
        # resources = config["resources"]
        # archetype_name = values["name"]
        # references = config["references"]
        return None  # return Archetype()
