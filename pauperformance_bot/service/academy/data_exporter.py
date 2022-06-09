from pauperformance_bot.constant.pauperformance.academy import (
    ACADEMY_FILE_SYSTEM,
    AcademyFileSystem,
)
from pauperformance_bot.entity.api.archetype import Archetype, ArchetypeCard
from pauperformance_bot.entity.api.deck import Deck
from pauperformance_bot.entity.api.miscellanea import Changelog, Newspauper
from pauperformance_bot.entity.api.video import Video
from pauperformance_bot.entity.deck.archive.abstract import AbstractArchivedDeck
from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.pauperformance.config_reader import ConfigReader
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
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
        self.decks: list[
            AbstractArchivedDeck
        ] = self.academy.pauperformance.list_archived_decks()

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
        for archetype in self.academy.pauperformance.config_reader.list_archetypes():
            archetype_decks = [
                deck for deck in self.decks if deck.archetype == archetype.name
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
        logger.info(f"Exporting decks to {self.academy_fs.ASSETS_DATA_DECK_DIR}...")
        banned_cards = [c["name"] for c in self.scryfall.get_banned_cards()]
        for deck in self.decks:
            set_index_entry = self.academy.pauperformance.set_index[int(deck.p12e_code)]
            playable_deck: PlayableDeck = self.pauperformance.archive.to_playable_deck(
                deck
            )
            api_deck: Deck = Deck(
                name=deck.p12e_name,
                url=deck.url,
                archetype=deck.archetype,
                set_name=set_index_entry["name"],
                set_date=set_index_entry["date"],
                legal=playable_deck.is_legal(banned_cards),
            )
            safe_dump_json_to_file(
                posix_path(self.academy_fs.ASSETS_DATA_DECK_DIR, deck.archetype),
                f"{deck.p12e_name}.json",
                api_deck,
            )
        logger.info(f"Exported decks to {self.academy_fs.ASSETS_DATA_DECK_DIR}.")

    def export_miscellanea(self):
        self.export_changelog()
        self.export_newspauper()

    def export_changelog(self):
        logger.info(f"Exporting Changelog to {self.academy_fs.ASSETS_DATA_DIR}...")
        changelog: Changelog = self.config_reader.get_changelog()
        safe_dump_json_to_file(
            self.academy_fs.ASSETS_DATA_DIR,
            "changelog.json",
            changelog,
        )
        logger.info(f"Exported Changelog to {self.academy_fs.ASSETS_DATA_DIR}.")

    def export_newspauper(self):
        logger.info(f"Exporting Newspauper to {self.academy_fs.ASSETS_DATA_DIR}...")
        newspauper: Newspauper = self.config_reader.get_newspauper()
        safe_dump_json_to_file(
            self.academy_fs.ASSETS_DATA_DIR,
            "newspauper.json",
            newspauper,
        )
        logger.info(f"Exported Newspauper to {self.academy_fs.ASSETS_DATA_DIR}.")

    def export_videos(self):
        # self.export_twitch_videos()
        self.export_youtube_videos()

    def export_youtube_videos(self):
        logger.info(
            f"Exporting YouTube videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}..."
        )
        for video_key in self.pauperformance.storage.list_imported_youtube_videos():
            video_path = posix_path(
                self.pauperformance.storage.youtube_video_path,
                video_key + ".txt",  # TODO: get rid of this
            )
            video_json = self.pauperformance.storage.get_file(video_path)
            video_id, phd_name, _, date, _ = video_key.split(">")
            video: Video = Video(
                name=video_json["title"],
                link=video_json["url"],
                language=video_json["language"],
                phd_name=phd_name,
                date=date,
                archetype=video_json["archetype"],
                video_id=video_id,
                deck_name=video_json["deck_name"],
            )
            safe_dump_json_to_file(
                posix_path(self.academy_fs.ASSETS_DATA_VIDEO_DIR, video.archetype),
                f"{video.video_id}.json",
                video,
            )
        logger.info(
            f"Exported YouTube videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}."
        )
