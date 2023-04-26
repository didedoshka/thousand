from thousand.Card import Card
from thousand.State import State
from copy import deepcopy
from typing import Optional

marriage_reward = (40, 60, 80, 100)
rank_reward = (0, 2, 3, 4, 10, 11)


def correct_moves(state) -> list[Card]:
    player_cards = deepcopy(state.players_cards[state.turn])
    if len(state.cards_on_desk) == 0:
        return player_cards
    player_cards_by_suits = {0: [], 1: [], 2: [], 3: []}
    for card in player_cards:
        player_cards_by_suits[card.get_suit()].append(card)

    first_card_suit = state.cards_on_desk[0].get_suit()
    if len(player_cards_by_suits[first_card_suit]) != 0:
        return player_cards_by_suits[first_card_suit]
    if state.trump is not None and len(player_cards_by_suits[state.trump]) != 0:
        return player_cards_by_suits[state.trump]
    return player_cards


def is_marriage(state: State, move: Card) -> bool:
    return (move.get_rank() == 2 and Card(move.card + 4) in state.players_cards[state.turn]
            or move.get_rank() == 3 and Card(move.card - 4) in state.players_cards[state.turn])


def get_reward_for_marriage(card: Card) -> int:
    return marriage_reward[card.get_suit()]


def get_reward_for_rank(card: Card) -> int:
    return rank_reward[card.get_rank()]


def get_winner(state: State) -> int:
    assert len(state.cards_on_desk) == 3, 'there should be three cards in order to find a winner'
    same_suit_as_first: list[tuple[Card, int]] = [(state.cards_on_desk[0], 0)]
    trumps: list[tuple[Card, int]] = []
    for i in [1, 2]:
        if state.cards_on_desk[i].get_suit() == state.cards_on_desk[0].get_suit():
            same_suit_as_first.append((state.cards_on_desk[i], i))

    for i in [0, 1, 2]:
        if state.cards_on_desk[i].get_suit() == state.trump:
            trumps.append((state.cards_on_desk[i], i))

    if len(trumps):
        return max(trumps)[1]

    return max(same_suit_as_first)[1]


def count_reward(state) -> int:
    reward = 0
    for card in state.cards_on_desk:
        reward += get_reward_for_rank(card)
    return reward


def move(state: State, move: Card) -> tuple[State, list[tuple[Optional[int], int]]]:
    next_state = deepcopy(state)
    reward: tuple[Optional[int], int] = (None, 0)
    next_state.cards_on_desk.append(move)
    next_state.players_cards[next_state.turn].remove(move)
    if len(next_state.cards_on_desk) == 1 and is_marriage(next_state, move) and next_state.turn == next_state.last:
        reward = (next_state.turn, get_reward_for_marriage(move))
        next_state.trump = move.get_suit()
    if len(next_state.cards_on_desk) == 3:
        winner = get_winner(next_state)
        i_of_winner = ((next_state.turn - 2 + winner) + 3) % 3
        reward = (i_of_winner, count_reward(next_state))
        next_state.cards_on_desk = []
        next_state.last = i_of_winner
        next_state.turn = i_of_winner
    else:
        next_state.turn = (next_state.turn + 1) % 3

    if len(next_state.players_cards[0]) + len(next_state.players_cards[1]) + len(next_state.players_cards[2]) == 0:
        next_state.terminated = True
    return next_state, [reward]

def get_players_rewards(rewards: list[tuple[Optional[int], int]]) -> tuple[int, int, int]:
    players_rewards = [0] * 3
    for who, what in rewards:
        if who is not None:
            players_rewards[who] += what

    return tuple(players_rewards)
