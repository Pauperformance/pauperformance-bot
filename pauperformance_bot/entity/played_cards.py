class PlayedCard:
    def __init__(self, quantity, card_name):
        if isinstance(quantity, str):
            quantity = int(quantity)
        self.quantity = quantity
        self.card_name = card_name

    def __str__(self):
        return f"{self.quantity} {self.card_name}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return hash(str(self))
