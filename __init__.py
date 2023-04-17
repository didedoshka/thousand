from thousand.thousand import Thousand, Player

from gymnasium.envs.registration import register

register(
    id="Thousand-v0",
    entry_point="thousand:Thousand",
    max_episode_steps=2000,
)
