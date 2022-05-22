from pauperformance_bot.util.entities import auto_repr


@auto_repr
class PlayedCard:
    def __init__(self, quantity, card_name):
        if isinstance(quantity, str):
            quantity = int(quantity)
        self.quantity = quantity
        self.card_name = card_name

    def __str__(self):
        return f"{self.quantity} {self.card_name}"

    def __hash__(self) -> int:
        return hash(repr(self))
