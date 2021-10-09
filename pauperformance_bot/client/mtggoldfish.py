from datetime import datetime
from itertools import count

from pyquery import PyQuery
from requests import session
from urllib.request import urlopen

from pauperformance_bot.client.dropbox_ import Dropbox
from pauperformance_bot.constant.mtggoldfish import API_ENDPOINT
from pauperformance_bot.constant.myr import USA_DATE_FORMAT, MTGGOLDFISH_DECKS_CACHE_DIR
from pauperformance_bot.entity.deck.mtggoldfish import ListedMTGGoldfishDeck
from pauperformance_bot.entity.deck.playable import PlayableDeck
from pauperformance_bot.entity.played_cards import PlayedCard
from pauperformance_bot.exceptions import MTGGoldfishException
from pauperformance_bot.credentials import MTGGOLDFISH_SHIKA93_PASSWORD, MTGGOLDFISH_SHIKA93_USERNAME, \
    MTGGOLDFISH_PAUPERFORMANCE_USERNAME, MTGGOLDFISH_PAUPERFORMANCE_PASSWORD
from pauperformance_bot.util.log import get_application_logger
from pauperformance_bot.util.path import posix_path

logger = get_application_logger()


class MTGGoldfish:
    def __init__(
            self,
            email=MTGGOLDFISH_PAUPERFORMANCE_USERNAME,
            password=MTGGOLDFISH_PAUPERFORMANCE_PASSWORD,
            endpoint=API_ENDPOINT,
            dropbox=Dropbox(),  # TODO: remove when list_decks() workaround is not needed
    ):
        self.email = email
        self.password = password
        self.endpoint = endpoint
        self.dropbox = dropbox
        self.session = session()
        self._login()

    def _login(self):
        logger.info(f"Logging to MTGGoldfish as {self.email}...")
        payload = {
            'action': 'login',
            'auth_key': self.email,
            'password': self.password,
            'commit': 'Log In',
        }
        response = self.session.post(
            f"{self.endpoint}/auth/identity/callback",
            data=payload,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(f"Failed to login for {self.email}")
        logger.debug(f"Header Set-Cookie: {response.headers['Set-Cookie']}")
        logger.debug(f"Session cookie: _mtg_session={self.session.cookies['_mtg_session']}")
        logger.debug(f"Response cookie: _mtg_session={response.cookies['_mtg_session']}")
        logger.info(f"Logged to MTGGoldfish as {self.email}.")

    def create_deck(self, name, description, playable_deck, format='pauper'):
        logger.info(f"Creating deck {name} for {self.email}...")
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;'
                      'v=b3;'
                      'q=0.9',
        }
        payload = {
            'utf8': '✓',
            'deck_input[name]': name,
            'deck_input[description]': description,
            'deck_input[format]': format,
            'deck_input[commander]': '',
            'deck_input[commander_alt]': '',
            'deck_input[companion]': '',
            'deck_input[private]': '0',
            'deck_input[specific_cards]': '0',
            'deck_input[deck]': playable_deck.mainboard_mtggoldfish,
            'card_name': '',
            'quantity': '1',
            'deck_input[sideboard]': playable_deck.sideboard_mtggoldfish,
            'commit': 'Save',
        }
        response = self.session.post(
            f"{self.endpoint}/decks",
            headers=headers,
            data=payload,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(f"Failed to create deck {name} for {self.email}")
        deck_id = response.request.url.split('/')[-1]
        logger.info(f"Created deck {name} for {self.email}. Id: {deck_id}")
        return deck_id

    def list_decks(self, filter_name='', format_='pauper', visibility='public'):
        all_decks = []
        for page in count(1):
            new_decks = self._list_decks_in_page(page, filter_name=filter_name, format_=format_, visibility=visibility)
            if len(new_decks) == 0:
                break
            all_decks += new_decks
        logger.warning("Fixing bug in MTGGoldfish pager...")
        # TODO: remove whenever possible
        # due to a bug in the pagination mechanism, decks are sometimes returned more than once or not returned at all
        # first, let's remove duplicates
        logger.warning(f"Initial number of decks: {len(all_decks)}")
        all_decks = list(set(all_decks))
        logger.warning(f"Without duplicates: {len(all_decks)}")
        # then, grab one-by-one all the missing decks from dropbox
        dropbox_decks = self.dropbox.get_imported_deckstats_deck_names()
        mtggoldfish_decks = {d.name for d in all_decks}
        for missing_deck in dropbox_decks - mtggoldfish_decks:
            logger.warning(f"Found missing deck: {missing_deck}")
            missing_deck = self._list_decks_in_page(1, missing_deck)
            if len(missing_deck) != 1:
                raise ValueError(f"Unable to find missing deck {missing_deck}")
            all_decks += missing_deck
        logger.warning(f"Final number of decks: {len(all_decks)}")
        return sorted(all_decks, key=lambda d: d.name)

    def _list_decks_in_page(self, page, filter_name='', format_='pauper', visibility='public'):
        logger.info(f"Listing decks for {self.email} in page {page}...")
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;'
                      'v=b3;'
                      'q=0.9',
            # 'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,it;q=0.7,de;q=0.6',
        }
        params = {
            # 'utf8': '✓',
            # 'panel': '#tab-all',
            'filter_name': filter_name,
            'filter_format': format_,
            'filter_visibility': visibility,  # possible values: '', 'private', 'public'
            'commit': 'Filter',
        }
        response = self.session.get(
            f"{self.endpoint}/decks?page={page}",
            headers=headers,
            params=params,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(f"Failed to list decks for {self.email}")
        logger.debug(f"Parsing page with decks for {self.email}...")
        pq = PyQuery(response.content)
        decks = []
        for c in pq('table tbody tr').items():
            row = c.text()
            _, name, _, format_, creation_date, visibility, _, _ = row.split('\n')
            creation_date = datetime.strptime(creation_date, USA_DATE_FORMAT)
            creation_date = 1000 * int(creation_date.timestamp())
            url = next(link.attrib['href'] for link in c('a'))
            logger.debug(f"Deck {name} has url: {url}")
            deck_id = url.split('/')[-1]
            decks.append(ListedMTGGoldfishDeck(name, format_, creation_date, visibility, deck_id))
        logger.info(f"Found {len(decks)} decks: {decks}")
        logger.info(f"Listed decks for {self.email}.")
        return decks

    def delete_deck(self, deck_id):
        logger.info(f"Deleting deck with id {deck_id} for {self.email}...")
        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;'
            'q=0.9,image/avif,image/webp,image/apng,*/*;'
            'q=0.8,application/signed-exchange;'
            'v=b3;'
            'q=0.9',
        }
        payload = {
            '_method': 'delete',
        }
        response = self.session.post(
            f"{self.endpoint}/deck/{deck_id}",
            headers=header,
            data=payload,
        )
        if response.status_code != 200:
            raise MTGGoldfishException(f"Failed to delete deck with id {deck_id} for {self.email}")
        logger.info(f"Deleted deck with id {deck_id} for {self.email}.")

    def to_playable_deck(self, listed_mtggoldfish_deck, decks_cache_dir=MTGGOLDFISH_DECKS_CACHE_DIR, use_cache=True):
        lines = None
        to_be_cached = True
        if use_cache:
            try:
                with open(posix_path(decks_cache_dir, f"{listed_mtggoldfish_deck.deck_id}.txt"), "r") as cache_f:
                    lines = [line[:-1] for line in cache_f.readlines()] + ['']  # for consistency with the original file
                    to_be_cached = False
            except FileNotFoundError:
                pass
        if not lines:
            content = urlopen(listed_mtggoldfish_deck.download_txt_url).read()
            lines = content.decode('utf-8').split('\r\n')
        if to_be_cached:
            with open(posix_path(decks_cache_dir, f"{listed_mtggoldfish_deck.deck_id}.txt"), "w") as cache_f:
                cache_f.writelines('\n'.join(lines))
        separator = lines.index('')
        maindeck = lines[:separator]
        sideboard = lines[separator+1:-1]
        return PlayableDeck(
            [PlayedCard(*(line.split(' ', maxsplit=1))) for line in maindeck],
            [PlayedCard(*(line.split(' ', maxsplit=1))) for line in sideboard],
        )


def main():
    # mtggoldfish = MTGGoldfish(MTGGOLDFISH_SHIKA93_USERNAME, MTGGOLDFISH_SHIKA93_PASSWORD)
    mtggoldfish = MTGGoldfish()
    all_decks = mtggoldfish.list_decks()
    for d in all_decks:
        if 'Affinity 676.002.MrEvilEye' in d.name:
            print('Found')
    all_decks = mtggoldfish.list_decks(filter_name='Affinity 676.002.MrEvilEye')
    print(all_decks)
    # for d in all_decks:
        # mtggoldfish.delete_deck(d[-1])
    # main = [PlayedCard(4, "Island"), PlayedCard(4, "Swamp")]
    # sideboard = [PlayedCard(4, "Plains"), PlayedCard(4, "Forest")]
    # deck = PlayableDeck(main, sideboard)
    # deck_id = mtggoldfish.create_deck('TEST API', 'My fucking description', deck, '15 Island')
    # mtggoldfish.list_decks()
    # mtggoldfish.delete_deck(deck_id)
    # mtggoldfish.list_decks()


if __name__ == '__main__':
    main()
