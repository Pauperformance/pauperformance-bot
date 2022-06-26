import logging
from pathlib import Path

import jsonpickle
import matplotlib.pyplot as plt
import seaborn

from pauperformance_bot.constant.pauperformance.academy import (
    ACADEMY_FILE_SYSTEM,
    TOP_N_ARCHETYPES_PIE_CHART,
    AcademyFileSystem,
)
from pauperformance_bot.entity.api.archetype import Archetype, ArchetypeCard
from pauperformance_bot.entity.api.deck import Deck, MTGGoldfishTournamentDeck
from pauperformance_bot.entity.api.miscellanea import Changelog, Metagame, Newspauper
from pauperformance_bot.entity.api.video import Video
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.entity.deck.archive.abstract import AbstractArchivedDeck
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.service.academy.academy import AcademyService
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
        # self.export_miscellanea()
        # self.export_phd_sheets()
        # self.export_videos()
        pass

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
        # self.export_metagame()
        pass

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

    def export_metagame(self, top_n_chart=TOP_N_ARCHETYPES_PIE_CHART):
        logger.info(
            f"Exporting Metagame data to {self.academy_fs.ASSETS_DATA_INTEL_DIR}..."
        )
        silver: SilverService = SilverService(self.pauperformance)
        metagame: Metagame = silver.get_metagame()
        safe_dump_json_to_file(
            self.academy_fs.ASSETS_DATA_INTEL_DIR,
            "metagame.json",
            metagame,
        )
        logger.info(
            f"Exported Metagame data to {self.academy_fs.ASSETS_DATA_INTEL_DIR}."
        )
        logger.info(
            f"Exporting Metagame picture to {self.academy_fs.ASSETS_DATA_INTEL_DIR}..."
        )
        data = []
        labels = []
        for meta_share in sorted(metagame.meta_shares, reverse=True):
            data.append(meta_share.meta_share)
            labels.append(meta_share.archetype_name)
        colors = seaborn.color_palette("colorblind", n_colors=top_n_chart + 1)
        other_meta = sum(data[top_n_chart:])
        data = data[:top_n_chart]
        data.append(other_meta)
        labels = labels[:top_n_chart]
        labels.append("Other")
        plt.figure(figsize=(7, 7))
        plt.pie(data, labels=labels, colors=colors, autopct="%.0f%%")
        plt.savefig(posix_path(self.academy_fs.ASSETS_DATA_INTEL_DIR, "metagame.png"))
        logger.info(
            f"Exported Metagame picture to {self.academy_fs.ASSETS_DATA_INTEL_DIR}."
        )

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
            ("https://www.mtggoldfish.com/deck/193618#online", "Izzet 8-Post"),
            ("https://www.mtggoldfish.com/deck/193686#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/4315445#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/1716388#online", "Flicker Tron"),
            ("https://www.mtggoldfish.com/deck/472450#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/2656936#online", "Boros Monarch"),
            ("https://www.mtggoldfish.com/deck/4486046#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/163605#online", "Izzet 8-Post"),
            ("https://www.mtggoldfish.com/deck/1269313#online", "MonoB Ponza"),
            ("https://www.mtggoldfish.com/deck/3378642#online", "MonoW Heroic"),
            (
                "https://www.mtggoldfish.com/deck/102380#online",
                "Empty The Warrens Storm",
            ),
            (
                "https://www.mtggoldfish.com/deck/118871#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/937125#online", "Dimir Delver"),
            (
                "https://www.mtggoldfish.com/deck/129793#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/33728#online", "Burn"),
            (
                "https://www.mtggoldfish.com/deck/118871#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/321531#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/180711#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/81081#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/4182914#online", "Cycling Storm"),
            ("https://www.mtggoldfish.com/deck/448174#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/3962634#online", "Flicker Tron"),
            ("https://www.mtggoldfish.com/deck/3895663#online", "Red Deck Wins"),
            ("https://www.mtggoldfish.com/deck/3415146#online", "Acid Trip"),
            ("https://www.mtggoldfish.com/deck/76956#online", "Red Deck Wins"),
            ("https://www.mtggoldfish.com/deck/2435059#online", "Flicker Tron"),
            ("https://www.mtggoldfish.com/deck/862949#online", "Inside Out"),
            ("https://www.mtggoldfish.com/deck/32365#online", "White Weenie"),
            ("https://www.mtggoldfish.com/deck/4366056#online", "MonoW Heroic"),
            ("https://www.mtggoldfish.com/deck/2972098#online", "Red Deck Wins"),
            ("https://www.mtggoldfish.com/deck/3432743#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/152476#online", "Esper Familiars"),
            ("https://www.mtggoldfish.com/deck/650045#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/4854331#online", "Boros Bully"),
            ("https://www.mtggoldfish.com/deck/1488534#online", "Dimir Control"),
            ("https://www.mtggoldfish.com/deck/4284478#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/35330#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/249503#online", "Izzet Faeries"),
            ("https://www.mtggoldfish.com/deck/1156935#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/3760141#online", "Walls"),
            ("https://www.mtggoldfish.com/deck/2162401#online", "Orzhov Pestilence"),
            ("https://www.mtggoldfish.com/deck/193609#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/654678#online", "Slivers"),
            ("https://www.mtggoldfish.com/deck/111269#online", "Infect"),
            ("https://www.mtggoldfish.com/deck/498473#online", "Izzet Blitz"),
            ("https://www.mtggoldfish.com/deck/770861#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/147490#online", "Bogles"),
            ("https://www.mtggoldfish.com/deck/3650797#online", "Familiars"),
            ("https://www.mtggoldfish.com/deck/112300#online", "White Weenie"),
            ("https://www.mtggoldfish.com/deck/50697#online", "Burn"),
            ("https://www.mtggoldfish.com/deck/101331#online", "MonoU Delver"),
            ("https://www.mtggoldfish.com/deck/749969#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/15903#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/1111449#online", "Slivers"),
            ("https://www.mtggoldfish.com/deck/4265788#online", "MonoW Heroic"),
            ("https://www.mtggoldfish.com/deck/361902#online", "Esper Familiars"),
            ("https://www.mtggoldfish.com/deck/3892355#online", "Boros Monarch"),
            ("https://www.mtggoldfish.com/deck/166294#online", "White Weenie"),
            ("https://www.mtggoldfish.com/deck/117461#online", "Trinket Control"),
            ("https://www.mtggoldfish.com/deck/62937#online", "Goblins"),
            ("https://www.mtggoldfish.com/deck/3776807#online", "Acid Trip"),
            ("https://www.mtggoldfish.com/deck/160902#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/736212#online", "Dimir Teachings"),
            ("https://www.mtggoldfish.com/deck/303994#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/15979#online", "Izzet 8-Post"),
            ("https://www.mtggoldfish.com/deck/174283#online", "Dimir Flicker"),
            ("https://www.mtggoldfish.com/deck/62581#online", "Izzet 8-Post"),
            ("https://www.mtggoldfish.com/deck/2565335#online", "Elves"),
            ("https://www.mtggoldfish.com/deck/1298251#online", "Dimir Control"),
            ("https://www.mtggoldfish.com/deck/3963688#online", "Jund Cascade"),
            ("https://www.mtggoldfish.com/deck/60628#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/393384#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/266509#online", "Esper Familiars"),
            ("https://www.mtggoldfish.com/deck/190851#online", "Izzet Blitz"),
            ("https://www.mtggoldfish.com/deck/2208921#online", "Boros Monarch"),
            ("https://www.mtggoldfish.com/deck/1716390#online", "Inside Out"),
            ("https://www.mtggoldfish.com/deck/29940#online", "Izzet 8-Post"),
            ("https://www.mtggoldfish.com/deck/190685#online", "Izzet Blitz"),
            ("https://www.mtggoldfish.com/deck/4165549#online", "White Weenie"),
            ("https://www.mtggoldfish.com/deck/98930#online", "Goblins"),
            ("https://www.mtggoldfish.com/deck/264409#online", "Bogles"),
            ("https://www.mtggoldfish.com/deck/179895#online", "Goblins"),
            (
                "https://www.mtggoldfish.com/deck/93140#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/19155#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/184600#online", "Burn"),
            ("https://www.mtggoldfish.com/deck/258484#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/456953#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/653781#online", "Golgari TortEx"),
            (
                "https://www.mtggoldfish.com/deck/93322#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/39713#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/278744#online", "Izzet Blitz"),
            ("https://www.mtggoldfish.com/deck/112610#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/354104#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/1006029#online", "Boros Monarch"),
            ("https://www.mtggoldfish.com/deck/2908770#online", "Familiars"),
            ("https://www.mtggoldfish.com/deck/115527#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/146245#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/3808077#online", "Flicker Tron"),
            ("https://www.mtggoldfish.com/deck/30208#online", "Dimir 8-Post"),
            ("https://www.mtggoldfish.com/deck/149931#online", "White Weenie"),
            ("https://www.mtggoldfish.com/deck/3668368#online", "Elves"),
            ("https://www.mtggoldfish.com/deck/696153#online", "Izzet Blitz"),
            ("https://www.mtggoldfish.com/deck/218996#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/2940582#online", "Dimir Delver"),
            ("https://www.mtggoldfish.com/deck/218996#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/208687#online", "Acid Trip"),
            ("https://www.mtggoldfish.com/deck/219895#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/4602587#online", "Gruul Ponza"),
            ("https://www.mtggoldfish.com/deck/198886#online", "Burn"),
            ("https://www.mtggoldfish.com/deck/2578982#online", "Stompy"),
            (
                "https://www.mtggoldfish.com/deck/170186#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/73174#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/133481#online", "MonoU Delver"),
            ("https://www.mtggoldfish.com/deck/4871133#online", "Turbofog"),
            ("https://www.mtggoldfish.com/deck/121072#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/359696#online", "MonoU Faeries"),
            (
                "https://www.mtggoldfish.com/deck/112305#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/79939#online", "Dimir 8-Post"),
            (
                "https://www.mtggoldfish.com/deck/170250#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/3574909#online", "Orzhov Pestilence"),
            ("https://www.mtggoldfish.com/deck/205640#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/171526#online", "MonoU Delver"),
            ("https://www.mtggoldfish.com/deck/188371#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/124280#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/308338#online", "Dimir Delver"),
            ("https://www.mtggoldfish.com/deck/453998#online", "Bogles"),
            ("https://www.mtggoldfish.com/deck/408405#online", "Affinity"),
            ("https://www.mtggoldfish.com/deck/280102#online", "MonoU Delver"),
            ("https://www.mtggoldfish.com/deck/4755505#online", "Boros Synth"),
            ("https://www.mtggoldfish.com/deck/183637#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/2033573#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/421440#online", "Bogles"),
            ("https://www.mtggoldfish.com/deck/222387#online", "MonoB Control"),
            ("https://www.mtggoldfish.com/deck/163822#online", "White Weenie"),
            ("https://www.mtggoldfish.com/deck/3669879#online", "MonoW Heroic"),
            (
                "https://www.mtggoldfish.com/deck/108126#online",
                "Empty The Warrens Storm",
            ),
            ("https://www.mtggoldfish.com/deck/244378#online", "Izzet Faeries"),
            ("https://www.mtggoldfish.com/deck/166340#online", "Infect"),
            ("https://www.mtggoldfish.com/deck/559608#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/4824607#online", "Stompy"),
            ("https://www.mtggoldfish.com/deck/3099428#online", "Jeskai Ephemerate"),
            ("https://www.mtggoldfish.com/deck/83731#online", "MonoU Faeries"),
            ("https://www.mtggoldfish.com/deck/247764#online", "Golgari TortEx"),
            ("https://www.mtggoldfish.com/deck/259542#online", "Burn"),
        ]
        known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = []
        for deck_url, archetype_name in manual_tags:
            mtggoldfish_deck_id = deck_url.replace("#online", "").rsplit("/")[-1]
            playable_deck_path = posix_path(
                self.academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
                f"{mtggoldfish_deck_id}.txt",
            )
            playable_deck: PlayableDeck = parse_playable_deck_from_lines(
                [line.strip() for line in open(playable_deck_path).readlines()]
            )
            try:
                archetype = next(a for a in archetypes if a.name == archetype_name)
                known_decks.append((playable_deck, archetype))
            except StopIteration:
                logger.error(f"Wrong manual tag for archetype {archetype_name}.")
                raise
        return known_decks

    def export_intel_decks(self):
        logger.info(
            f"Exporting decks intel to {self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR}..."
        )
        known_decks = self._get_known_decks()  # let's help Silver
        silver: SilverService = SilverService(self.pauperformance, known_decks)
        # we need to classify all unclassified decks
        self._classify_mtggoldfish_tournament_decks(silver)

    def _classify_mtggoldfish_tournament_decks(self, silver: SilverService):
        banned_cards = [c["name"] for c in self.scryfall.get_banned_cards()]
        already_classified_deck_ids = set(
            p.as_posix().split("/")[-1].replace(".json", "")
            for p in Path(self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR).rglob("*.json")
        )
        unclassified_decks_count = 0
        for playable_deck_file in Path(
            self.academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR
        ).glob("*.txt"):
            playable_deck_file = playable_deck_file.as_posix()
            deck_id = playable_deck_file.split("/")[-1].replace(".txt", "")
            if deck_id in already_classified_deck_ids:
                logger.debug(
                    f"Deck {playable_deck_file} already classified. Skipping it..."
                )
                continue
            # A PlayableDeck has no knowledge about the time it was created.
            # This information is stored in the tournament metadata for the deck.
            tournament_deck_path = posix_path(
                self.academy_fs.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DECKS_DIR,
                f"{deck_id}.json",
            )
            try:
                tournament_deck: MTGGoldfishTournamentDeck = jsonpickle.decode(
                    open(tournament_deck_path).read()
                )
            except FileNotFoundError:
                logger.warning(
                    f"Unable to find tournament deck metadata: {tournament_deck_path}. "
                    f"Please, download it first."
                )
                continue  # no tournament, no party: skip the deck
            logger.debug(f"Classifying deck {playable_deck_file}...")
            playable_deck = parse_playable_deck_from_lines(
                [line.strip() for line in open(playable_deck_file).readlines()]
            )
            most_similar_archetype, highest_similarity = silver.classify_deck(
                playable_deck
            )
            logger.debug(
                f"Deck could be {most_similar_archetype.name} "
                f"({highest_similarity})."
            )
            if highest_similarity < 0.80:
                logger.debug("Similarity score not sufficient. Skipping deck...")
                unclassified_decks_count += 1
                # logger.warning(f"https://www.mtggoldfish.com/deck/{deck_id}")
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
                f"{deck_id}.json",
                api_deck,
            )
        logger.info(f"Classified decks: {len(already_classified_deck_ids)}")
        logger.warning(f"Unclassified decks: {unclassified_decks_count}")
        logger.info(
            f"Exported decks intel to {self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR}."
        )
