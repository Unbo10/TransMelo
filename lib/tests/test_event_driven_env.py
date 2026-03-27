from __future__ import annotations

import sys
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from transmelo.env import BRTConfig, BRTEnv  # noqa: E402


class EventDrivenEnvTests(unittest.TestCase):
    def test_smoke_runs_many_decisions(self):
        env = BRTEnv(BRTConfig.default())
        obs, info = env.reset()
        expected_shape = obs.shape
        prev_t = env.world.t

        for _ in range(500):
            mask = info["action_mask"]
            self.assertEqual(mask.shape, (env.config.action_candidates_max,))
            self.assertEqual(mask.dtype, np.bool_)
            self.assertEqual(obs.shape, expected_shape)
            self.assertTrue(np.all(np.isfinite(obs)))

            action = int(np.argmax(mask)) if mask.any() else 0
            obs, reward, terminated, truncated, info = env.step(action)
            self.assertFalse(terminated)
            self.assertFalse(truncated)
            self.assertGreaterEqual(env.world.t, prev_t)
            prev_t = env.world.t
            self.assertTrue(np.all(np.isfinite(obs)))

            for bus in env.world.buses:
                self.assertGreaterEqual(bus.pax, 0)
                self.assertLessEqual(bus.pax, bus.capacity)
            for station in env.world.stations.values():
                self.assertTrue(np.all(station.queues >= 0))

    def test_events_at_same_time_do_not_advance_clock(self):
        env = BRTEnv(BRTConfig.default())
        obs, info = env.reset()
        base_t = info["event"]["t_tick"] if info.get("event") else env.world.t
        times = []

        for _ in range(3):
            mask = info["action_mask"]
            action = 0  # HOLD
            obs, reward, terminated, truncated, info = env.step(action)
            self.assertFalse(terminated)
            self.assertFalse(truncated)
            times.append(info["event"]["t_tick"] if info.get("event") else env.world.t)
            self.assertEqual(info["action_mask"].shape, (env.config.action_candidates_max,))

        self.assertTrue(all(t == base_t for t in times))


if __name__ == "__main__":
    unittest.main()
