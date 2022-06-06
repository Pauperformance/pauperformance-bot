import glob
from collections import defaultdict
from pathlib import Path

from pauperformance_bot.constant.academy import (
    ARCHETYPES_DIR,
    ARCHETYPES_DIR_RELATIVE_URL,
    ARCHETYPES_INDEX_OUTPUT_FILE,
    DEV_OUTPUT_FILE,
    FAMILIES_DIR,
    FAMILIES_DIR_RELATIVE_URL,
    HOME_OUTPUT_FILE,
    PAUPER_POOL_OUTPUT_FILE,
    PAUPER_POOL_PAGE_NAME,
    SET_INDEX_OUTPUT_FILE,
    SET_INDEX_PAGE_NAME,
)
from pauperformance_bot.constant.flags import get_language_flag
from pauperformance_bot.constant.myr import (
    ARCHETYPE_TEMPLATE_FILE,
    ARCHETYPES_INDEX_TEMPLATE_FILE,
    CONFIG_ARCHETYPES_DIR,
    CONFIG_DIR,
    CONFIG_FAMILIES_DIR,
    CONFIG_NEWSPAUPER_FILE,
    DEV_TEMPLATE_FILE,
    FAMILY_TEMPLATE_FILE,
    HOME_TEMPLATE_FILE,
    PAUPER_POOL_TEMPLATE_FILE,
    SET_INDEX_TEMPLATE_FILE,
    TEMPLATES_ARCHETYPES_DIR,
    TEMPLATES_FAMILIES_DIR,
    TEMPLATES_PAGES_DIR,
)
from pauperformance_bot.service.pauperformance import PauperformanceService
from pauperformance_bot.util.config import (
    read_archetype_config,
    read_family_config,
    read_newspauper_config,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path
from pauperformance_bot.util.template import render_template
from pauperformance_bot.util.time import now_utc, pretty_str

logger = get_application_logger()


class AcademyService:
    def __init__(
        self,
        pauperformance: PauperformanceService,
    ):
        self.pauperformance: PauperformanceService = pauperformance
        self.scryfall = pauperformance.scryfall
        self.set_index = pauperformance.set_index

    def update_all(self, update_dev=True):
        self.update_home()
        self.update_archetypes_index()
        self.update_set_index()
        self.update_pauper_pool()
        self.update_archetypes()
        self.update_families()
        if update_dev:
            self.update_dev()

    def update_home(
        self,
        config_dir=CONFIG_DIR,
        templates_pages_dir=TEMPLATES_PAGES_DIR,
        newspauper_file=CONFIG_NEWSPAUPER_FILE,
        home_template_file=HOME_TEMPLATE_FILE,
        home_output_file=HOME_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering home in {templates_pages_dir} from " f"{home_template_file}..."
        )
        config = read_newspauper_config(posix_path(config_dir, newspauper_file))
        resources = config["resources"]
        current_set = self.pauperformance.get_current_set_index()
        render_template(
            templates_pages_dir,
            home_template_file,
            home_output_file,
            {
                "p12e_code": current_set["p12e_code"],
                "set_name": f"{current_set['name']} "
                f"({current_set['scryfall_code']}), "
                f"released on {current_set['date']}",
                "resources": resources,
            },
        )
        logger.info(f"Rendered home to {home_output_file}.")

    def update_archetypes_index(
        self,
        config_pages_dir=CONFIG_ARCHETYPES_DIR,
        templates_pages_dir=TEMPLATES_PAGES_DIR,
        archetypes_dir=ARCHETYPES_DIR_RELATIVE_URL,
        families_dir=FAMILIES_DIR_RELATIVE_URL,
        archetypes_index_template_file=ARCHETYPES_INDEX_TEMPLATE_FILE,
        archetypes_index_output_file=ARCHETYPES_INDEX_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering archetype index in {templates_pages_dir} from "
            f"{archetypes_index_template_file}..."
        )
        archetypes = []
        for archetype_config_file in glob.glob(f"{config_pages_dir}/*.ini"):
            logger.info(f"Processing {archetype_config_file}")
            config = read_archetype_config(archetype_config_file)
            values = config["values"]
            archetypes.append(
                {
                    "name": values["name"],
                    "mana": values["mana"],
                    "type": ", ".join(values["type"]),
                    "family": values["family"] if values["family"] else "",
                }
            )
        archetypes.sort(key=lambda a: a["name"])
        render_template(
            templates_pages_dir,
            archetypes_index_template_file,
            archetypes_index_output_file,
            {
                "archetypes": archetypes,
                "archetypes_dir": archetypes_dir,
                "families_dir": families_dir,
            },
        )
        logger.info(f"Rendered archetypes index to {archetypes_index_output_file}.")

    def update_set_index(
        self,
        templates_pages_dir=TEMPLATES_PAGES_DIR,
        set_index_template_file=SET_INDEX_TEMPLATE_FILE,
        set_index_output_file=SET_INDEX_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering set index in {templates_pages_dir} from "
            f"{set_index_template_file}..."
        )
        bolded_set_index = self._boldify_sets_with_new_cards()
        render_template(
            templates_pages_dir,
            set_index_template_file,
            set_index_output_file,
            {
                "index": bolded_set_index,
                "pauper_pool_page": PAUPER_POOL_PAGE_NAME.as_html(),
            },
        )
        logger.info(f"Rendered set index to {set_index_output_file}.")

    def update_pauper_pool(
        self,
        templates_pages_dir=TEMPLATES_PAGES_DIR,
        pauper_pool_template_file=PAUPER_POOL_TEMPLATE_FILE,
        pauper_pool_output_file=PAUPER_POOL_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering pauper pool in {templates_pages_dir} from "
            f"{pauper_pool_template_file}..."
        )
        card_index = self.pauperformance.incremental_card_index
        render_template(
            templates_pages_dir,
            pauper_pool_template_file,
            pauper_pool_output_file,
            {
                "tot_cards_number": sum(len(i) for i in card_index.values()),
                "set_index": list(self.set_index.values()),
                "card_index": card_index,
                "set_index_page": SET_INDEX_PAGE_NAME.as_html(),
            },
        )
        logger.info(f"Rendered pauper pool to {pauper_pool_template_file}.")

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
        for archetype_config_file in glob.glob(f"{config_pages_dir}/*.ini"):
            logger.info(f"Processing {archetype_config_file}")
            config = read_archetype_config(archetype_config_file)
            values = config["values"]
            resources = config["resources"]
            archetype_name = values["name"]
            archetype_decks = [
                deck for deck in all_decks if deck.archetype == archetype_name
            ]

            for deck in archetype_decks:
                playable_deck = self.pauperformance.archive.to_playable_deck(deck)
                deck.legality = "✅" if playable_deck.is_legal(banned_cards) else "Ban 🔨"
                p12e_set = self.pauperformance.set_index[int(deck.p12e_code)]
                deck.set_name = p12e_set["name"]
                deck.set_date = p12e_set["date"]

            staples, frequents = self.pauperformance.analyze_cards_frequency(
                archetype_decks
            )
            if len(archetype_decks) < 2:
                logger.warning(
                    f"{archetype_name} doesn't have at least 2 decks to "
                    f"generate staples and frequent cards."
                )
            values["staples"] = self._get_rendered_card_info(staples)
            values["frequents"] = self._get_rendered_card_info(frequents)
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

            archetype_output_file = posix_path(
                pauperformance_archetypes_dir,
                archetype_file_name.replace(".ini", ".md"),
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
            template_values = {
                **values,
                "videos": archetype_videos,
                "resources": resources,
            }
            render_template(
                templates_archetypes_dir,
                archetype_template_file,
                archetype_output_file,
                template_values,
            )
        logger.info("Generated archetypes.")

    def update_families(
        self,
        config_families_dir=CONFIG_FAMILIES_DIR,
        config_archetypes_dir=CONFIG_ARCHETYPES_DIR,
        templates_families_dir=TEMPLATES_FAMILIES_DIR,
        archetypes_dir=ARCHETYPES_DIR_RELATIVE_URL,
        family_template_file=FAMILY_TEMPLATE_FILE,
        pauperformance_families_dir=FAMILIES_DIR,
    ):
        logger.info("Generating families...")
        logger.debug("Building families-archetypes map...")
        families_map = defaultdict(list)
        for archetype_config_file in glob.glob(f"{config_archetypes_dir}/*.ini"):
            config = read_archetype_config(archetype_config_file)
            values = config["values"]
            if values["family"]:
                families_map[values["family"]].append(values["name"])
        logger.info(f"Families map: {families_map}")

        for family_name in families_map.keys():
            family_config_file = posix_path(config_families_dir, f"{family_name}.ini")
            logger.info(f"Processing {family_config_file}")
            values = read_family_config(family_config_file)
            if values["name"] != family_name:
                raise ValueError()
            values["archetypes"] = [
                {
                    "name": archetype,
                }
                for archetype in sorted(families_map[family_name])
            ]
            values["archetypes_dir"] = archetypes_dir
            family_file_name = Path(family_config_file).name
            if family_name != family_file_name.replace(".ini", ""):
                logger.warning(
                    f"Family config mismatch: {family_name} vs " f"{family_file_name}"
                )

            family_output_file = posix_path(
                pauperformance_families_dir,
                family_file_name.replace(".ini", ".md"),
            )
            logger.info(
                f"Rendering {family_name} in {templates_families_dir} "
                f"from {family_template_file}..."
            )
            render_template(
                templates_families_dir,
                family_template_file,
                family_output_file,
                values,
            )
        logger.info("Generated family.")

    def update_dev(
        self,
        templates_pages_dir=TEMPLATES_PAGES_DIR,
        dev_template_file=DEV_TEMPLATE_FILE,
        dev_output_file=DEV_OUTPUT_FILE,
    ):
        logger.info(
            f"Rendering dev in {templates_pages_dir} from " f"{dev_template_file}..."
        )
        render_template(
            templates_pages_dir,
            dev_template_file,
            dev_output_file,
            {
                "last_update_date": pretty_str(now_utc()),
            },
        )
        logger.info(f"Rendered dev to {dev_output_file}.")

    def _get_rendered_card_info(self, cards):
        rendered_cards = []
        for card in sorted(cards):
            scryfall_card = self.scryfall.get_card_named(card)
            if "image_uris" not in scryfall_card:  # e.g. Delver of Secrets
                image_uris = scryfall_card["card_faces"][0]["image_uris"]
            else:
                image_uris = scryfall_card["image_uris"]
            image_url = image_uris["normal"]
            if "?" in image_url:
                image_url = image_url[: image_url.index("?")]
            rendered_cards.append(
                {
                    "name": card,
                    "image_url": image_url,
                    "page_url": scryfall_card["scryfall_uri"].replace(
                        "?utm_source=api", ""
                    ),
                }
            )
        return rendered_cards

    def _boldify_sets_with_new_cards(self):
        card_index = self.pauperformance.incremental_card_index
        bolded_index = []
        for item in self.set_index.values():
            p12e_code = item["p12e_code"]
            if len(card_index[p12e_code]) == 0:
                bolded_index.append(item)
            else:
                bolded_index.append({k: f"**{v}**" for k, v in item.items()})
        return bolded_index
