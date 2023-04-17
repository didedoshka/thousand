import numpy as np

import gymnasium as gym
from gymnasium import spaces

from Card import Card
from State import State
from Game import Game
from typing import Any


class Thousand(gym.Env):
    """
    Gym environment for card game "Thousand"
    Second player in the game is the one we train and call "agent"

    Attributes
    ----------
    observation_space : gym.MultiDiscrete
        First 24 values are a mask of agent cards, second 24 values are a mask of already seen cards, third 24 values are a mask of first card on table, fourth 24 values are a mask of second card on table, next 4 values are a mask of current trump, the last value is whether or not last trick was taken

    action_space : gym.Discrete 
        24 moves as each card can be a move

    game : Game
        current game state
    """
    metadata = {"render_modes": ["ansi"]}

    def __init__(self, render_mode: str | None = None):
        self.observation_space = spaces.MultiBinary(101)
        self.action_space = spaces.Discrete(24)

        self.render_mode = render_mode

    def _is_terminated(self) -> bool:
        return self.game.state.terminated

    def _play_until_agent(self) -> list[tuple[int | None, int]]:
        rewards = []
        while self.game.state.turn != 2 and not self._is_terminated():
            rewards.append(self.game.proceed_a_move(self._make_a_move()))
        return rewards

    def _make_a_move(self):
        move = self.players[self.game.state.turn].make_a_move(self._get_observation(), self._get_info())
        correct_moves = self.game.correct_moves()
        if move not in correct_moves:
            move = self.np_random.choice(correct_moves)
        return move

    def _get_observation(self):
        observation = np.zeros(101, dtype=bool)
        for player_card in self.game.state.players_cards[self.game.state.turn]:
            observation[player_card.card] = 1

        unseen_cards = [0] * 24
        for player in [0, 1, 2]:
            for card in self.game.state.players_cards[player]:
                unseen_cards[card.card] = 1

        for card in range(24):
            if not unseen_cards[card]:
                observation[24 + card] = 1

        if len(self.game.state.cards_on_desk) >= 1:
            observation[2 * 24 + self.game.state.cards_on_desk[0].card] = 1

        if len(self.game.state.cards_on_desk) >= 2:
            observation[3 * 24 + self.game.state.cards_on_desk[1].card] = 1

        if self.game.state.trump is not None:
            observation[4 * 24 + self.game.state.trump] = 1

        if self.game.state.last == self.game.state.turn:
            observation[4 * 24 + 4] = 1

        return observation

    def _get_info(self):
        return {"correct_moves": self.game.correct_moves()}

    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):
        """
        Resets the environment to an initial internal state, returning an initial observation and info.
        Parameters
        ----------
            options: dict containing two players inherited from Player class. Their incorrect moves will be replaced with random correct ones

        Returns
        -------
            observation: Observation of the initial state. This will be an element of :attr:`observation_space`
            info (dict): "correct_moves" contains correct moves in current state
        """
        super().reset(seed=seed)

        self.players = options['players']

        deck_of_cards = np.arange(24)
        self.np_random.shuffle(deck_of_cards)

        players_cards = [[Card(s) for s in sorted(deck_of_cards[0:8])], [Card(s) for s in sorted(deck_of_cards[8:16])],
                         [Card(s) for s in sorted(deck_of_cards[16:24])]]
        turn = self.np_random.integers(3)
        self.game = Game(State(players_cards, turn))
        self.rewards: list[tuple[int | None, int]] = self._play_until_agent()

        observation = self._get_observation()
        info = self._get_info()

        return observation, info

    def step(self, action: int):
        """
        Run one timestep of the environment's dynamics using the agent actions.
        Args:
            action: an action provided by the agent to update the environment state.

        Returns:
            observation: An element of the environment's :attr:`observation_space` as the next observation due to the agent actions.
            info (dict): "correct_moves" contains correct moves in current state
        """
        move = Card(action)
        correct_moves = self.game.correct_moves()
        if move not in correct_moves:
            observation = self._get_observation()
            info = self._get_info()
            return observation, -5, False, False, info
        current_rewards = [self.game.proceed_a_move(move)]
        terminated = self._is_terminated()
        if not terminated:
            current_rewards += self._play_until_agent()

        second_player_reward = 0

        for player, amount in current_rewards:
            if player == 2:
                second_player_reward += amount

        self.rewards += current_rewards

        terminated = self._is_terminated()
        observation = self._get_observation()
        info = self._get_info()
        return observation, second_player_reward, terminated, False, info

    def render(self):
        return self.game.state.get_ansi() + f'rewards are {self.rewards}'
