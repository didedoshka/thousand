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
        self.observation_space = spaces.MultiDiscrete([2] * 101)
        self.action_space = spaces.Discrete(24)

        self.render_mode = render_mode

    def _is_terminated(self):
        return len(self.played_cards) == 24

    def _play_until_agent(self):
        rewards = []
        while self.turn != 2 and not self._is_terminated():
            rewards.append(self._proceed_a_move(self._make_a_move()))
        return rewards

    def _make_a_move(self):
        move = self.players[self.turn].make_a_move(self._get_observation(), self._get_info())
        correct_moves = self._correct_moves()
        if move not in correct_moves:
            logging.warning(f'move {move} of player{self.turn} was incorrect')
            move = self.np_random.choice(correct_moves)
        return move

    def _get_observation(self):
        observation = np.zeros(101, dtype=int)
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

        self.rewards = [0, 0, 0]

        self._play_until_agent()

        observation = self._get_observation()
        info = self._get_info()

        return observation, info

    def step(self, action):
        """
        Run one timestep of the environment's dynamics using the agent actions.
        Args:
            action: an action provided by the agent to update the environment state.

        Returns:
            observation: An element of the environment's :attr:`observation_space` as the next observation due to the agent actions.
            info (dict): "correct_moves" contains correct moves in current state
        """
        correct_moves = self._correct_moves()
        if action not in correct_moves:
            observation = self._get_observation()
            return observation, -5, False, False, {}
        rewards = [self._proceed_a_move(action)]
        terminated = self._is_terminated()
        if not terminated:
            rewards += self._play_until_agent()
        reward = 0

        for player, one_reward in rewards:
            if player == 2:
                reward += one_reward

        terminated = self._is_terminated()
        observation = self._get_observation()
        info = self._get_info()
        return observation, reward, terminated, False, info

    def render(self):
        rendering_view = f"""
        last trick was won by {self.last}
        
        current rewards = {self.rewards}
        
        player0 cards = {[(self._name_of_a_card_by_number(i), i) for i in self.players_cards[0]]}
        player1 cards = {[(self._name_of_a_card_by_number(i), i) for i in self.players_cards[1]]}
        player2 cards = {[(self._name_of_a_card_by_number(i), i) for i in self.players_cards[2]]}
        
        cards on desk = {[self._name_of_a_card_by_number(i) for i in self.cards_on_desk]}
        """

        return rendering_view


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    logging.info("Started in main")

    thou = Thousand(render_mode='ansi')

    obs, info = thou.reset(seed=int(input()), options={'players': [Player(), Player()]})
    terminated = False
    full_reward = 0
    while not terminated:
        print(thou.render())
        action = int(input())
        obs, reward, terminated, trunc, info = thou.step(action)
        full_reward += reward
        print(reward)

    print(full_reward)
