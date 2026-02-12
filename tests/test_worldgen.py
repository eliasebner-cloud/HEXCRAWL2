"""Tests for deterministic seed-based world generation."""

from __future__ import annotations

import unittest

from hexcrawl.core.hex_math import AXIAL_DIRECTIONS
from hexcrawl.world.world_config import WorldProfile, build_world_config
from hexcrawl.world.worldgen import TerrainType, WorldGen


class TestWorldGen(unittest.TestCase):
    def test_deterministic_outputs(self) -> None:
        world_gen = WorldGen(seed=1337, config=build_world_config(WorldProfile.DEV))

        coords = [(-12, 4), (0, 0), (19, -8), (7, 13)]
        first_pass = [world_gen.get_tile(q, r) for q, r in coords]
        second_pass = [world_gen.get_tile(q, r) for q, r in coords]

        self.assertEqual(first_pass, second_pass)

    def test_height_is_bounded(self) -> None:
        world_gen = WorldGen(seed=2025, config=build_world_config(WorldProfile.DEV))

        for q in range(-20, 21, 2):
            for r in range(-20, 21, 2):
                height = world_gen.get_tile(q, r).height
                self.assertGreaterEqual(height, 0.0)
                self.assertLessEqual(height, 1.0)

    def test_coast_has_ocean_neighbor(self) -> None:
        world_gen = WorldGen(seed=1337, config=build_world_config(WorldProfile.DEV))

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

    def test_wrap_x_returns_same_tile(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        world_gen = WorldGen(seed=1337, config=config)

        base_q, base_r = 17, 22
        wrapped_q = base_q + config.width
        self.assertEqual(world_gen.get_tile(base_q, base_r), world_gen.get_tile(wrapped_q, base_r))

    def test_worldgen_cache_uses_canonical_wrap_x_key(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        world_gen = WorldGen(seed=1337, config=config)

        base_q, base_r = 15, 9
        wrapped_q = base_q + config.width

        world_gen.get_tile(base_q, base_r)
        cache_size_after_first = len(world_gen._tile_cache)
        world_gen.get_tile(wrapped_q, base_r)

        self.assertEqual(len(world_gen._tile_cache), cache_size_after_first)


    def test_lattice_noise_does_not_wrap_y_when_wrap_y_disabled(self) -> None:
        world_gen = WorldGen(seed=1337, config=build_world_config(WorldProfile.DEV))

        freq = 4
        ix = 7
        iy = 1
        y_offset = freq

        base = world_gen._lattice_noise(ix, iy, x_period=freq, y_period=None)
        shifted = world_gen._lattice_noise(ix, iy + y_offset, x_period=freq, y_period=None)

        self.assertNotEqual(base, shifted)

    def test_height_neighbor_correlation(self) -> None:
        world_gen = WorldGen(seed=1337, config=build_world_config(WorldProfile.DEV))

        near_diffs: list[float] = []
        far_diffs: list[float] = []

        for q in range(-80, 81, 8):
            for r in range(-60, 61, 8):
                here = world_gen.get_tile(q, r).height
                near = world_gen.get_tile(q + 1, r).height
                far = world_gen.get_tile(q + 64, r + 32).height
                near_diffs.append(abs(here - near))
                far_diffs.append(abs(here - far))

        mean_near = sum(near_diffs) / len(near_diffs)
        mean_far = sum(far_diffs) / len(far_diffs)

        self.assertLess(mean_near, mean_far)

    def test_out_of_bounds_r_defaults_to_ocean(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        world_gen = WorldGen(seed=1337, config=config)

        self.assertEqual(world_gen.get_tile(0, config.r_max + 1).terrain_type, TerrainType.OCEAN)
        self.assertEqual(world_gen.get_tile(0, config.r_min - 1).terrain_type, TerrainType.OCEAN)


if __name__ == "__main__":
    unittest.main()
