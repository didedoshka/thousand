from Card import Card


class State:

    def __init__(self, players_cards: list[list[Card]], turn: int) -> None:
        self.players_cards = players_cards
        self.turn = turn
        self.trump = None
        self.last = None
        self.cards_on_desk = []

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
