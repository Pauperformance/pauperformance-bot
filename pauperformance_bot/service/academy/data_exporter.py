import glob
import logging
import os
import time
from pathlib import Path

import jsonpickle

from pauperformance_bot.constant.pauperformance.academy import (
    ACADEMY_FILE_SYSTEM,
    AcademyFileSystem,
)
from pauperformance_bot.entity.api.archetype import Archetype, ArchetypeCard
from pauperformance_bot.entity.api.deck import Deck, MTGGoldfishTournamentDeck
from pauperformance_bot.entity.api.miscellanea import Changelog, Metagame, Newspauper
from pauperformance_bot.entity.api.video import Video
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.entity.deck.archive.abstract import AbstractArchivedDeck
from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.service.academy.academy import AcademyService
from pauperformance_bot.service.mtg.downloader.downloader import MtgoDeckDownloader
from pauperformance_bot.service.pauperformance.config_reader import ConfigReader
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver import SilverService
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path, safe_dump_json_to_file

logger = get_application_logger()
logger.setLevel(logging.WARNING)


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
        # self.export_archetypes()
        # self.export_decks()
        self.export_miscellanea()
        # self.export_phd_sheets()
        # self.export_videos()

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
                posix_path(
                    self.academy_fs.ASSETS_DATA_DECK_ACADEMY_DIR, deck.archetype
                ),
                f"{deck.p12e_name}.json",
                api_deck,
            )
        logger.info(f"Exported decks to {self.academy_fs.ASSETS_DATA_DECK_DIR}.")

    def export_miscellanea(self):
        # self.export_changelog()
        # self.export_newspauper()
        self.export_metagame()

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

    def export_metagame(self):
        logger.info(f"Exporting Metagame to {self.academy_fs.ASSETS_DATA_INTEL_DIR}...")
        silver: SilverService = SilverService(self.pauperformance)
        metagame: Metagame = silver.get_metagame()
        safe_dump_json_to_file(
            self.academy_fs.ASSETS_DATA_INTEL_DIR,
            "metagame.json",
            metagame,
        )
        logger.info(f"Exported Metagame to {self.academy_fs.ASSETS_DATA_INTEL_DIR}.")

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

    # TODO: remove if/when possible
    def _get_known_decks(self) -> list[tuple[PlayableDeck, ArchetypeConfig]]:
        archetypes: list[
            ArchetypeConfig
        ] = self.pauperformance.config_reader.list_archetypes()
        manual_tags = [
            ("https://www.mtggoldfish.com/deck/165690#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/89107#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/35472#online", "Orzhov TortEx"),
            ("https://www.mtggoldfish.com/deck/1503048#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/307573#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/265942#online", "Dimir Delver"),
            ("https://www.mtggoldfish.com/deck/320970#online", "Abzan TortEx"),
            ("https://www.mtggoldfish.com/deck/191116#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/201858#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/257820#online", "Burn"),
            ("https://www.mtggoldfish.com/deck/57237#online", "Goblins"),
            ("https://www.mtggoldfish.com/deck/95703#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/25237#online", "Esper Familiars"),
            ("https://www.mtggoldfish.com/deck/53337#online", "Infect"),
            ("https://www.mtggoldfish.com/deck/609285#online", "Izzet Faeries"),
            ("https://www.mtggoldfish.com/deck/3101802#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/192241#online", "Familiars"),
            ("https://www.mtggoldfish.com/deck/208356#online", "Esper Familiars"),
            ("https://www.mtggoldfish.com/deck/237912#online", "Burn"),
            ("https://www.mtggoldfish.com/deck/2717333#online", "Jeskai Ephemerate"),
            ("https://www.mtggoldfish.com/deck/806954#online", "Flicker Tron"),
            ("https://www.mtggoldfish.com/deck/613671#online", "Red Deck Wins"),
            ("https://www.mtggoldfish.com/deck/256460#online", "Izzet Blitz"),
            ("https://www.mtggoldfish.com/deck/2739463#online", "Brew"),
            ("https://www.mtggoldfish.com/deck/4433748#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/1134581#online", "MonoW Heroic"),
            ("https://www.mtggoldfish.com/deck/192214#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/361953#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/1020888#online", "Flicker Tron"),
            ("https://www.mtggoldfish.com/deck/219799#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/233627#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/3762821#online", "MonoB Suicide"),
            ("https://www.mtggoldfish.com/deck/225844#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/4558872#online", "Elves"),
            ("https://www.mtggoldfish.com/deck/294806#online", "Burn"),
            ("https://www.mtggoldfish.com/deck/216511#online", "Burn"),
            ("https://www.mtggoldfish.com/deck/997993#online", "Goblins"),
            ("https://www.mtggoldfish.com/deck/2823243#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/222548#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/2120164#online", "Flicker Tron"),
            ("https://www.mtggoldfish.com/deck/246484#online", "Bogles"),
            ("https://www.mtggoldfish.com/deck/196853#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/369951#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/295056#online", "Acid Trip"),
            ("https://www.mtggoldfish.com/deck/219727#online", "Izzet Blitz"),
            ("https://www.mtggoldfish.com/deck/248028#online", "White Weenie"),
            (
                "https://www.mtggoldfish.com/deck/65257#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/280188#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/19108#online", "Esper Familiars"),
            (
                "https://www.mtggoldfish.com/deck/17250#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/826943#online", "Flicker Tron"),
            (
                "https://www.mtggoldfish.com/deck/21865#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/443455#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/198528#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/49187#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/25297#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/38273#online", "Golgari TortEx"),
            ("https://www.mtggoldfish.com/deck/20432#online", "Esper Familiars"),
            ("https://www.mtggoldfish.com/deck/375769#online", "Bogles"),
            (
                "https://www.mtggoldfish.com/deck/102606#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/3882#online", "Izzet 8-Post"),
            (
                "https://www.mtggoldfish.com/deck/39712#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/352176#online", "Slivers"),
            ("https://www.mtggoldfish.com/deck/3996759#online", "Golgari TortEx"),
            ("https://www.mtggoldfish.com/deck/222096#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/187644#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/182266#online", "Izzet 8-Post"),
            (
                "https://www.mtggoldfish.com/deck/148003#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/188272#online", "Trinket Control"),
            ("https://www.mtggoldfish.com/deck/660917#online", "Dimir Control"),
            ("https://www.mtggoldfish.com/deck/131043#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/97038#online", "Affinity"),
            (
                "https://www.mtggoldfish.com/deck/155630#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/35795#online", "Dimir 8-Post"),
            ("https://www.mtggoldfish.com/deck/109429#online", "MonoB Control"),
            (
                "https://www.mtggoldfish.com/deck/102381#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/69434#online", "Esper Familiars"),
            ("https://www.mtggoldfish.com/deck/203761#online", "Izzet 8-Post"),
            ("https://www.mtggoldfish.com/deck/136556#online", "Izzet 8-Post"),
            ("https://www.mtggoldfish.com/deck/51150#online", "Infect"),
            ("https://www.mtggoldfish.com/deck/30181#online", "Goblins"),
            ("https://www.mtggoldfish.com/deck/185644#online", "Familiars"),
            ("https://www.mtggoldfish.com/deck/1933307#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/800091#online", "Inside Out"),
            ("https://www.mtggoldfish.com/deck/194478#online", "MonoU 8-Post"),
            ("https://www.mtggoldfish.com/deck/177648#online", "Goblins"),
            ("https://www.mtggoldfish.com/deck/112487#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/604436#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/182044#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/15004#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/3059914#online", "Orzhov Pestilence"),
            ("https://www.mtggoldfish.com/deck/884869#online", "Dimir Alchemy"),
            ("https://www.mtggoldfish.com/deck/99691#online", "MonoU Delver"),
        ]
        known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = []
        for deck_url, archetype_name in manual_tags:
            download_url = deck_url.replace("/deck", "/deck/download")
            deck_downloader = MtgoDeckDownloader(download_url)
            playable_deck = deck_downloader.download()
            archetype = next(a for a in archetypes if a.name == archetype_name)
            known_decks.append((playable_deck, archetype))
            time.sleep(1)
        return known_decks

    def export_intel_decks(self):
        logger.info(
            f"Exporting decks intel to {self.academy_fs.ASSETS_DATA_INTEL_DIR}..."
        )
        known_decks = self._get_known_decks()  # let's help Silver
        silver: SilverService = SilverService(self.pauperformance, known_decks)
        banned_cards = [c["name"] for c in self.scryfall.get_banned_cards()]
        for deck_file in glob.glob(
            f"{self.academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_DIR}{os.sep}*.json"
        ):
            if any(
                deck_file.rsplit("/")[-1] in p.as_posix()
                for p in Path(self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR).rglob(
                    "*.json"
                )
            ):
                logger.debug(
                    f"Deck {deck_file.rsplit('/')[-1]} already classified. "
                    f"Skipping it..."
                )
                continue
            time.sleep(4)
            tournament_deck: MTGGoldfishTournamentDeck = jsonpickle.decode(
                open(deck_file).read()
            )
            logger.debug(f"Classifying deck at {tournament_deck.url}...")
            download_url = tournament_deck.url.replace("/deck", "/deck/download")
            deck_downloader = MtgoDeckDownloader(download_url)
            try:
                playable_deck = deck_downloader.download()
                most_similar_archetype, highest_similarity = silver.classify_deck(
                    playable_deck
                )
                logger.debug(
                    f"Deck could be {most_similar_archetype.name} "
                    f"({highest_similarity})."
                )
                if "Boros" in most_similar_archetype.name:  # TODO: remove
                    continue
                if highest_similarity < 0.80:
                    logger.debug("Similarity score not sufficient. Skipping deck...")
                    logger.warning(tournament_deck.url)
                    continue
                logger.debug("Similarity score sufficient. Storing intel...")
                set_index_entry = self.academy.pauperformance.get_set_index_by_date(
                    usa_date=tournament_deck.tournament_date
                )
                api_deck: Deck = Deck(
                    name=tournament_deck.archetype,
                    url=tournament_deck.url,
                    archetype=most_similar_archetype.name,
                    set_name=set_index_entry["name"],
                    set_date=set_index_entry["date"],
                    legal=playable_deck.is_legal(banned_cards),
                )
                safe_dump_json_to_file(
                    posix_path(
                        self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR, api_deck.archetype
                    ),
                    f"{tournament_deck.identifier}.json",
                    api_deck,
                )
            except Exception:  # TODO: remove
                logger.warning(f"Exception while processing {deck_file}...")
        logger.info(f"Exported decks intel to {self.academy_fs.ASSETS_DATA_INTEL_DIR}.")
