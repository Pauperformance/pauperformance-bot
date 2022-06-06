from pauperformance_bot.constant.academy import ACADEMY_FILE_SYSTEM, AcademyFileSystem
from pauperformance_bot.entity.api.archetype import (
    Archetype,
    ArchetypeCard,
    DiscordResource,
    Resource,
    SideboardResource,
)
from pauperformance_bot.entity.api.deck import Deck
from pauperformance_bot.entity.api.miscellanea import Newspauper
from pauperformance_bot.entity.api.video import Video
from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.config_reader import ConfigReader
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path, safe_dump_json_to_file

logger = get_application_logger()


class AcademyDataExporter:
    def __init__(
        self,
        academy: AcademyService,
        academy_fs: AcademyFileSystem = ACADEMY_FILE_SYSTEM,
    ):
        self.academy: AcademyService = academy
        self.academy_fs: AcademyFileSystem = academy_fs
        self.pauperformance: PauperformanceService = academy.pauperformance
        self.scryfall = self.pauperformance.scryfall
        self.config_reader: ConfigReader = self.pauperformance.config_reader

    def export_all(self):
        self.export_archetypes()
        self.export_decks()
        self.export_miscellanea()
        self.export_phd_sheets()
        self.export_videos()

    def export_phd_sheets(self):
        logger.info(f"Exporting phd sheets to {self.academy_fs.ASSETS_DATA_PHD_DIR}...")
        for phd_sheet in self.config_reader.list_phd_sheets(
            scryfall_service=self.scryfall
        ):
            safe_dump_json_to_file(
                self.academy_fs.ASSETS_DATA_PHD_DIR,
                f"{phd_sheet.name}.json",
                phd_sheet,
            )
        logger.info(f"Exported phd sheets to {self.academy_fs.ASSETS_DATA_PHD_DIR}.")

    def export_archetypes(self):
        logger.info(
            f"Exporting archetypes to {self.academy_fs.ASSETS_DATA_ARCHETYPE_DIR}..."
        )
        all_decks = self.academy.pauperformance.list_archived_decks()
        for archetype in self.academy.pauperformance.config_reader.list_archetypes():
            archetype_decks = [
                deck for deck in all_decks if deck.archetype == archetype.name
            ]
            staples, frequents = self.academy.pauperformance.analyze_cards_frequency(
                archetype_decks
            )
            staples = [
                ArchetypeCard(
                    name=card["name"],
                    link=card["page_url"],
                    preview=card["image_url"],
                )
                # TODO: refactor
                for card in self.academy._get_rendered_card_info(staples)
            ]
            frequents = [
                ArchetypeCard(
                    name=card["name"],
                    link=card["page_url"],
                    preview=card["image_url"],
                )
                # TODO: refactor
                for card in self.academy._get_rendered_card_info(frequents)
            ]
            api_archetype = Archetype(
                name=archetype.name,
                aliases=archetype.aliases,
                family=archetype.family,
                dominant_mana=archetype.dominant_mana,
                game_type=archetype.game_type,
                description=archetype.description,
                reference_decks=archetype.reference_decks,
                resource_sideboard=archetype.resource_sideboard,
                resources_discord=archetype.resources_discord,
                resources=archetype.resources,
                staples=staples,
                frequent=frequents,
            )
            safe_dump_json_to_file(
                self.academy_fs.ASSETS_DATA_ARCHETYPE_DIR,
                f"{archetype.name}.json",
                api_archetype,
            )
        logger.info(
            f"Exported archetypes to {self.academy_fs.ASSETS_DATA_ARCHETYPE_DIR}."
        )

    def export_decks(self):
        self._tmp_export_synthetic_decks()

    def export_miscellanea(self):
        self.export_newspauper()

    def export_newspauper(self):
        logger.info(f"Exporting newspauper to {self.academy_fs.ASSETS_DATA_DIR}...")
        newspauper: Newspauper = self.config_reader.get_newspauper()
        safe_dump_json_to_file(
            self.academy_fs.ASSETS_DATA_DIR,
            "newspauper.json",
            newspauper,
        )
        logger.info(f"Exported newspauper to {self.academy_fs.ASSETS_DATA_DIR}.")

    def export_videos(self):
        # self.export_twitch_videos()  # TODO
        self.export_youtube_videos()

    def export_youtube_videos(self):
        logger.info(
            f"Exporting YouTube videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}..."
        )
        for video_key in self.pauperformance.storage.list_imported_youtube_videos():
            video_id, phd_name, language, date, deck_name = video_key.split(">")
            archetype = deck_name.split(".", maxsplit=1)[0].rsplit(" ", maxsplit=1)[0]
            video_path = posix_path(
                self.pauperformance.storage.youtube_video_path,
                video_key + ".txt",  # TODO: get rid of this
            )
            video_json = self.pauperformance.storage.get_file(video_path)
            video: Video = Video(
                name=video_json["title"],
                link=video_json["url"],
                language=language,
                phd_name=phd_name,
                date=date,
                archetype=archetype,
                video_id=video_id,
                deck_name=deck_name,
            )
            safe_dump_json_to_file(
                posix_path(self.academy_fs.ASSETS_DATA_VIDEO_DIR, video.archetype),
                f"{video.video_id}.json",
                video,
            )
        logger.info(
            f"Exported YouTube videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}."
        )

    def _tmp_export_synthetic_decks(self):
        logger.info(f"Exporting decks to {self.academy_fs.ASSETS_DATA_DECK_DIR}...")
        decks: list[Deck] = []
        deck: Deck = Deck(
            name="Stompy 722.001.tarmogoyf_ita",
            url="https://www.mtggoldfish.com/deck/4680163",
            archetype="Stompy",
            set_name="Kamigawa: Neon Dynasty",
            set_date="2022-02-18",
            legal=True,
        )
        decks.append(deck)
        deck: Deck = Deck(
            name="Stompy 696.001.Ixidor29",
            url="https://www.mtggoldfish.com/deck/4624367",
            archetype="Stompy",
            set_name="	Innistrad: Midnight Hunt",
            set_date="2021-09-24",
            legal=True,
        )
        decks.append(deck)
        deck: Deck = Deck(
            name="Stompy 722.002.tarmogoyf_ita",
            url="https://www.mtggoldfish.com/deck/4706455",
            archetype="Stompy",
            set_name="Kamigawa: Neon Dynasty",
            set_date="2022-02-18",
            legal=True,
        )
        decks.append(deck)
        for deck in decks:
            safe_dump_json_to_file(
                posix_path(self.academy_fs.ASSETS_DATA_DECK_DIR, deck.archetype),
                f"{deck.name}.json",
                deck,
            )
        logger.info(f"Exported decks to {self.academy_fs.ASSETS_DATA_DECK_DIR}.")
