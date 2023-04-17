from Card import Card


class State:

    def __init__(self, players_cards: list[list[Card]], turn: int) -> None:
        self.players_cards = players_cards
        self.turn = turn
        self.trump = None
        self.last = None
        self.cards_on_desk = []
