from thousand.Card import Card


class State:

    def __init__(self, players_cards: list[list[Card]], turn: int) -> None:
        self.players_cards = players_cards
        self.turn = turn
        self.trump: int | None = None
        self.last: int | None = None
        self.cards_on_desk: list[Card] = []
        self.terminated = False

    def get_ansi(self):
        from textwrap import dedent
        return dedent(f"""
            player0: {[s.get_ansi() for s in self.players_cards[0]]} 
            player1: {[s.get_ansi() for s in self.players_cards[1]]} 
            player2: {[s.get_ansi() for s in self.players_cards[2]]} 

            turn: player{self.turn}
            last: {f'player{self.last}' if self.last is not None else 'nobody'}
            trump: {Card.suits[self.trump] if self.trump is not None else 'nothing'}

            cards_on_desk: {[s.get_ansi() for s in self.cards_on_desk]}
        """)

    def __hash__(self) -> int:
        h = 0
        for cards in self.players_cards:
            h ^= hash(tuple(cards))
        h ^= hash(self.turn)
        h ^= hash(tuple(self.cards_on_desk))
        h ^= hash(self.last)
        h ^= hash(self.trump)
        return h
