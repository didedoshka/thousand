from thousand.Card import Card
import textwrap


class State:

    number_of_players = 3

    def __init__(self, players_cards: list[list[Card]], turn: int) -> None:
        self.players_cards = players_cards
        self.turn = turn
        self.trump: int | None = None
        self.last: int | None = None
        self.cards_on_desk: list[Card] = []
        self.terminated = False

    def get_ansi(self):
        return textwrap.dedent(f"""
            player0: {[s.get_ansi() for s in self.players_cards[0]]} 
            player1: {[s.get_ansi() for s in self.players_cards[1]]} 
            player2: {[s.get_ansi() for s in self.players_cards[2]]} 

            turn: player{self.turn}
            last: {f'player{self.last}' if self.last is not None else 'nobody'}
            trump: {Card.suits[self.trump] if self.trump is not None else 'nothing'}

            cards_on_desk: {[s.get_ansi() for s in self.cards_on_desk]}
            """)

    def get_minimal_ansi(self):
        return textwrap.dedent(f"""{[s.get_ansi() for s in self.players_cards[0]]}{[s.get_ansi() for s in self.players_cards[1]]}{[s.get_ansi() for s in self.players_cards[2]]}tu{self.turn}la{self.last if self.last is not None else -1}tr{Card.suits[self.trump] if self.trump is not None else '-'}{[s.get_ansi() for s in self.cards_on_desk]}""")

    def __hash__(self) -> int:
        h = 0
        for i in range(3):
            h ^= hash((tuple(self.players_cards[i]), i))
        h ^= hash(self.turn)
        h ^= hash(tuple(self.cards_on_desk))
        if self.last is not None:
            h ^= hash(self.last + 100)
        if self.trump is not None:
            h ^= hash(self.trump + 1000)
        return h
