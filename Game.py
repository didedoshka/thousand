from Card import Card
from State import State


class Game():

    marriage_reward = (40, 60, 80, 100)
    rank_reward = (0, 2, 3, 4, 10, 11)

    def __init__(self, state: State) -> None:
        self.state = state

    def get_state(self) -> State:
        return self.state

    def correct_moves(self) -> list[Card]:
        player_cards = self.state.players_cards[self.state.turn]
        if len(self.state.cards_on_desk) == 0:
            return player_cards
        player_cards_by_suits = {0: [], 1: [], 2: [], 3: []}
        for card in player_cards:
            player_cards_by_suits[card.get_suit()].append(card)

        first_card_suit = self.state.cards_on_desk[0].get_suit()
        if len(player_cards_by_suits[first_card_suit]) != 0:
            return player_cards_by_suits[first_card_suit]
        if self.state.trump is not None and len(player_cards_by_suits[self.state.trump]) != 0:
            return player_cards_by_suits[self.state.trump]
        return player_cards

    def is_marriage(self, move: Card) -> bool:
        return (move.get_rank() == 2 and Card(move.card + 4) in self.state.players_cards[self.state.turn]
                or move.get_rank() == 3 and Card(move.card - 4) in self.state.players_cards[self.state.turn])

    def get_reward_for_marriage(self, card: Card) -> int:
        return self.marriage_reward[card.get_suit()]

    def get_reward_for_rank(self, card: Card) -> int:
        return self.rank_reward[card.get_suit()]

    def get_winner(self) -> int:
        assert len(self.state.cards_on_desk) == 3, 'there should be three cards in order to find a winner'
        same_suit_as_first: list[tuple[Card, int]] = [(self.state.cards_on_desk[0], 0)]
        trumps: list[tuple[Card, int]] = []
        for i in [1, 2]:
            if self.state.cards_on_desk[i].get_suit() == self.state.cards_on_desk[0].get_suit():
                same_suit_as_first.append((self.state.cards_on_desk[i], i))

        for i in [0, 1, 2]:
            if self.state.cards_on_desk[i].get_suit() == self.state.trump:
                trumps.append((self.state.cards_on_desk[i], i))

        if len(trumps):
            return max(trumps)[1]

        return max(same_suit_as_first)[1]

    def count_reward(self) -> int:
        reward = 0
        for card in self.state.cards_on_desk:
            reward += self.get_reward_for_rank(card.get_rank())
        return reward

    def proceed_a_move(self, move: Card) -> tuple[int | None, int]:
        reward: tuple[int | None, int] = (None, 0)
        self.state.cards_on_desk.append(move)
        self.state.players_cards[self.state.turn].remove(move)
        if len(self.state.cards_on_desk) == 1 and self.is_marriage(move) and self.state.turn == self.state.last:
            reward = (self.state.turn, self.get_reward_for_marriage(move))
            self.state.trump = move.get_suit()
        if len(self.state.cards_on_desk) == 3:
            winner = self.get_winner()
            i_of_winner = ((self.state.turn - 2 + winner) + 3) % 3
            reward = (i_of_winner, self.count_reward())
            self.state.cards_on_desk = []
            self.state.last = i_of_winner
            self.state.turn = i_of_winner
        else:
            self.state.turn = (self.state.turn + 1) % 3

        return reward
