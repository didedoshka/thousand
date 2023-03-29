from thousand.thousand import GridWorldEnv

from gymnasium.envs.registration import register

register(
    id="thousand-v0",
    entry_point="thousand:Thousand",
    max_episode_steps=300,
)