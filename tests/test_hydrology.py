"""Tests for deterministic hydrology model."""

from __future__ import annotations

import unittest

from hexcrawl.world.hydrology import HydrologyModel
from hexcrawl.world.world_config import WorldConfig, WorldProfile


class TestHydrology(unittest.TestCase):
    def _build_config(self) -> WorldConfig:
        return WorldConfig(profile=WorldProfile.DEV, width=8, height=6)

    def test_flow_and_accumulation_on_sloped_plane(self) -> None:
        config = self._build_config()

        def height_fn(q: int, r: int) -> float:
            return float(q + config.width)

        model = HydrologyModel(
            seed=5,
            config=config,
            height_fn=height_fn,
            is_ocean_fn=lambda q, r: False,
        )

        up_q = 1
        mid_q = 0
        r = 0

        self.assertEqual(model.flow_to(up_q, r), (mid_q, r))
        self.assertGreater(model.accumulation(mid_q, r), model.accumulation(up_q, r))

    def test_ocean_has_no_rivers(self) -> None:
        config = self._build_config()

        model = HydrologyModel(
            seed=5,
            config=config,
            height_fn=lambda q, r: float(q + r + 100),
            is_ocean_fn=lambda q, r: r == config.r_min,
        )

        q = 0
        ocean_r = config.r_min
        self.assertIsNone(model.flow_to(q, ocean_r))
        self.assertEqual(model.river_strength(q, ocean_r), 0)


    def test_target_guard_skips_global_build_without_crash(self) -> None:
        config = WorldConfig(profile=WorldProfile.TARGET, width=8, height=6)

        model = HydrologyModel(
            seed=11,
            config=config,
            height_fn=lambda q, r: float(q + r + 100),
            is_ocean_fn=lambda q, r: False,
        )
        model._cache_maxsize = 10
        model._supports_global_build = False

        self.assertIsNone(model.flow_to(0, 0))
        self.assertEqual(model.accumulation(0, 0), 0)
        self.assertEqual(model.river_strength(0, 0), 0)
        self.assertFalse(model.is_lake(0, 0))
        self.assertTrue(model._built)

    def test_wrap_x_invariance(self) -> None:
        config = self._build_config()

        model = HydrologyModel(
            seed=7,
            config=config,
            height_fn=lambda q, r: float((q - config.q_min) + (r - config.r_min)),
            is_ocean_fn=lambda q, r: False,
        )

        q, r = 1, 0
        self.assertEqual(model.flow_to(q, r), model.flow_to(q + config.width, r))
        self.assertEqual(model.accumulation(q, r), model.accumulation(q + config.width, r))
        self.assertEqual(model.river_strength(q, r), model.river_strength(q + config.width, r))
        self.assertEqual(model.is_lake(q, r), model.is_lake(q + config.width, r))


if __name__ == "__main__":
    unittest.main()
