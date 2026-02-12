"""Tests for deterministic seed-based world generation."""

from __future__ import annotations

import unittest

from hexcrawl.core.hex_math import AXIAL_DIRECTIONS
from hexcrawl.world.worldgen import TerrainType, WorldGen


class TestWorldGen(unittest.TestCase):
    def test_deterministic_outputs(self) -> None:
        world_gen = WorldGen(seed=1337)

        coords = [(-12, 4), (0, 0), (19, -8), (7, 13)]
        first_pass = [world_gen.get_tile(q, r) for q, r in coords]
        second_pass = [world_gen.get_tile(q, r) for q, r in coords]

        self.assertEqual(first_pass, second_pass)

    def test_height_is_bounded(self) -> None:
        world_gen = WorldGen(seed=2025)

        for q in range(-20, 21, 2):
            for r in range(-20, 21, 2):
                height = world_gen.get_tile(q, r).height
                self.assertGreaterEqual(height, 0.0)
                self.assertLessEqual(height, 1.0)

    def test_coast_has_ocean_neighbor(self) -> None:
        world_gen = WorldGen(seed=1337)

        for q in range(-30, 31):
            for r in range(-30, 31):
                tile = world_gen.get_tile(q, r)
                if tile.terrain_type != TerrainType.COAST:
                    continue

                has_ocean_neighbor = any(
                    world_gen.get_tile(q + dq, r + dr).terrain_type == TerrainType.OCEAN
                    for dq, dr in AXIAL_DIRECTIONS
                )
                self.assertTrue(has_ocean_neighbor, msg=f"COAST without OCEAN neighbor at {(q, r)}")


if __name__ == "__main__":
    unittest.main()
