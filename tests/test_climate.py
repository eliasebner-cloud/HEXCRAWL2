"""Tests for deterministic climate and biome generation."""

from __future__ import annotations

import unittest

from hexcrawl.world.climate import BiomeType, ClimateGen
from hexcrawl.world.worldgen import TerrainType


class TestClimateGen(unittest.TestCase):
    def test_deterministic_outputs(self) -> None:
        climate_gen = ClimateGen(seed=9001)

        coords = [(-12, 4), (0, 0), (19, -8), (7, 13)]
        first_pass = [
            climate_gen.get_tile(q, r, TerrainType.PLAINS, 0.5)
            for q, r in coords
        ]
        second_pass = [
            climate_gen.get_tile(q, r, TerrainType.PLAINS, 0.5)
            for q, r in coords
        ]

        self.assertEqual(first_pass, second_pass)

    def test_heat_and_moisture_are_bounded(self) -> None:
        climate_gen = ClimateGen(seed=1338)

        terrain_cycle = [
            TerrainType.PLAINS,
            TerrainType.HILLS,
            TerrainType.MOUNTAINS,
            TerrainType.COAST,
            TerrainType.SNOW,
        ]
        for q in range(-20, 21, 2):
            for r in range(-20, 21, 2):
                terrain = terrain_cycle[(q + r) % len(terrain_cycle)]
                tile = climate_gen.get_tile(q, r, terrain, 0.5)
                self.assertGreaterEqual(tile.heat, 0.0)
                self.assertLessEqual(tile.heat, 1.0)
                self.assertGreaterEqual(tile.moisture, 0.0)
                self.assertLessEqual(tile.moisture, 1.0)

    def test_ocean_tiles_are_ocean_biome(self) -> None:
        climate_gen = ClimateGen(seed=42)

        for q in range(-30, 31, 3):
            for r in range(-30, 31, 3):
                tile = climate_gen.get_tile(q, r, TerrainType.OCEAN, 0.1)
                self.assertEqual(tile.biome_type, BiomeType.OCEAN)


if __name__ == "__main__":
    unittest.main()
