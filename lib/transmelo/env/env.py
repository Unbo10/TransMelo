from __future__ import annotations

from typing import Optional, Tuple

import gymnasium as gym
from gymnasium import spaces
import numpy as np

from .config import BRTConfig
from .world import ActionCandidate, DecisionEvent, World


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

        self.k_max = max(1, int(self.config.action_candidates_max)) #*max action candidates
        self._current_event: Optional[DecisionEvent] = None
        self._current_candidates: list[ActionCandidate] = []
        self._current_mask: np.ndarray = np.zeros(self.k_max, dtype=bool)

        obs_dim = self.world.observation_dim()
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(obs_dim,), dtype=np.float32
        ) #*all features normalized in [0,1] except time (in [-1,1])
        self.action_space = spaces.Discrete(self.k_max)

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
        self._current_event = None
        self._current_candidates = []
        self._current_mask = np.zeros(self.k_max, dtype=bool)
        _, truncated = self._prepare_event()
        obs = self.world.build_observation()
        info = self._info(truncated=truncated)
        return obs, info

    def step(self, action: int):
        """
        Step the environment one tick using the provided action.

        Parameters
        ----------
        action : int
            Discrete action index into the current candidate list.

        Returns
        -------
        tuple
            (obs, reward, terminated, truncated, info)
        """
        reward = 0.0
        terminated = False
        #*Make sure we have an event ready; advance time if needed
        time_reward, truncated = self._prepare_event()
        reward += time_reward
        if truncated and self._current_event is None:
            obs = self.world.build_observation()
            info = self._info(truncated=True)
            return obs, reward, terminated, True, info

        event = self._current_event
        candidates = self._current_candidates
        mask = self._current_mask

        if event is None:
            obs = self.world.build_observation()
            info = self._info(truncated=truncated)
            return obs, reward, terminated, truncated, info

        act_idx = int(action) if action is not None else 0
        invalid_action = act_idx < 0 or act_idx >= len(candidates) or not mask[act_idx]
        if invalid_action:
            metrics = self.world.blank_metrics()
            metrics["invalid_actions"] = 1
        else:
            metrics = self.world.apply_candidate(event, candidates[act_idx])
        reward += self.world.reward(metrics, include_queue=False)

        #*Consume the event and prepare the next one
        self._current_event = None
        self._current_candidates = []
        self._current_mask = np.zeros(self.k_max, dtype=bool)

        time_reward, truncated_time = self.world.advance_until_event()
        reward += time_reward
        truncated = truncated or truncated_time
        if not truncated:
            self._prepare_next_from_queue()

        obs = self.world.build_observation()
        truncated = truncated or (self.world.t >= self.config.horizon_ticks)
        info = {**metrics, **self._info(truncated=truncated)}
        return obs, reward, terminated, truncated, info

    def _prepare_next_from_queue(self) -> None:
        """
        Pull the next event from the queue and refresh candidates/mask.
        """
        event = self.world.pop_next_event()
        self._current_event = event
        if event is None:
            self._current_candidates = []
            self._current_mask = np.zeros(self.k_max, dtype=bool)
            return
        self._current_candidates = self.world.build_candidates(event)
        self._current_mask = self.world.candidate_mask(event)

    def _prepare_event(self) -> Tuple[float, bool]:
        """
        Ensure there is a pending event; advance simulation if needed.
        """
        if self._current_event is not None:
            return 0.0, False
        reward_accum, truncated = self.world.advance_until_event()
        if truncated and not self.world.event_queue:
            return reward_accum, True
        self._prepare_next_from_queue()
        return reward_accum, truncated

    def get_action_mask(self) -> np.ndarray:
        """
        Return the current action mask (shape = (k_max,)).
        """
        return self._current_mask.copy()

    def peek_event(self) -> Optional[dict]:
        """
        Return metadata for the current pending event.
        """
        if self._current_event is None:
            return None
        return self._event_info(self._current_event)

    def _event_info(self, event: Optional[DecisionEvent]) -> Optional[dict]:
        if event is None:
            return None
        return {
            "event_type": event.event_type,
            "t_tick": event.t_tick,
            "t_sec": event.t_sec,
            "terminal_id": event.terminal_id,
            "bus_id": event.bus_id,
        }

    def _candidate_info(self) -> list[dict]:
        info_list: list[dict] = []
        for idx, cand in enumerate(self._current_candidates):
            info_list.append(
                {
                    "idx": idx,
                    "type": cand.kind,
                    "route_id": cand.route_id,
                    "end_station_id": cand.end_station_id,
                    "end_idx": cand.end_idx,
                    "to_terminal_id": cand.to_terminal_id,
                    "travel_ticks": cand.travel_ticks,
                }
            )
        return info_list

    def _info(self, truncated: bool = False) -> dict:
        """
        Build the Gym info dict with mask, event, and candidates.
        """
        info = {
            "action_mask": self.get_action_mask(),
            "event": self._event_info(self._current_event),
            "candidates": self._candidate_info(),
            "t_tick": self.world.t,
            "t_sec": self.world.time_sec,
        }
        if truncated:
            info["truncated"] = True
        return info
