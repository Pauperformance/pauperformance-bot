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
        self._tmp_export_synthetic_archetypes()

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

    def _tmp_export_synthetic_archetypes(self):
        logger.info(
            f"Exporting archetypes to {self.academy_fs.ASSETS_DATA_ARCHETYPE_DIR}..."
        )
        cards = [
            ArchetypeCard(
                name="Burning-Tree Emissary",
                link="https://scryfall.com/card/dds/55/burning-tree-emissary",
                preview="https://c1.scryfall.com/file/scryfall-cards/normal/front/"
                "2/2/22e3e874-a0ec-4459-b78d-abef6b9232b9.jpg",
            ),
            ArchetypeCard(
                name="Hunger of the Howlpack",
                link="https://scryfall.com/card/cns/168/hunger-of-the-howlpack",
                preview="https://c1.scryfall.com/file/scryfall-cards/normal/front/"
                "2/3/23676697-2b84-4e9f-9e38-4fd58085a698.jpg",
            ),
            ArchetypeCard(
                name="Nest Invader",
                link="https://scryfall.com/card/pca/69/nest-invader",
                preview="https://c1.scryfall.com/file/scryfall-cards/normal/front/"
                "3/0/3085f5b1-d2e3-4dd4-8263-024b2b5da4b4.jpg",
            ),
        ]
        archetype: Archetype = Archetype(
            name="Stompy",
            aliases=["MonoG Aggro"],
            family=None,
            dominant_mana=["G"],
            game_type=["Aggro"],
            description="Stompy is a fast and solid aggro deck, and the most popular of"
            " this type in the format."
            "It takes advantage of cheap and strong creatures, sometimes wi"
            "th [evasion or pseudo-evasion abilities](https://mtg.fandom.co"
            "m/wiki/Evasion_ability), to immediately put pressure on the bo"
            "ard."
            "Several efficient pump spells helps Stompy quickly reducing th"
            "e opponent's life total, allowing players to consistently win "
            "games in the fist few turns."
            "Since 2019, the addition of [Savage Swipe](https://scryfall.co"
            "m/card/mh1/178/savage-swipe) from Modern Horizons (mh1) has pr"
            "ovided the deck with a powerful option for clearing out blocke"
            "rs while also applying additional pressure.",
            staples=cards,
            frequent=cards,
            reference_decks=[
                "Stompy 722.001.tarmogoyf_ita",
                "Stompy 696.001.Ixidor29",
            ],
            resource_sideboard=SideboardResource(
                link="https://docs.google.com/spreadsheets/d/1iBnopoHW5EspnWOvCDVm28eTI"
                "581RljyJoJgAZJOhXQ/edit?usp=sharing",
            ),
            resources_discord=[
                DiscordResource(
                    name="Pauper Stompy Discord",
                    link="https://discord.gg/RzTmb76qjJ",
                    language="eng",
                )
            ],
            resources=[
                Resource(
                    name="Pauper Stompy Deck Guide",
                    link="https://strategy.channelfireball.com/all-strategy/mtg/channel"
                    "magic-articles/pauper-stompy-deck-guide/",
                    language="eng",
                    author="Alex Ullman",
                    date="2020-08-27",
                ),
                Resource(
                    name="[PAUPER PRIMER] Mono Green",
                    link="http://www.metagame.it/forum/viewtopic.php?f=187&t=10786",
                    language="ita",
                    author="Mr Pain",
                    date="2013-12-24",
                ),
            ],
        )
        safe_dump_json_to_file(
            self.academy_fs.ASSETS_DATA_ARCHETYPE_DIR,
            f"{archetype.name}.json",
            archetype,
        )
        logger.info(
            f"Exported archetypes to {self.academy_fs.ASSETS_DATA_ARCHETYPE_DIR}."
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
