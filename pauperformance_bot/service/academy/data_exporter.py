from pathlib import Path

import jsonpickle
import matplotlib.pyplot as plt
import seaborn

from pauperformance_bot.constant.pauperformance.academy import (
    ACADEMY_FILE_SYSTEM,
    TOP_N_ARCHETYPES_PIE_CHART,
    AcademyFileSystem,
)
from pauperformance_bot.entity.api.archetype import Archetype
from pauperformance_bot.entity.api.deck import Deck, MTGGoldfishTournamentDeck
from pauperformance_bot.entity.api.miscellanea import Changelog, Metagame, Newspauper
from pauperformance_bot.entity.api.video import Video
from pauperformance_bot.entity.config.archetype import ArchetypeConfig
from pauperformance_bot.entity.deck.archive.abstract import AbstractArchivedDeck
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.service.academy.data_loader import AcademyDataLoader
from pauperformance_bot.service.pauperformance.config_reader import ConfigReader
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver.decklassifier import Decklassifier
from pauperformance_bot.service.pauperformance.silver.deckstatistics import (
    DeckstatisticsFactory,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import (
    posix_path,
    safe_dump_json_to_file,
    safe_posix_path,
)

logger = get_application_logger()


class AcademyDataExporter:
    def __init__(
        self,
        pauperformance: PauperformanceService,
        academy_fs: AcademyFileSystem = ACADEMY_FILE_SYSTEM,
    ):
        self.academy_fs: AcademyFileSystem = academy_fs
        self.pauperformance: PauperformanceService = pauperformance
        self.scryfall = self.pauperformance.scryfall
        self.config_reader: ConfigReader = self.pauperformance.config_reader
        self.decks: list[AbstractArchivedDeck] = (
            self.pauperformance.list_archived_decks()
        )
        self.silver: Decklassifier = Decklassifier(self.pauperformance)
        self.academy_loader: AcademyDataLoader = AcademyDataLoader()

    def export_all(self):
        self.export_archetypes()
        self.export_decks()
        self.export_intel_decks()
        self.export_intel_cards()
        # self.export_phd_sheets()
        # self.export_videos()
        # self.export_miscellanea()

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
        for archetype in self.pauperformance.config_reader.list_archetypes():
            # Staples and frequents can be built:
            # a) from archived decks
            # b) from classified decks

            # method a:
            # archetype_decks = [
            #     deck for deck in self.decks if deck.archetype == archetype.name
            # ]
            # staples, frequents = self.pauperformance.analyze_cards_frequency(
            #     archetype_decks
            # )

            # method b:
            statistics = DeckstatisticsFactory(
                self.scryfall, self.academy_loader
            ).build_metadata_for(archetype.name)
            staples, frequents = statistics.get_staple_and_frequent_cards()

            staples = self.scryfall.get_archetype_cards(staples)
            frequents = self.scryfall.get_archetype_cards(frequents)
            api_archetype = Archetype(
                name=archetype.name,
                aliases=archetype.aliases,
                family=archetype.family,
                dominant_mana=archetype.dominant_mana,
                game_type=archetype.game_type,
                description=archetype.description,
                must_have_cards=archetype.must_have_cards,
                must_not_have_cards=archetype.must_not_have_cards,
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
            set_index_entry = self.pauperformance.set_index[int(deck.p12e_code)]
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

    # TODO: clean up this: below it's just a draft
    def export_intel_cards(self):
        logger.info(
            f"Exporting cards intel to {self.academy_fs.ASSETS_DATA_INTEL_CARD_DIR}..."
        )
        cards_intel = {}

        for kd in self.silver.known_decks:
            deck = kd[0]
            arch = kd[1]
            for played_card in deck.mainboard + deck.sideboard:
                if played_card.card_name not in cards_intel:
                    cards_intel[played_card.card_name] = {"archetypes": set()}
                cards_intel[played_card.card_name]["archetypes"].add(arch)
        # TODO: enrich card data
        for card_name, card_data in cards_intel.items():
            safe_dump_json_to_file(
                self.academy_fs.ASSETS_DATA_INTEL_CARD_DIR,
                f"{safe_posix_path(card_name)}.json",
                card_data,
            )

        logger.info(
            f"Exported cards intel to {self.academy_fs.ASSETS_DATA_INTEL_CARD_DIR}."
        )

    def export_miscellanea(self):
        self.export_changelog()
        self.export_newspauper()
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

    def export_metagame(self, top_n_chart=TOP_N_ARCHETYPES_PIE_CHART):
        logger.info(
            f"Exporting Metagame data to {self.academy_fs.ASSETS_DATA_INTEL_DIR}..."
        )
        metagame: Metagame = self.silver.get_metagame()
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
        self.export_twitch_videos()
        self.export_youtube_videos()

    def export_twitch_videos(self):
        logger.info(
            f"Exporting Twitch videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}..."
        )
        self._export_videos(self.pauperformance.storage.list_imported_twitch_videos())
        logger.info(
            f"Exported Twitch videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}."
        )

    def export_youtube_videos(self):
        logger.info(
            f"Exporting YouTube videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}..."
        )
        self._export_videos(self.pauperformance.storage.list_imported_youtube_videos())
        logger.info(
            f"Exported YouTube videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}."
        )

    def _export_videos(self, video_keys):
        for video_key in video_keys:
            video_path = posix_path(
                self.pauperformance.storage.youtube_video_path,
                video_key + ".txt",
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

    def _load_mtggoldfish_tournament_training_data(
        self,
    ) -> list[tuple[PlayableDeck, ArchetypeConfig]]:
        # Note: this method assumes all the decks in the training data are available in
        # the academy as .txt to load and parse.
        archetypes: list[ArchetypeConfig] = (
            self.pauperformance.config_reader.list_archetypes()
        )
        known_decks: list[tuple[PlayableDeck, ArchetypeConfig]] = []
        training_file = (
            self.config_reader.myr_file_system.MTGGOLDFISH_DECK_TRAINING_DATA
        )
        training_data = [
            tuple(line.split(","))
            for line in open(training_file, "r").read().splitlines()
            if line != ""
        ]
        for deck_id, archetype_name in training_data:
            playable_deck_path = posix_path(
                self.academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
                f"{deck_id}.txt",
            )
            playable_deck: PlayableDeck = parse_playable_deck_from_lines(
                [line.strip() for line in open(playable_deck_path).readlines()]
            )
            try:
                archetype = next(a for a in archetypes if a.name == archetype_name)
                known_decks.append((playable_deck, archetype))
            except StopIteration:
                logger.error(
                    f"Unrecognized archetype label '{archetype_name}' for deck with "
                    f"id {deck_id}."
                )
                raise
        # TODO: remove deck_id as soon as manual classification is done
        return known_decks, deck_id

    def export_intel_decks(self):
        logger.info(
            f"Exporting decks intel to {self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR}..."
        )
        # let's help Silver loading some training data
        known_decks, _ = self._load_mtggoldfish_tournament_training_data()
        self.silver.add_known_decks(known_decks)
        # we need to classify all unclassified decks
        self._classify_mtggoldfish_tournament_decks()
        logger.info(
            f"Exported decks intel to {self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR}."
        )

    def _classify_mtggoldfish_tournament_decks(self):
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
                    f"Please, (re)download it first."
                )
                continue  # no tournament, no party: skip the deck
            logger.debug(f"Classifying deck {playable_deck_file}...")
            try:
                playable_deck = parse_playable_deck_from_lines(
                    [line.strip() for line in open(playable_deck_file).readlines()]
                )
            except (IndexError, ValueError):
                logger.warning(f"Unable to parse deck {playable_deck_file}...")
                continue
            most_similar_archetype, highest_similarity = self.silver.classify_deck(
                playable_deck
            )
            if not most_similar_archetype:
                logger.warning("Unable to find similar deck...")
                continue
            logger.debug(
                f"Deck could be {most_similar_archetype.name} ({highest_similarity})."
            )
            if highest_similarity < 0.80:
                logger.debug("Similarity score not sufficient. Skipping deck...")
                unclassified_decks_count += 1
                continue
            logger.debug("Similarity score sufficient. Storing intel...")
            set_index_entry = self.pauperformance.get_set_index_by_date(
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

    def classify_deck(self, playable_deck):
        most_similar_archetype, highest_similarity = self.silver.classify_deck(
            playable_deck
        )
        if not most_similar_archetype:
            logger.warning("Unable to find similar deck...")
            return None, None
        logger.debug(
            f"Deck could be {most_similar_archetype.name} ({highest_similarity})."
        )
        return most_similar_archetype.name, highest_similarity

    # TODO: this is a temporary function to create the dataset
    def _label_mtggoldfish_tournament_decks(self, latest_training_sample):
        banned_cards = [c["name"] for c in self.scryfall.get_banned_cards()]
        already_classified_deck_ids = set(
            p.as_posix().split("/")[-1].replace(".json", "")
            for p in Path(self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR).rglob("*.json")
        )
        unclassified_decks_count = 0
        training_file = (
            self.config_reader.myr_file_system.MTGGOLDFISH_DECK_TRAINING_DATA
        )
        # TODO: get rid of skip_f and skip_list
        skip_f = training_file.replace(".csv", "_skip.csv")
        skip_list = set(
            line for line in open(skip_f, "r").read().splitlines() if line != ""
        )
        for playable_deck_file in sorted(
            Path(self.academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR).glob(
                "*.txt"
            ),
            reverse=True,
            key=lambda d: int(d.as_posix().split("/")[-1].replace(".txt", "")),
        ):
            playable_deck_file = playable_deck_file.as_posix()
            deck_id = playable_deck_file.split("/")[-1].replace(".txt", "")
            if deck_id in already_classified_deck_ids:
                logger.debug(
                    f"Deck {playable_deck_file} already classified. Skipping it..."
                )
                continue
            if deck_id in skip_list:
                logger.debug(f"Deck {playable_deck_file} to be skipped. Skipping it...")
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
                    f"Please, (re)download it first."
                )
                continue  # no tournament, no party: skip the deck
            logger.debug(f"Classifying deck {playable_deck_file}...")
            try:
                playable_deck = parse_playable_deck_from_lines(
                    [line.strip() for line in open(playable_deck_file).readlines()]
                )
            except (IndexError, ValueError):
                logger.warning(f"Unable to parse deck {playable_deck_file}...")
                continue
            most_similar_archetype, highest_similarity = self.silver.classify_deck(
                playable_deck
            )
            if not most_similar_archetype:
                logger.warning("Unable to find similar deck...")
                continue
            logger.debug(
                f"Deck could be {most_similar_archetype.name} ({highest_similarity})."
            )
            if highest_similarity < 0.75:
                logger.debug("Similarity score not sufficient. Skipping deck...")
                unclassified_decks_count += 1
                # continue
                # if "Gorilla Shaman" in playable_deck:
                #     continue
                # if "Ancient Grudge" in playable_deck:
                #     continue
                # if not latest_training_sample or deck_id < latest_training_sample:
                #     logger.warning(
                #         f"Deck could be {most_similar_archetype.name} "
                #         f"({highest_similarity})."
                #     )
                #     url = f"https://www.mtggoldfish.com/deck/{deck_id}"
                #     logger.warning(url)
                # webbrowser.open(url, new=0, autoraise=True)
                # import pyautogui
                # import time
                # import webbrowser
                # pyautogui.keyDown("alt")
                # time.sleep(0.2)
                # pyautogui.press("tab")
                # time.sleep(0.2)
                # pyautogui.keyUp("alt")
                # logger.warning("Yes/Skip/Almost/Brew/No? [Ysabn]")
                # reply = input()
                # print(reply)
                # if reply in ["", "y", "yy"]:
                #     with open(training_file, "a") as out_f:
                #         out_f.write(f"{deck_id},{most_similar_archetype.name}\n")
                #     self.silver.known_decks.append(
                #         (playable_deck, most_similar_archetype)
                #     )
                # elif reply in ["b", "bb", "bbb"]:
                #     with open(training_file, "a") as out_f:
                #         out_f.write(
                #             f"{deck_id},Brew "
                #             f"{most_similar_archetype.name.split(' ')[0]}\n"
                #         )
                # elif reply in ["s", "ss", "sss"]:
                #     with open(skip_f, "a") as out_f:
                #         out_f.write(f"{deck_id}\n")
                # elif reply in ["a", "aa"]:
                #     self.silver.known_decks = []
                #     known_decks, _ = (
                #         self._load_mtggoldfish_tournament_training_data()
                #     )
                #     self.silver.add_known_decks(known_decks)
                #     with open(training_file, "a") as out_f:
                #         out_f.write(
                #             f"{deck_id},"
                #             f"{most_similar_archetype.name.split(' ')[0]} \n"
                #         )
                # else:
                #     pass
                continue
            logger.debug("Similarity score sufficient. Storing intel...")
            set_index_entry = self.pauperformance.get_set_index_by_date(
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
