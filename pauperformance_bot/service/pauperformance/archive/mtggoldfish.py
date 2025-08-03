import re
import time
from datetime import datetime
from functools import cache, wraps
from itertools import count
from urllib.request import urlopen

from pyquery import PyQuery
from requests import session

from pauperformance_bot.constant.mtg.mtggoldfish import (
    API_ENDPOINT,
    DECK_API_ENDPOINT,
    MIN_AUTHENTICITY_TOKEN_LEN,
    MTGGOLDFISH_THROTTLE_ERROR_RESPONSE,
    NO_COOKIE_HEADER,
    REQUESTS_SLEEP_SECONDS,
)
from pauperformance_bot.constant.pauperformance.academy import AcademyFileSystem
from pauperformance_bot.constant.pauperformance.myr import USA_DATE_FORMAT
from pauperformance_bot.credentials import (
    MTGGOLDFISH_PAUPERFORMANCE_PASSWORD,
    MTGGOLDFISH_PAUPERFORMANCE_USERNAME,
)
from pauperformance_bot.entity.deck.archive.abstract import AbstractArchivedDeck
from pauperformance_bot.entity.deck.archive.mtggoldfish import MTGGoldfishArchivedDeck
from pauperformance_bot.entity.deck.playable import (
    PlayableDeck,
    parse_playable_deck_from_lines,
)
from pauperformance_bot.exceptions import ArchiveException, MTGGoldfishException
from pauperformance_bot.service.pauperformance.archive.abstract import (
    AbstractArchiveService,
)
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()


def with_login(func):
    @wraps(func)
    def maybe_login(*args, **kwargs):
        mtggoldfish = args[0]  # "self" is the 1st argument of method calls
        if not mtggoldfish.logged:
            mtggoldfish.login()
            mtggoldfish.logged = True
        return func(*args, **kwargs)

    return maybe_login


class MTGGoldfishArchiveService(AbstractArchiveService):
    def __init__(
        self,
        storage,
        email=MTGGOLDFISH_PAUPERFORMANCE_USERNAME,
        password=MTGGOLDFISH_PAUPERFORMANCE_PASSWORD,
        endpoint=API_ENDPOINT,
        deck_api_endpoint=DECK_API_ENDPOINT,
    ):
        self.email = email
        self.password = password
        self.endpoint = endpoint
        self.deck_api_endpoint = deck_api_endpoint
        self.session = session()
        self.logged = False

        # Dear reader,
        # The following attributes should have never existed.
        # In a just world, we would have been able to query MTGGoldfish and get the list
        # of our decks in a simple and efficient way.
        # However, the world is not just.
        # MTGGoldfish has a ridiculous bug: by iterating over the pages of your decks
        # (i.e. here https://www.mtggoldfish.com/decks), you will NOT get all your
        # decks.
        # For some reasons, the pagination mechanism is broken and some decks just
        # disappear or are returned multiple times.
        # However, they can be found if you directly search for them by name.
        # I tried to explain the bug to the MTGGoldfish team, by email and by Twitter,
        # but I got no response.
        # So, let's just fix this shit ourselves with some caching mechanism.
        self.storage = storage  # will be the source of truth to detect missing decks
        self._decks_cache: list[AbstractArchivedDeck] = []  # will act as a cache

    @staticmethod
    def _parse_login_authenticity_token(response):
        for line in response.text.split("\n"):
            if "authenticity_token" not in line:
                continue
            # Multiple authenticity_token token can be found in the page
            # (facebook, twitter, twitch, etc).
            # We need the one for the classic login (/auth/identity/callback).
            if "/auth/identity/callback" not in line:
                continue
            logger.debug(f"Extracting authenticity_token from line: {line}")
            value_token = "value="
            for match in re.finditer(value_token, line):
                token = line[match.end() + 1 :]
                token = token[0 : token.find('"')]
                if len(token) >= MIN_AUTHENTICITY_TOKEN_LEN:
                    logger.debug(f"Found authenticity_token: {token}")
                    return token
        raise MTGGoldfishException("Unable to get authenticity_token from MTGGoldfish.")

    @staticmethod
    def _parse_meta_authenticity_token(response):
        for line in response.text.split("\n"):
            if "meta" not in line or "csrf-token" not in line:
                continue
            logger.debug(f"Extracting authenticity_token from line: {line}")
            content_token = "content="
            authenticity_token = line[
                line.rfind(content_token) + len(content_token) + 1 : -4
            ]
            logger.debug(f"Found authenticity_token: {authenticity_token}")
            return authenticity_token
        raise MTGGoldfishException("Unable to get authenticity_token from MTGGoldfish.")

    def _get_login_info(self):
        logger.info("Getting dynamic login info from MTGGoldfish...")
        response = self.session.get(f"{self.endpoint}")
        if "_mtg_session" not in response.cookies.get_dict():
            raise MTGGoldfishException(
                "Unable to get mtg_session_cookie from MTGGoldfish."
            )
        mtg_session_cookie = response.cookies.get_dict()["_mtg_session"]
        logger.debug(f"Found mtg_session_cookie: {mtg_session_cookie}")
        return mtg_session_cookie, self._parse_login_authenticity_token(response)

    def login(self):
        mtg_session_cookie, authenticity_token = self._get_login_info()
        logger.info(f"Logging to MTGGoldfish as {self.email}...")
        header = {
            "cookie": f"_mtg_session={mtg_session_cookie}",
        }
        payload = {
            "authenticity_token": authenticity_token,
            "auth_key": self.email,
            "password": self.password,
            "commit": "Log In",
        }
        response = self.session.post(
            f"{self.endpoint}/auth/identity/callback",
            headers=header,
            data=payload,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(f"Failed to login for {self.email}")
        logger.debug(f"Header Set-Cookie: {response.headers['Set-Cookie']}")
        logger.debug(
            f"Session cookie: " f"_mtg_session={self.session.cookies['_mtg_session']}"
        )
        logger.debug(
            f"Response cookie: _mtg_session={response.cookies['_mtg_session']}"
        )
        logger.info(f"Logged to MTGGoldfish as {self.email}.")

    def get_uri(self, deck_id):
        return f"{self.deck_api_endpoint}/{deck_id}"

    @with_login
    def create_deck(self, name, description, playable_deck):
        return self._create_deck(name, description, playable_deck, format_="pauper")

    def _create_deck(self, name, description, playable_deck, format_):
        logger.info(f"Creating deck {name} for {self.email}...")
        # we need to perform a dummy request to parse the authenticity_token
        response = self.session.get(f"{self.endpoint}/decks/new")
        authenticity_token = self._parse_meta_authenticity_token(response)
        headers = {
            "cookie": f"_mtg_session={self.session.cookies['_mtg_session']}",
            **NO_COOKIE_HEADER,
        }
        payload = {
            "utf8": "✓",
            "authenticity_token": authenticity_token,
            "deck_input[name]": name,
            "deck_input[description]": description,
            "deck_input[format]": format_,
            "deck_input[commander]": "",
            "deck_input[commander_alt]": "",
            "deck_input[companion]": "",
            "deck_input[private]": "0",
            "deck_input[specific_cards]": "0",
            "deck_input[deck]": playable_deck.mainboard_mtggoldfish,
            "card_name": "",
            "quantity": "1",
            "deck_input[sideboard]": playable_deck.sideboard_mtggoldfish,
            "commit": "Save",
        }
        response = self.session.post(
            f"{self.endpoint}/decks",
            headers=headers,
            data=payload,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(f"Failed to create deck {name} for {self.email}")
        deck_id = response.request.url.split("/")[-1]
        logger.info(f"Created deck {name} for {self.email}. Id: {deck_id}")
        return deck_id

    @with_login
    def list_decks(self) -> list[AbstractArchivedDeck]:
        self._update_decks_cache()
        return self._decks_cache

    def _update_decks_cache(self):
        all_decks = []
        for page in count(1):
            new_decks = self._list_decks_in_page(page)

            if new_decks and all(d in self._decks_cache for d in new_decks):
                logger.debug("No new deck detected: cache is not stale.")
                return  # no new deck detected: no need to do anything else

            all_decks += new_decks

            if len(new_decks) == 0:
                break  # last page reached: no need to further scroll pages

        # the first time we list decks we need to apply a workaround
        if len(self._decks_cache) == 0:
            all_decks = self._workaround_retrieve_missing_decks(all_decks)

        self._decks_cache = sorted(all_decks, key=lambda d: d.name)

    @with_login
    def _list_decks_in_page(
        self, page, filter_name="", mtg_format="pauper", visibility="public"
    ):
        # possible filter_visibility values: '', 'private', 'public'
        logger.info(f"Listing decks for {self.email} in page {page}...")
        params = {
            "filter_name": filter_name,
            "filter_format": mtg_format,
            "filter_visibility": visibility,
            "commit": "Filter",
        }
        response = self.session.get(
            f"{self.endpoint}/decks?page={page}",
            headers=NO_COOKIE_HEADER,
            params=params,
        )
        if response.status_code == 400 and "Invalid page number" in response.text:
            # reached end of pagination: no more decks
            return []
        if response.status_code != 200:
            raise MTGGoldfishException(f"Failed to list decks for {self.email}")
        logger.debug(f"Parsing page with decks for {self.email}...")
        pq = PyQuery(response.content)
        decks = []
        for c in pq("table tbody tr").items():
            row = c.text()
            _, name, _, format_, creation_date, visibility, _, _ = row.split("\n")
            creation_date = datetime.strptime(creation_date, USA_DATE_FORMAT)
            creation_date = 1000 * int(creation_date.timestamp())
            url = next(link.attrib["href"] for link in c("a"))
            logger.debug(f"Deck {name} has url: {url}")
            deck_id = url.split("/")[-1]
            decks.append(MTGGoldfishArchivedDeck(name, creation_date, deck_id))
        logger.info(f"Found {len(decks)} decks: {decks}")
        logger.info(f"Listed decks for {self.email}.")
        return decks

    def _workaround_retrieve_missing_decks(self, all_decks):
        logger.debug("Fixing bug in MTGGoldfish pager...")

        # Due to a bug in the pagination mechanism, decks are sometimes
        # returned more than once or not returned at all.

        # first, let's remove duplicates
        logger.debug(f"Initial number of decks: {len(all_decks)}")
        all_decks = list(set(all_decks))
        logger.debug(f"Without duplicates: {len(all_decks)}")
        # then, grab one-by-one all the missing decks from storage
        storage_decks = self.storage.list_imported_deckstats_deck_names()
        mtggoldfish_decks = {d.name for d in all_decks}
        for missing_deck in storage_decks - mtggoldfish_decks:
            logger.debug(f"Found missing deck: {missing_deck}")
            missing_deck = self._list_decks_in_page(1, missing_deck)
            if len(missing_deck) != 1:
                raise ValueError(f"Unable to find missing deck {missing_deck}")
            all_decks += missing_deck
        logger.debug(f"Final number of decks: {len(all_decks)}")
        return all_decks

    @with_login
    def delete_deck(self, deck_id):
        logger.info(f"Deleting deck with id {deck_id} for {self.email}...")
        # we need to perform a dummy request to parse the authenticity_token
        params = {
            "filter_name": "",
            "filter_format": "pauper",
            "filter_visibility": "public",
            "commit": "Filter",
        }
        response = self.session.get(
            f"{self.endpoint}/decks",
            headers=NO_COOKIE_HEADER,
            params=params,
        )
        authenticity_token = self._parse_meta_authenticity_token(response)
        header = {
            "cookie": f"_mtg_session={self.session.cookies['_mtg_session']}",
            "accept": "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,image/apng,*/*;"
            "q=0.8,application/signed-exchange;"
            "v=b3;"
            "q=0.9",
        }
        payload = {
            "authenticity_token": authenticity_token,
            "_method": "delete",
        }
        response = self.session.post(
            f"{self.endpoint}/deck/{deck_id}",
            headers=header,
            data=payload,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(
                f"Failed to delete deck with id {deck_id} for {self.email}"
            )
        logger.info(f"Deleted deck with id {deck_id} for {self.email}.")

    @staticmethod
    def to_playable_deck(
        listed_deck: AbstractArchivedDeck,
        decks_cache_dir=AcademyFileSystem().ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR,
        use_cache=True,
    ) -> PlayableDeck:
        # TODO: fix ASSETS_DATA_DECK_MTGGOLDFISH_TOURNAMENT_DIR
        lines = None
        to_be_cached = True
        if use_cache:
            try:
                with open(
                    posix_path(decks_cache_dir, f"{listed_deck.deck_id}.txt"),
                    "r",
                ) as cache_f:
                    lines = [line[:-1] for line in cache_f.readlines()] + [
                        ""
                    ]  # for consistency with the original file
                    to_be_cached = False
            except FileNotFoundError:
                pass
        if not lines:
            lines = [MTGGOLDFISH_THROTTLE_ERROR_RESPONSE]
            while MTGGOLDFISH_THROTTLE_ERROR_RESPONSE in lines:
                content = urlopen(listed_deck.download_txt_url).read()
                lines = content.decode("utf-8")
                time.sleep(REQUESTS_SLEEP_SECONDS)
            lines = lines.split("\r\n")
        if to_be_cached:
            with open(
                posix_path(decks_cache_dir, f"{listed_deck.deck_id}.txt"),
                "w",
            ) as cache_f:
                cache_f.writelines("\n".join(lines))
        return parse_playable_deck_from_lines(lines)

    @cache
    def get_deck(self, deck_name: str) -> AbstractArchivedDeck:
        for deck in self.list_decks():
            if deck.p12e_name == deck_name:
                return deck
        raise ArchiveException(f"Unable to find deck with name {deck_name}.")
