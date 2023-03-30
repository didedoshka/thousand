import numpy as np
import pygame

import gymnasium as gym
from gymnasium import spaces

import logging
from abc import ABC, abstractmethod


class Player():
    @abstractmethod
    def make_a_move(self, observation):
        pass


class SmallestPlayer(Player):
    def make_a_move(self, observation):
        for i in range(0, 24):
            if observation[i] == 1:
                return i


class Thousand(gym.Env):
    r"""
    Gym environment for card game "Thousand"
    Second player in the game is the one we train and call "agent"

    Attributes

    - :attr:`observation_space` - gym.MulitDiscrete
        First 24 values correspond to cards. Possible values

        - 0 if never seen
        - 1 if in hand
        - 2 if played already
        - 3 if first on table
        - 4 if second on table.

        25th value corresponds to trump
        26th value corresponds to whether or not last trick was taken
    - :attr:`cards` - list of cards
    """
    metadata = {"render_modes": ["human", "ansi"], "render_fps": 4}
    cards = ['9♠', '9♣', '9♦', '9♥',
             'J♠', 'J♣', 'J♦', 'J♥',
             'Q♠', 'Q♣', 'Q♦', 'Q♥',
             'K♠', 'K♣', 'K♦', 'K♥',
             '10♠', '10♣', '10♦', '10♥',
             'A♠', 'A♣', 'A♦', 'A♥']
    suits = ['S', 'C', 'D', 'H']
    marriage_reward = [40, 60, 80, 100]
    card_reward = [0, 2, 3, 4, 10, 11]

    def __init__(self, render_mode=None):
        self.observation_space = spaces.MultiDiscrete([5] * 24 + [4] + [2])
        logging.info(f'observation_space set to {self.observation_space}')

        self.action_space = spaces.Discrete(24)
        logging.info(f'action_space set to {self.action_space}')

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        logging.info(f'render_mode set to {self.render_mode}')

    def reset(self, *, seed=None, options=None):
        """
        Resets the environment to an initial internal state, returning an initial observation and info.
        Args:
            options: dict containing two players inherited from Player class. Their incorrect moves will be replaced with random correct ones
            :param *:
        """
        super().reset(seed=seed)

        self.players = options['players']
        logging.info(f'players set to {self.players}')

        deck_of_cards = np.arange(24)
        self.np_random.shuffle(deck_of_cards)

        self.players_cards = [sorted(deck_of_cards[0:8]), sorted(deck_of_cards[8:16]), sorted(deck_of_cards[16:24])]
        logging.info(f'players_cards set to {self.players_cards}')

        self.turn = self.np_random.integers(3)
        logging.info(f'turn set to {self.turn}')

        self.played_cards = []
        self.trump = None
        self.last = None

        self.cards_on_desk = []

        self._play_until_agent()

        observation = self._get_observation()

        return observation, {}

    def _play_until_agent(self):
        rewards = []
        while self.turn != 2:
            rewards.append(self._proceed_a_move(self._make_a_move()))
        return rewards

    def _get_suit(self, card):
        return card % 4

    def _correct_moves(self):
        player_cards = self.players_cards[self.turn]
        if len(self.cards_on_desk) == 0:
            return player_cards
        player_cards_by_suits = {0: [], 1: [], 2: [], 3: []}
        for card in player_cards:
            player_cards_by_suits[self._get_suit(card)].append(card)

        first_card_suit = self._get_suit(self.cards_on_desk[0])
        if len(player_cards_by_suits[first_card_suit]) != 0:
            return player_cards_by_suits[first_card_suit]
        if self.trump is not None and len(player_cards_by_suits[self.trump]) != 0:
            return player_cards_by_suits[self.trump]
        return player_cards

    def _is_marriage(self, move):
        if move < 8 or move >= 16:
            return False
        if move < 12 and (move + 4) in self.players_cards[self.turn]:
            return True
        if move >= 12 and (move - 4) in self.players_cards[self.turn]:
            return True
        return False

    def _get_winner(self):
        same_suit_as_first = [(self.cards_on_desk[0], 0)]
        trumps = []
        for i in [1, 2]:
            if self._get_suit(self.cards_on_desk[i]) == self._get_suit(self.cards_on_desk[0]):
                same_suit_as_first.append((self.cards_on_desk[i], i))

        for i in [0, 1, 2]:
            if self._get_suit(self.cards_on_desk[i]) == self.trump:
                trumps.append((self.cards_on_desk[i], i))

        if len(trumps):
            return max(trumps)[1]

        return max(same_suit_as_first)[1]

    def _count_reward(self):
        reward = 0
        for card in self.cards_on_desk:
            reward += self.card_reward[card // 4]

        return reward

    def _proceed_a_move(self, move):
        logging.info(f'player {self.turn} makes move {move}')
        reward = (None, 0)
        self.cards_on_desk.append(move)
        self.players_cards[self.turn].remove(move)
        logging.info(f'card {move} removed from player{self.turn} {self.players_cards[self.turn]}')
        if len(self.cards_on_desk) == 1 and self._is_marriage(move) and self.turn == self.last:
            reward = (self.turn, self.marriage_reward[self._get_suit(move)])
            self.trump = self._get_suit(move)
        if len(self.cards_on_desk) == 3:
            winner = self._get_winner()
            i_of_winner = ((self.turn - 2 + winner) + 3) % 3
            reward = (i_of_winner, self._count_reward())
            self.played_cards += self.cards_on_desk
            self.cards_on_desk = []
            self.last = i_of_winner
            self.turn = i_of_winner
        else:
            self.turn = (self.turn + 1) % 3

        return reward

    def _make_a_move(self):
        move = self.players[self.turn].make_a_move(self._get_observation())
        correct_moves = self._correct_moves()
        if move not in correct_moves:
            move = self.np_random.choice(correct_moves)
        return move

    def step(self, action):
        correct_moves = self._correct_moves()
        if action not in correct_moves:
            observation = self._get_observation()
            return observation, -10, False, False, {}
        rewards = [self._proceed_a_move(action)]
        rewards += self._play_until_agent()
        reward = 0

        for pl, r in rewards:
            if pl == 2:
                reward += r

        observation = self._get_observation()
        terminated = self._is_terminated()
        return observation, reward, terminated, False, {}

    def _is_terminated(self):
        return len(self.played_cards) == 24

    def _get_observation(self):
        observation = np.zeros(25, dtype=int)
        for card in self.players_cards[self.turn]:
            observation[card] = 1
        for card in self.played_cards:
            observation[card] = 2
        if len(self.cards_on_desk) >= 1:
            observation[self.cards_on_desk[0]] = 3
        if len(self.cards_on_desk) >= 2:
            observation[self.cards_on_desk[1]] = 4

        observation[24] = self.turn == self.last

        logging.info(f'observation for player{self.turn} is {observation}')

        return observation

    def _name_of_a_card_by_number(self, card):
        return self.cards[card]

    def render(self):
        rendering_view = f"""
        last trick was won by {self.last}
        
        player0 cards = {[(self._name_of_a_card_by_number(i), i) for i in self.players_cards[0]]}
        player1 cards = {[(self._name_of_a_card_by_number(i), i) for i in self.players_cards[1]]}
        player2 cards = {[(self._name_of_a_card_by_number(i), i) for i in self.players_cards[2]]}
        
        cards on desk = {[self._name_of_a_card_by_number(i) for i in self.cards_on_desk]}
        """

        return rendering_view


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Started in main")

    thou = Thousand(render_mode='ansi')

    obs, info = thou.reset(seed=0, options={'players': [SmallestPlayer(), SmallestPlayer()]})
    terminated = False
    while not terminated:
        print(thou.render())
        action = int(input())
        obs, reward, terminated, trunc, info = thou.step(action)
        print(reward)
