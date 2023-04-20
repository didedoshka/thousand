from thousand.Card import Card
import textwrap
from typing import Optional

class State:

    number_of_players = 3

    def __init__(self, players_cards: list[list[Card]], turn: int) -> None:
        self.players_cards = players_cards
        self.turn = turn
        self.trump: Optional[int] = None
        self.last: Optional[int] = None
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
        return f"""{[s.get_ansi() for s in self.players_cards[0]]}{[s.get_ansi() for s in self.players_cards[1]]}{[s.get_ansi() for s in self.players_cards[2]]}tu{self.turn}la{self.last if self.last is not None else '-'}tr{Card.suits[self.trump] if self.trump is not None else '-'}{[s.get_ansi() for s in self.cards_on_desk]}"""

    def __hash__(self) -> int:
        h = 0
        for player_cards in self.players_cards:
            for card in player_cards:
                h = h * 100 + (card.card + 1)

        h = h * 10 + (self.turn + 1)
        for card in self.cards_on_desk:
            h = h * 100 + (card.card + 1)
        if self.last is None:
            h = h * 10 + 4
        else:
            h = h * 10 + (self.last + 1)

        if self.trump is None:
            h = h * 10 + 5
        else:
            h = h * 10 + (self.trump + 1)
        return h
