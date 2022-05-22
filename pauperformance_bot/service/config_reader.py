import configparser
import glob

from pauperformance_bot.constant.myr import CONFIG_PHDS_DIR
from pauperformance_bot.entity.api.phd_sheet import PhDSheet
from pauperformance_bot.service.scryfall import ScryfallService
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


class ConfigReader:
    @staticmethod
    def _read_config_file(config_file_path):
        logger.debug(f"Reading configuration file {config_file_path}...")
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option  # preserve case
        config.read(config_file_path)
        logger.debug(f"Read configuration file {config_file_path}.")
        return config

    def list_phd_sheets(
        self,
        config_dir: str = CONFIG_PHDS_DIR,
        scryfall_service: ScryfallService = ScryfallService(),
    ) -> list[PhDSheet]:
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
