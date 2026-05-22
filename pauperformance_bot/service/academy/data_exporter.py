import collections
import csv
import shutil
from pathlib import Path

import jsonpickle
import matplotlib.pyplot as plt
import seaborn

from pauperformance_bot.constant.pauperformance.academy import (
    ACADEMY_FILE_SYSTEM,
    TOP_N_ARCHETYPES_PIE_CHART,
    AcademyFileSystem,
)
from pauperformance_bot.constant.pauperformance.silver import (
    BREW_CLASSIFICATION_THRESHOLD,
)
from pauperformance_bot.entity.api.archetype import Archetype
from pauperformance_bot.entity.api.deck import Deck, MTGGoldfishTournamentDeck
from pauperformance_bot.entity.api.miscellanea import Changelog, Metagame, Newspauper
from pauperformance_bot.entity.api.video import Video
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
from pauperformance_bot.util.naming import fix_card_name
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
        self.decklassifier: Decklassifier = Decklassifier(pauperformance, academy_fs)
        self.academy_loader: AcademyDataLoader = AcademyDataLoader()

    def export_all(self):
        # TODO: remove each (relevant) folder before re-exporting to avoid stale files
        # self.export_miscellanea()
        # self.export_creator_sheets()
        # self.export_archetypes()
        # self.export_decks()
        # self.export_youtube_videos()
        # self.export_intel_cards()
        self.export_intel_decks()

    def export_creator_sheets(self):
        logger.info(
            f"Exporting creator sheets to {self.academy_fs.ASSETS_DATA_CREATOR_DIR}..."
        )
        for sheet in self.config_reader.list_creator_sheets():
            safe_dump_json_to_file(
                self.academy_fs.ASSETS_DATA_CREATOR_DIR,
                f"{sheet.name}.json",
                sheet,
            )
        logger.info(
            f"Exported creator sheets to {self.academy_fs.ASSETS_DATA_CREATOR_DIR}."
        )

    def export_archetypes(self):
        logger.info(
            f"Exporting archetypes to {self.academy_fs.ASSETS_DATA_ARCHETYPE_DIR}..."
        )
        for archetype in self.pauperformance.config_reader.list_archetypes():
            logger.debug(f"Processing archetype {archetype}...")
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
            logger.debug(f"Processed archetype {archetype}.")
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
        archetypes_index = collections.defaultdict(set)
        logger.debug("Loading archetypes for each card...")
        for known_deck in self.decklassifier.known_decks:
            deck, arch = known_deck
            for played_card in deck.mainboard + deck.sideboard:
                card = fix_card_name(played_card.card_name)
                archetypes_index[card].add(arch.name)

        for set_index, scryfall_cards in self.pauperformance.card_index.items():
            logger.debug(f"Processing set: {set_index}...")
            for scryfall_card in scryfall_cards:
                card_name = scryfall_card["name"]
                cards_intel[card_name] = {}
                cards_intel[card_name]["scryfall"] = scryfall_card
                if card_name in archetypes_index:
                    cards_intel[card_name]["archetypes"] = archetypes_index[card_name]
                else:
                    cards_intel[card_name]["archetypes"] = set()
                safe_dump_json_to_file(
                    self.academy_fs.ASSETS_DATA_INTEL_CARD_DIR,
                    f"{safe_posix_path(card_name)}.json",
                    cards_intel[card_name],
                )
        logger.info(
            f"Exported cards intel to {self.academy_fs.ASSETS_DATA_INTEL_CARD_DIR}."
        )

    def export_miscellanea(self):
        self.export_set_index()
        # self.export_changelog()
        # self.export_newspauper()
        # self.export_metagame()
        self.export_pauper_pool()

    def export_set_index(self):
        logger.info(f"Exporting Set Index to {self.academy_fs.ASSETS_DATA_DIR}...")
        augmented_set_index = collections.OrderedDict()
        for key, value in self.pauperformance.set_index.items():
            augmented_set_index[key] = value
            augmented_set_index[key]["new_pauper_cards"] = (
                len(self.pauperformance.incremental_card_index[key]) > 0
            )
        safe_dump_json_to_file(
            self.academy_fs.ASSETS_DATA_DIR,
            "set_index.json",
            augmented_set_index,
        )
        logger.info(f"Exported Set Index to {self.academy_fs.ASSETS_DATA_DIR}.")

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
        metagame: Metagame = self.decklassifier.get_metagame()
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

    def export_youtube_videos(self):
        logger.info(
            f"Exporting YouTube videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}..."
        )
        logger.debug(
            f"Deleting old YouTube videos at {self.academy_fs.ASSETS_DATA_VIDEO_DIR}..."
        )
        for child in Path(self.academy_fs.ASSETS_DATA_VIDEO_DIR).iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        self._export_videos(self.pauperformance.storage.list_imported_youtube_videos())
        logger.info(
            f"Exported YouTube videos to {self.academy_fs.ASSETS_DATA_VIDEO_DIR}."
        )

    def _export_videos(self, video_keys):
        folder = self.pauperformance.storage.get_folder(
            self.pauperformance.storage.youtube_video_path
        )
        # zip entries are named "<folder_name>/<filename>" — extract just the filename
        files_by_name = {
            name.split("/")[-1]: content for name, content in folder.items()
        }
        myr_fs = self.pauperformance.config_reader.myr_file_system
        with open(myr_fs.VIDEO_BANNED_IDS) as f:
            banned_ids = {line.strip() for line in f if line.strip()}
        for video_key in video_keys:
            video_json = files_by_name[video_key + ".txt"]
            video_id, creator_name, _, date, _ = video_key.split(">")
            if "premodern" in video_json["title"].lower():
                continue
            if video_id in banned_ids:
                continue
            video: Video = Video(
                name=video_json["title"],
                link=video_json["url"],
                language=video_json["language"],
                creator_name=creator_name,
                date=date,
                archetype=video_json["archetype"],
                video_id=video_id,
                deck_name=video_json["deck_name"],
                is_short=video_json["is_short"],
            )
            safe_dump_json_to_file(
                posix_path(self.academy_fs.ASSETS_DATA_VIDEO_DIR, video.archetype),
                f"{video.video_id}.json",
                video,
            )

    def export_intel_decks(self):
        logger.info(
            f"Exporting decks intel to {self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR}..."
        )
        # we need to classify all unclassified decks
        self._classify_mtggoldfish_tournament_decks()
        logger.info(
            f"Exported decks intel to {self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR}."
        )

    def _classify_mtggoldfish_tournament_decks(self):
        # banned_cards = [c["name"] for c in self.scryfall.get_banned_cards()]
        already_classified_deck_ids = set(
            p.as_posix().split("/")[-1].replace(".json", "")
            for p in Path(self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR).rglob("*.json")
        )
        unclassified_decks_count = 0
        myr_fs = self.pauperformance.config_reader.myr_file_system
        with open(myr_fs.MISSING_DECK_ARCHETYPES, "w") as out_f:
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
                        f"Unable to find tournament deck metadata: "
                        f"{tournament_deck_path}. Please, (re)download it first."
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
                most_similar_archetype, highest_similarity = (
                    self.decklassifier.classify_deck(playable_deck)
                )
                if not most_similar_archetype:
                    logger.debug("Unable to find similar deck...")
                    continue
                logger.debug(
                    f"Deck could be {most_similar_archetype.name} "
                    f"({highest_similarity})."
                )
                if highest_similarity < 0.80:
                    logger.debug("Similarity score not sufficient. Skipping deck...")
                    unclassified_decks_count += 1
                    csv.writer(out_f).writerow(
                        [
                            deck_id,
                            most_similar_archetype.name,
                            highest_similarity,
                            f"https://www.mtggoldfish.com/proxies/new?id={deck_id}",
                        ]
                    )
                    continue
                logger.debug("Similarity score sufficient. Storing intel...")
                tournament_deck.archetype = most_similar_archetype.name
                safe_dump_json_to_file(
                    posix_path(
                        self.academy_fs.ASSETS_DATA_INTEL_DECK_DIR,
                        most_similar_archetype.name,
                    ),
                    f"{deck_id}.json",
                    most_similar_archetype.name,
                )
            logger.info(f"Classified decks: {len(already_classified_deck_ids)}")
            logger.warning(f"Unclassified decks: {unclassified_decks_count}")

    def classify_deck(self, playable_deck):
        most_similar_archetype, highest_similarity = self.decklassifier.classify_deck(
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
            most_similar_archetype, highest_similarity = (
                self.decklassifier.classify_deck(playable_deck)
            )
            if not most_similar_archetype:
                logger.warning("Unable to find similar deck...")
                continue
            logger.debug(
                f"Deck could be {most_similar_archetype.name} ({highest_similarity})."
            )
            if highest_similarity < BREW_CLASSIFICATION_THRESHOLD:
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
                #     self.decklassifier.known_decks.append(
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
                #     self.decklassifier.known_decks = []
                #     known_decks, _ = (
                #         self._load_mtggoldfish_tournament_training_data()
                #     )
                #     self.decklassifier.add_known_decks(known_decks)
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

    def export_pauper_pool(self):
        logger.info(f"Exporting pauper pool to {self.academy_fs.ASSETS_DATA_DIR}...")
        pool = []
        for p12e_code, cards in self.pauperformance.incremental_card_index.items():
            if not cards:
                continue
            set_info = self.pauperformance.set_index[p12e_code]
            pool.append(
                {
                    "code": p12e_code,
                    "scryfall": set_info["scryfall_code"],
                    "name": set_info["name"],
                    "date": set_info["date"],
                    "cards": sorted(
                        [
                            {
                                "name": card["name"],
                                "url": card["scryfall_uri"].replace(
                                    "?utm_source=api", ""
                                ),
                            }
                            for card in cards
                        ],
                        key=lambda c: c["name"],
                    ),
                }
            )
        safe_dump_json_to_file(
            self.academy_fs.ASSETS_DATA_DIR,
            "pauper_pool.json",
            pool,
        )
        logger.info(f"Exported pauper pool to {self.academy_fs.ASSETS_DATA_DIR}.")
