import glob
from pathlib import Path

from deprecated import deprecated

from pauperformance_bot.constant.flags import get_language_flag
from pauperformance_bot.constant.pauperformance.academy import (
    ARCHETYPES_DIR,
)
from pauperformance_bot.constant.pauperformance.myr import (
    ARCHETYPE_TEMPLATE_FILE,
    CONFIG_ARCHETYPES_DIR,
    TEMPLATES_ARCHETYPES_DIR,
)
from pauperformance_bot.service.academy.data_loader import AcademyDataLoader
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.service.pauperformance.silver.deckstatistics import (
    DeckstatisticsFactory,
)
from pauperformance_bot.util.config import (
    read_archetype_config,
)
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


@deprecated(reason="Migrated")
class AcademyService:
    def __init__(
        self,
        pauperformance: PauperformanceService,
    ):
        self.pauperformance: PauperformanceService = pauperformance
        self.scryfall = pauperformance.scryfall
        self.set_index = pauperformance.set_index

    def update_all(self):
        self.update_archetypes()

    def update_archetypes(
        self,
        config_pages_dir=CONFIG_ARCHETYPES_DIR,
        templates_archetypes_dir=TEMPLATES_ARCHETYPES_DIR,
        archetype_template_file=ARCHETYPE_TEMPLATE_FILE,
        pauperformance_archetypes_dir=ARCHETYPES_DIR,
    ):
        logger.info("Generating archetypes...")
        all_decks = self.pauperformance.list_archived_decks()
        banned_cards = [c["name"] for c in self.scryfall.get_banned_cards()]
        videos = self.pauperformance.list_videos()
        loader = AcademyDataLoader()
        for archetype_config_file in glob.glob(f"{config_pages_dir}/*.ini"):
            logger.info(f"Processing {archetype_config_file}")
            config = read_archetype_config(archetype_config_file)
            values = config["values"]
            archetype_name = values["name"]
            archetype_decks = [
                deck for deck in all_decks if deck.archetype == archetype_name
            ]

            for deck in archetype_decks:
                playable_deck = self.pauperformance.archive.to_playable_deck(deck)
                deck.legality = (
                    "✅" if playable_deck.is_legal(banned_cards) else "Ban 🔨"
                )
                p12e_set = self.pauperformance.set_index[int(deck.p12e_code)]
                deck.set_name = p12e_set["name"]
                deck.set_date = p12e_set["date"]

            # Staples and frequents can be built:
            # a) from archived decks
            # b) from classified decks

            # method a:
            # staples, frequents = self.pauperformance.analyze_cards_frequency(
            #     archetype_decks
            # )
            # if len(archetype_decks) < 2:
            #     logger.warning(
            #         f"{archetype_name} doesn't have at least 2 decks to "
            #         f"generate staples and frequent cards."
            #     )

            # method b:
            statistics = DeckstatisticsFactory(
                self.scryfall,
                loader,
            ).build_metadata_for(archetype_name)
            staples, frequents = statistics.get_staple_and_frequent_cards()

            values["staples"] = self.scryfall.get_archetype_cards(staples)
            values["frequents"] = self.scryfall.get_archetype_cards(frequents)
            sorted_decks = sorted(
                archetype_decks,
                key=lambda d: d.p12e_name,
                reverse=True,
            )
            references = set(config["references"].values())
            values["decks"] = []
            values["references"] = []
            for deck in sorted_decks:
                if deck.p12e_name in references:
                    values["references"].append(deck)
                else:
                    values["decks"].append(deck)
            archetype_file_name = Path(archetype_config_file).name
            if archetype_name != archetype_file_name.replace(".ini", ""):
                logger.warning(
                    f"Archetype config mismatch: {archetype_name} vs "
                    f"{archetype_file_name}"
                )

            logger.info(
                f"Rendering {archetype_name} in {templates_archetypes_dir} "
                f"from {archetype_template_file}..."
            )
            archetype_videos = []
            for video in sorted(
                videos,
                key=lambda v: v.published_at + v.title + v.url,
                reverse=True,
            ):
                if video.archetype == archetype_name:
                    deck_url = ""
                    if video.deck_name:
                        matches = [
                            d.url
                            for d in all_decks
                            if d.p12e_name.startswith(video.deck_name)
                        ]
                        if len(matches) > 0:
                            # TODO: remove ugly temporary workaround for optional decks
                            deck_url = (
                                '<a href="' + matches[0] + '" target="_blank">🗎</a>'
                            )
                    archetype_videos.append(
                        {
                            "language": get_language_flag(video.language),
                            "deck_url": deck_url,
                            "url": f"{video.url}",
                            "creator": video.phd,
                            "date": video.published_at,
                            "fa_icon": video.fa_icon,
                            "title": video.title.replace("|", "-"),
                        }
                    )
            # template_values = {
            #     **values,
            #     "videos": archetype_videos,
            #     "resources": resources,
            # }
            # render_template(
            #     templates_archetypes_dir,
            #     archetype_template_file,
            #     archetype_output_file,
            #     template_values,
            # )
        logger.info("Generated archetypes.")
