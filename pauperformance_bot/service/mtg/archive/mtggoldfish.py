from datetime import datetime
from functools import wraps
from itertools import count
from urllib.request import urlopen

from pyquery import PyQuery
from requests import session

from pauperformance_bot.constant.mtggoldfish import (
    API_ENDPOINT,
    DECK_API_ENDPOINT,
)
from pauperformance_bot.constant.myr import (
    MTGGOLDFISH_DECKS_CACHE_DIR,
    USA_DATE_FORMAT,
)
from pauperformance_bot.credentials import (
    MTGGOLDFISH_PAUPERFORMANCE_PASSWORD,
    MTGGOLDFISH_PAUPERFORMANCE_USERNAME,
)
from pauperformance_bot.entity.deck.archive.mtggoldfish import (
    MTGGoldfishArchivedDeck,
)
from pauperformance_bot.entity.deck.playable import (
    parse_playable_deck_from_lines,
)
from pauperformance_bot.exceptions import MTGGoldfishException
from pauperformance_bot.service.mtg.archive.abstract import (
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
        storage,  # TODO: remove with list_decks() workaround ASAP
        email=MTGGOLDFISH_PAUPERFORMANCE_USERNAME,
        password=MTGGOLDFISH_PAUPERFORMANCE_PASSWORD,
        endpoint=API_ENDPOINT,
        deck_api_endpoint=DECK_API_ENDPOINT,
    ):
        self.storage = storage
        self.email = email
        self.password = password
        self.endpoint = endpoint
        self.deck_api_endpoint = deck_api_endpoint
        self.session = session()
        self.logged = False

    def login(self):
        logger.info(f"Logging to MTGGoldfish as {self.email}...")
        payload = {
            "action": "login",
            "auth_key": self.email,
            "password": self.password,
            "commit": "Log In",
        }
        response = self.session.post(
            f"{self.endpoint}/auth/identity/callback",
            data=payload,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(f"Failed to login for {self.email}")
        logger.debug(f"Header Set-Cookie: {response.headers['Set-Cookie']}")
        logger.debug(
            f"Session cookie: "
            f"_mtg_session={self.session.cookies['_mtg_session']}"
        )
        logger.debug(
            f"Response cookie: _mtg_session={response.cookies['_mtg_session']}"
        )
        logger.info(f"Logged to MTGGoldfish as {self.email}.")

    def get_uri(self, deck_id):
        return f"{self.deck_api_endpoint}/{deck_id}"

    @with_login
    def create_deck(self, name, description, playable_deck):
        return self._create_deck(
            name, description, playable_deck, format_="pauper"
        )

    def _create_deck(self, name, description, playable_deck, format_):
        logger.info(f"Creating deck {name} for {self.email}...")
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,image/apng,*/*;"
            "q=0.8,application/signed-exchange;"
            "v=b3;"
            "q=0.9",
        }
        payload = {
            "utf8": "✓",
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
            raise MTGGoldfishException(
                f"Failed to create deck {name} for {self.email}"
            )
        deck_id = response.request.url.split("/")[-1]
        logger.info(f"Created deck {name} for {self.email}. Id: {deck_id}")
        return deck_id

    @with_login
    def list_decks(self, filter_name=""):
        return self._list_decks(
            filter_name=filter_name, format_="pauper", visibility="public"
        )

    def _list_decks(self, filter_name, format_, visibility):
        all_decks = []
        for page in count(1):
            new_decks = self._list_decks_in_page(
                page,
                filter_name=filter_name,
                format_=format_,
                visibility=visibility,
            )
            if len(new_decks) == 0:
                break
            all_decks += new_decks
        logger.warning("Fixing bug in MTGGoldfish pager...")

        # TODO: remove whenever possible
        # Due to a bug in the pagination mechanism, decks are sometimes
        # returned more than once or not returned at all.

        # first, let's remove duplicates
        logger.warning(f"Initial number of decks: {len(all_decks)}")
        all_decks = list(set(all_decks))
        logger.warning(f"Without duplicates: {len(all_decks)}")
        # then, grab one-by-one all the missing decks from storage
        storage_decks = self.storage.list_imported_deckstats_deck_names()
        mtggoldfish_decks = {d.name for d in all_decks}
        for missing_deck in storage_decks - mtggoldfish_decks:
            logger.warning(f"Found missing deck: {missing_deck}")
            missing_deck = self._list_decks_in_page(1, missing_deck)
            if len(missing_deck) != 1:
                raise ValueError(f"Unable to find missing deck {missing_deck}")
            all_decks += missing_deck
        logger.warning(f"Final number of decks: {len(all_decks)}")
        return sorted(all_decks, key=lambda d: d.name)

    @with_login
    def _list_decks_in_page(
        self, page, filter_name="", format_="pauper", visibility="public"
    ):
        # possible filter_visibility values: '', 'private', 'public'
        logger.info(f"Listing decks for {self.email} in page {page}...")
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,image/apng,*/*;"
            "q=0.8,application/signed-exchange;"
            "v=b3;"
            "q=0.9",
        }
        params = {
            "filter_name": filter_name,
            "filter_format": format_,
            "filter_visibility": visibility,
            "commit": "Filter",
        }
        response = self.session.get(
            f"{self.endpoint}/decks?page={page}",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(
                f"Failed to list decks for {self.email}"
            )
        logger.debug(f"Parsing page with decks for {self.email}...")
        pq = PyQuery(response.content)
        decks = []
        for c in pq("table tbody tr").items():
            row = c.text()
            _, name, _, format_, creation_date, visibility, _, _ = row.split(
                "\n"
            )
            creation_date = datetime.strptime(creation_date, USA_DATE_FORMAT)
            creation_date = 1000 * int(creation_date.timestamp())
            url = next(link.attrib["href"] for link in c("a"))
            logger.debug(f"Deck {name} has url: {url}")
            deck_id = url.split("/")[-1]
            decks.append(MTGGoldfishArchivedDeck(name, creation_date, deck_id))
        logger.info(f"Found {len(decks)} decks: {decks}")
        logger.info(f"Listed decks for {self.email}.")
        return decks

    @with_login
    def delete_deck(self, deck_id):
        logger.info(f"Deleting deck with id {deck_id} for {self.email}...")
        header = {
            "accept": "text/html,application/xhtml+xml,application/xml;"
            "q=0.9,image/avif,image/webp,image/apng,*/*;"
            "q=0.8,application/signed-exchange;"
            "v=b3;"
            "q=0.9",
        }
        payload = {
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
        listed_deck,
        decks_cache_dir=MTGGOLDFISH_DECKS_CACHE_DIR,
        use_cache=True,
    ):
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
            content = urlopen(listed_deck.download_txt_url).read()
            lines = content.decode("utf-8").split("\r\n")
        if to_be_cached:
            with open(
                posix_path(decks_cache_dir, f"{listed_deck.deck_id}.txt"),
                "w",
            ) as cache_f:
                cache_f.writelines("\n".join(lines))
        return parse_playable_deck_from_lines(lines)
