from gymnasium.envs.registration import register
from thousand.ThousandEnv import ThousandEnv

register(
    id="Thousand-v1",
    entry_point="thousand:ThousandEnv",
    max_episode_steps=200,
)
