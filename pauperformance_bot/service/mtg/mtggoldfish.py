from urllib.request import urlopen

import requests
from pyquery import PyQuery

from pauperformance_bot.constant.mtggoldfish import (
    API_ENDPOINT,
    DECK_API_TOKEN,
    DECK_TOOLS_CONTAINER_CLASS,
    FULL_PAUPER_METAGAME_URL,
    METAGAME_ARCHETYPE_TITLE_URL_CLASS,
    METAGAME_SHARE_CLASS,
)
from pauperformance_bot.entity.deck.archive.mtggoldfish import MTGGoldfishArchivedDeck
from pauperformance_bot.entity.deck.playable import parse_playable_deck_from_lines
from pauperformance_bot.exceptions import MTGGoldfishException
from pauperformance_bot.service.deck_analyser import classify_deck
from pauperformance_bot.service.pauperformance.pauperformance import (
    PauperformanceService,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.time import now_utc

logger = get_application_logger()


class MTGGoldfish:
    def get_pauper_meta(
        self,
        pauperformance: PauperformanceService,
        metagame_page_url: str = FULL_PAUPER_METAGAME_URL,
    ):
        logger.info(f"Getting pauper meta from {metagame_page_url}...")
        response = requests.get(metagame_page_url)
        if response.status_code != 200:
            raise MTGGoldfishException(
                f"Unable to get pauper meta from url: {metagame_page_url}"
            )
        logger.debug("Parsing meta...")
        pq = PyQuery(response.content)
        archetype_shares = [
            archetype.text().split()[1]
            for archetype in pq(METAGAME_SHARE_CLASS).items()
        ]
        logger.debug(f"Found {len(archetype_shares)} meta shares.")
        archetype_links = [
            f"{API_ENDPOINT}{archetype.attr['href']}"
            for archetype in pq(METAGAME_ARCHETYPE_TITLE_URL_CLASS).items()
        ]
        logger.debug(f"Found {len(archetype_links)} meta archetypes.")
        if len(archetype_shares) != len(archetype_links):
            raise MTGGoldfishException(
                "Mismatch with archetype shares after parsing meta."
            )
        meta = {}
        for share, link in zip(archetype_shares, archetype_links):
            logger.info(f"Archetype {link}: {share}.")
            logger.debug(f"Retrieving sample deck for archetype {link}...")
            response = requests.get(link)
            if response.status_code != 200:
                raise MTGGoldfishException(
                    f"Unable to get pauper deck from url: {link}"
                )
            deck_id = (
                next(PyQuery(response.content)(DECK_TOOLS_CONTAINER_CLASS).items())
                .attr["href"]
                .replace(f"/{DECK_API_TOKEN}/", "")
            )
            logger.debug(f"Archetype deck has id {deck_id}.")
            logger.debug("Downloading and parsing list...")
            fake_deck = MTGGoldfishArchivedDeck(
                "Foo 000.000.ABC | Foo (bar)",
                now_utc(),
                deck_id,
            )
            content = urlopen(fake_deck.download_txt_url).read()
            lines = content.decode("utf-8").split("\r\n")
            playable_deck = parse_playable_deck_from_lines(lines)
            # logger.debug(
            #     f"Retrieved sample deck for archetype {link}: {playable_deck}"
            # )
            similar_archetype, similarity_score = classify_deck(
                playable_deck,
                pauperformance,
            )
            meta[link] = (share, similar_archetype, similarity_score)
        logger.info(f"Got pauper meta {meta}.")
        return meta
