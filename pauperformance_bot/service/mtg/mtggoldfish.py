import datetime
import time
import urllib.parse
from pathlib import Path
from urllib.request import urlopen

import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery

from pauperformance_bot.constant.mtg.mtggoldfish import (
    API_ENDPOINT,
    DECK_API_TOKEN,
    DECK_DOWNLOAD_TOKEN,
    DECK_TOOLS_CONTAINER_CLASS,
    FULL_PAUPER_METAGAME_URL,
    METAGAME_ARCHETYPE_TITLE_URL_CLASS,
    METAGAME_SHARE_CLASS,
    REQUESTS_SLEEP_SECONDS,
)
from pauperformance_bot.entity.api.deck import MTGGoldfishTournamentDeck
from pauperformance_bot.entity.api.tournament import Tournament
from pauperformance_bot.entity.deck.archive.mtggoldfish import MTGGoldfishArchivedDeck
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.entity.mtg.mtggoldfish import MTGGoldfishTournamentSearchResult
from pauperformance_bot.exceptions import MTGGoldfishException
from pauperformance_bot.service.mtg.downloader.downloader import MtgoDeckDownloader
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path, safe_dump_json_to_file
from pauperformance_bot.util.time import now_utc

logger = get_application_logger()


class MTGGoldfish:
    @staticmethod
    def get_pauper_meta(
        metagame_page_url: str = FULL_PAUPER_METAGAME_URL,
    ) -> dict[str, tuple[str, PlayableDeck]]:
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
        meta_decks = {}
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
            meta_decks[link] = (share, playable_deck)
            time.sleep(REQUESTS_SLEEP_SECONDS)  # avoid flooding (and soft-ban)
        logger.info(f"Got pauper meta: {len(meta_decks)} archetypes.")
        return meta_decks

    @staticmethod
    def get_pauper_tournaments(
        from_date: datetime.datetime,
        to_date: datetime.datetime,
        tournament_name="",
    ) -> list[MTGGoldfishTournamentSearchResult]:
        tournaments = []
        for page in range(1, 5):  # MTGGoldfish returns at most 4 results pages
            from_param = f"{from_date.month}%2F{from_date.day}%2F{from_date.year}"
            to_param = f"{to_date.month}%2F{to_date.day}%2F{to_date.year}"
            url = (
                f"{API_ENDPOINT}/tournament_searches/create"
                f"?commit=Search"
                f"&page={page}"
                f"&tournament_search%5Bdate_range%5D={from_param}+-+{to_param}"
                f"&tournament_search%5Bformat%5D=pauper"
                f"&utf8=%E2%9C%93"
            )
            if tournament_name:
                tournament_param = urllib.parse.quote(tournament_name)
                url += f"&tournament_search%5Bname%5D={tournament_param}"
            else:
                url += "&tournament_search%5Bname%5D="
            logger.debug(f"Collecting results from page: {url}")
            html_page = urllib.request.urlopen(url)
            bs = BeautifulSoup(html_page.read(), features="lxml")
            rows = bs.findAll("tr")[1:]  # skip header
            i = 0
            for a in bs.findAll("a"):
                if (
                    "tournament" in a["href"]
                    and "/new" not in a["href"]
                    and "tournament_searches" not in a["href"]
                ):
                    result = MTGGoldfishTournamentSearchResult(
                        url=f"{API_ENDPOINT}{a['href']}",
                        name=a.text,
                        date=rows[i].text.split()[0],
                    )
                    tournaments.append(result)
                    i += 1
                    logger.debug(f"Added result {result}")
            time.sleep(REQUESTS_SLEEP_SECONDS)  # avoid flooding (and soft-ban)
            if any("No tournaments found." == x.text.strip() for x in bs.findAll("p")):
                break
            if page == 4:
                logger.warning(
                    f"Too many results in {url}: cannot search for more than {page} "
                    f"pages. Try to narrow down you date range."
                )
        return tournaments

    @staticmethod
    def get_tournament_decks(
        tournament_result: MTGGoldfishTournamentSearchResult,
    ) -> list[MTGGoldfishTournamentDeck]:
        url = tournament_result.url
        logger.debug(f"Extracting tournament decks from {url}...")
        tournament_decks: list[MTGGoldfishTournamentDeck] = []
        html_page = urllib.request.urlopen(url)
        bs = BeautifulSoup(html_page.read(), features="lxml")
        for tr in bs.findAll("tr")[1:]:  # skip header
            columns = tr.contents
            if len(columns) < 10:
                continue
            # sometimes the special ' ' character is used instead of ' ': fix it
            place = columns[1].text.strip().replace(" ", " ")
            archetype = columns[3].text.strip().replace(" ", " ")
            pilot = columns[5].text.strip().replace(" ", " ")
            # Sometimes MTGGoldfish does not report deck prices.
            # Maybe in the past they could not get this info.
            # Let's take into account missing values.
            try:
                tabletop_price = int(columns[7].text.strip()[2:])
            except (ValueError, IndexError):
                tabletop_price = None
            try:
                mtgo_price = int(columns[9].text.strip().split()[0])
            except (ValueError, IndexError):
                mtgo_price = None
            tournament_deck = MTGGoldfishTournamentDeck(
                url=f"{API_ENDPOINT}{list(columns[3].children)[1]['href']}",
                archetype=archetype,
                place=place,
                pilot=pilot,
                tabletop_price=tabletop_price,
                mtgo_price=mtgo_price,
                tournament_id=tournament_result.identifier,
                tournament_name=tournament_result.name,
                tournament_date=tournament_result.date,
            )
            logger.debug(f"Extracted deck {tournament_deck}.")
            tournament_decks.append(tournament_deck)
        logger.debug(f"Extracted tournament decks from {url}.")
        return tournament_decks

    def download_mtggoldfish_tournaments(self, start_date, end_date, academy_fs):
        processed_tournament_ids = {
            tournament_id.name.rstrip(".json")
            for tournament_id in Path(
                academy_fs.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DIR
            ).glob("*.json")
        }
        start = end_date
        end = end_date
        delta = datetime.timedelta(days=10)  # prevents some tournaments to be skipped
        while end > start_date:
            end -= delta
            logger.info(f"Processing from {start} to {end}...")
            results: list[MTGGoldfishTournamentSearchResult] = (
                self.get_pauper_tournaments(end, start)
            )
            logger.info(f"Found {len(results)} tournaments.")
            for result in results:
                if f"{result.identifier}" in processed_tournament_ids:
                    logger.debug(
                        f"Skipping already processed tournament {result.identifier}..."
                    )
                    continue

                logger.debug(f"Fetching data from {result.url}...")
                decks: list[MTGGoldfishTournamentDeck] = self.get_tournament_decks(
                    result
                )
                for deck in decks:
                    logger.debug(f"Storing deck metadata {deck.identifier}...")
                    safe_dump_json_to_file(
                        academy_fs.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DECKS_DIR,
                        f"{deck.identifier}.json",
                        deck,
                    )
                    logger.debug(f"Stored deck metadata {deck.identifier}...")
                    time.sleep(REQUESTS_SLEEP_SECONDS)
                    logger.debug(f"Storing deck list {deck.identifier}...")
                    download_url = deck.url.replace(
                        f"/{DECK_API_TOKEN}", f"/{DECK_DOWNLOAD_TOKEN}"
                    )
                    try:
                        deck_downloader = MtgoDeckDownloader(download_url)
                        playable_deck: PlayableDeck = deck_downloader.download()
                    except ValueError:
                        logger.warning(f"Unable to parse deck at {download_url}...")
                        continue
                    with open(
                        posix_path(
                            academy_fs.ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
                            f"{deck.identifier}.txt",
                        ),
                        "w",
                    ) as out_f:
                        out_f.write(playable_deck.mainboard_mtggoldfish)
                        out_f.write("\n\n")
                        out_f.write(playable_deck.sideboard_mtggoldfish)
                        out_f.write("\n")
                    logger.debug(f"Stored deck list {deck.identifier}...")

                tournament_api = Tournament(
                    url=result.url,
                    name=result.name,
                    date=result.date,
                    deck_ids=[d.identifier for d in decks],
                )
                logger.debug(f"Storing tournament {result.identifier}...")
                safe_dump_json_to_file(
                    academy_fs.ASSETS_DATA_TOURNAMENT_MTGGOLDFISH_DIR,
                    f"{result.identifier}.json",
                    tournament_api,
                )
                logger.debug(f"Stored tournament {result.identifier}.")
                time.sleep(REQUESTS_SLEEP_SECONDS)
            time.sleep(REQUESTS_SLEEP_SECONDS)
            start -= delta
