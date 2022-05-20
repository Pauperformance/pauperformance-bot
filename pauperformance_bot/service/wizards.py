import re
from typing import List

import requests
from pyquery import PyQuery

from pauperformance_bot.constant.wizards import PAUPER_CHALLENGE_TOURNAMENT_CLASSES
from pauperformance_bot.entity.mtgo_standings import MTGOStandingMatch, MTGOStandings
from pauperformance_bot.exceptions import WizardsException
from pauperformance_bot.util.log import get_application_logger

logger = get_application_logger()


def _parse_match_result(player1_line, player2_line) -> MTGOStandingMatch:
    result = re.search(r"\(([0-9]+)\) (\w+), ([0-9-]+)", player1_line)
    player1_ranking, player1, match_score = result.groups()
    result = re.search(r"\(([0-9]+)\) (\w+)", player2_line)
    player2_ranking, player2 = result.groups()
    return MTGOStandingMatch(
        player1,
        player1_ranking,
        player2,
        player2_ranking,
        match_score,
    )


def _parse_round_results(pq, round_class) -> List[MTGOStandingMatch]:
    logger.debug(f"Inspecting class: {round_class}...")
    matches: List[MTGOStandingMatch] = []
    buffer = []
    for player in pq(round_class).items():
        logger.debug(f"Parsing: {player.text()}")
        buffer.append(player.text())
        if len(buffer) == 2:
            matches.append(_parse_match_result(*buffer))
            logger.debug(f"Match: {matches[-1]}")
            buffer = []
    logger.debug(f"Inspected class: {round_class}.")
    return matches


class WizardsService:
    def __init__(self):
        pass

    def parse_mtgo_pauper_challenge(self, url: str) -> MTGOStandings:
        response = requests.get(url)
        if response.status_code != 200:
            raise WizardsException(f"Failed to load standings from url: {url}")
        logger.debug(f"Parsing standings from url: {url}...")
        pq = PyQuery(response.content)
        standings = MTGOStandings(
            *(
                _parse_round_results(
                    pq,
                    player_class,
                )
                for player_class in PAUPER_CHALLENGE_TOURNAMENT_CLASSES
            )
        )
        logger.info(f"MTGO standings: {standings}.")
        logger.debug(f"Parsed standings from url: {url}.")
        return standings
