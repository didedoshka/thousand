class Card:
    ranks = ('9', 'J', 'Q', 'K', '10', 'A')
    suits = ('♠', '♣', '♦', '♥')

    def __init__(self, card) -> None:
        self.card = card

    def get_suit(self) -> int:
        return self.card % 4

    def get_rank(self) -> int:
        return self.card // 4

    def get_ansi(self) -> str:
        return self.ranks[self.get_rank()] + self.suits[self.get_suit()]
