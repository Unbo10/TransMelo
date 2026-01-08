from __future__ import annotations

from typing import Optional

import gymnasium as gym
from gymnasium import spaces
import numpy as np

from .config import BRTConfig
from .world import World


class BRTEnv(gym.Env):
    """
    Gymnasium environment wrapping the TransMelo world.

    Provides observation and action spaces, and delegates stepping/resetting
    to the underlying World simulator.
    """
    metadata = {"render_modes": []}

    def __init__(self, config: Optional[BRTConfig] = None):
        """
        Initialize the environment and construct observation/action spaces.

        Parameters
        ----------
        config : BRTConfig, optional
            Environment configuration. Default is `BRTConfig.default()`.
        """
        super().__init__()
        self.config = config or BRTConfig.default()
        self.world = World(self.config)
        self.world.reset()

        obs_dim = self.world.observation_dim()
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(obs_dim,), dtype=np.float32
        ) #*all features normalized in [0,1] except time (in [-1,1])
        action_sizes = []
        #*Add dispatch actions and transfers per terminal
        for terminal_id in self.world.terminal_order:
            action_sizes.append(len(self.world.dispatch_options.get(terminal_id, [])) + 1)
        for terminal_id in self.world.terminal_order:
            action_sizes.append(len(self.world.transfer_options.get(terminal_id, [])) + 1)
        self.action_space = spaces.MultiDiscrete(action_sizes)

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """
        Reset the environment.

        Parameters
        ----------
        seed : int, optional
            RNG seed. Default is None.
        options : dict, optional
            Unused Gym options. Default is None.

        Returns
        -------
        tuple[np.ndarray, dict]
            Observation and info dict containing the action mask.
        """
        super().reset(seed=seed)
        self.world.reset(seed=seed)
        obs = self.world.build_observation()
        info = {"action_mask": self.world.get_action_mask()}
        return obs, info

    def step(self, action):
        """
        Step the environment one tick using the provided action.

        Parameters
        ----------
        action : np.ndarray
            MultiDiscrete action: one component per terminal dispatch choice
            plus one transfer choice.

        Returns
        -------
        tuple
            (obs, reward, terminated, truncated, info)
        """
        metrics = self.world.tick(action)
        obs = self.world.build_observation()
        reward = self.world.reward(metrics)
        terminated = False
        truncated = self.world.t >= self.config.horizon_ticks
        info = {**metrics, "action_mask": self.world.get_action_mask()}
        return obs, reward, terminated, truncated, info
