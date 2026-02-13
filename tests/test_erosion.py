"""Tests for deterministic WG-6 erosion/polish behavior."""

from __future__ import annotations

import unittest

from hexcrawl.world.world_config import WorldProfile, build_world_config
from hexcrawl.world.worldgen import WorldGen


class TestErosion(unittest.TestCase):
    def test_deterministic_eroded_height(self) -> None:
        world_gen = WorldGen(seed=1337, config=build_world_config(WorldProfile.DEV))

        coords = [(-18, 7), (0, 0), (26, -10), (15, 23)]
        first = [world_gen.get_tile(q, r).height for q, r in coords]
        second = [world_gen.get_tile(q, r).height for q, r in coords]

        self.assertEqual(first, second)

    def test_eroded_height_is_bounded(self) -> None:
        world_gen = WorldGen(seed=2025, config=build_world_config(WorldProfile.DEV))

        for q in range(-30, 31, 6):
            for r in range(-24, 25, 6):
                height = world_gen.get_tile(q, r).height
                self.assertGreaterEqual(height, 0.0)
                self.assertLessEqual(height, 1.0)

    def test_river_carving_effect_on_high_strength_tile(self) -> None:
        world_gen = WorldGen(seed=1337, config=build_world_config(WorldProfile.DEV))

        sample = None
        best_strength = -1
        for q in range(-80, 81, 4):
            for r in range(-60, 61, 4):
                strength = world_gen.get_river_strength(q, r)
                if strength > best_strength:
                    best_strength = strength
                    sample = (q, r)

        self.assertIsNotNone(sample, msg="No sampled river tile found")
        q, r = sample
        self.assertGreaterEqual(best_strength, 180, msg="No sufficiently strong river found in bounded search")

        canonical = world_gen.config.canonicalize(q, r)
        self.assertIsNotNone(canonical)
        cq, cr = canonical

        base_height = world_gen._base_height_at(cq, cr)
        eroded_height = world_gen.get_tile(cq, cr).height
        self.assertLessEqual(eroded_height, base_height)


if __name__ == "__main__":
    unittest.main()
