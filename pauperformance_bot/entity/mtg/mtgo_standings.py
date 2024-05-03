from pauperformance_bot.util.decorators import auto_repr


@auto_repr
class MTGOStandingMatch:
    def __init__(
        self,
        player1,
        player1_ranking,
        player2,
        player2_ranking,
        match_score,
    ):
        self.player1 = player1
        self.player1_ranking = player1_ranking
        self.player2 = player2
        self.player2_ranking = player2_ranking
        self.match_score = match_score

    def __str__(self):
        return (
            f"{self.player1} ({self.player1_ranking}) vs "
            f"{self.player2} ({self.player2_ranking}) ({self.match_score}))"
        )

    def __hash__(self) -> int:
        return hash(repr(self))


@auto_repr
class MTGOStandings:
    def __init__(self, quarterfinals, semifinals, finals):
        self.quarterfinals = quarterfinals
        self.semifinals = semifinals
        self.finals = finals

    def __str__(self):
        return (
            f"Quarterfinals: {self.quarterfinals}. "
            f"Semifinals: {self.semifinals}. "
            f"Finals: {self.finals}"
        )

    def __hash__(self) -> int:
        return hash(repr(self))
