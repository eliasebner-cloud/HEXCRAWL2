"""Tests for deterministic climate and biome generation."""

from __future__ import annotations

import unittest

from hexcrawl.world.climate import BiomeType, ClimateGen
from hexcrawl.world.world_config import WorldProfile, build_world_config
from hexcrawl.world.worldgen import TerrainType


class TestClimateGen(unittest.TestCase):
    def test_deterministic_outputs(self) -> None:
        climate_gen = ClimateGen(seed=9001, config=build_world_config(WorldProfile.DEV))

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
        climate_gen = ClimateGen(seed=1338, config=build_world_config(WorldProfile.DEV))

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
        climate_gen = ClimateGen(seed=42, config=build_world_config(WorldProfile.DEV))

        for q in range(-30, 31, 3):
            for r in range(-30, 31, 3):
                tile = climate_gen.get_tile(q, r, TerrainType.OCEAN, 0.1)
                self.assertEqual(tile.biome_type, BiomeType.OCEAN)

    def test_higher_altitude_is_cooler_on_average(self) -> None:
        climate_gen = ClimateGen(seed=77, config=build_world_config(WorldProfile.DEV))

        low_samples = []
        high_samples = []
        for q in range(-24, 25, 2):
            for r in range(-24, 25, 2):
                low_samples.append(climate_gen.get_tile(q, r, TerrainType.PLAINS, 0.15).heat)
                high_samples.append(climate_gen.get_tile(q, r, TerrainType.PLAINS, 0.92).heat)

        low_avg = sum(low_samples) / len(low_samples)
        high_avg = sum(high_samples) / len(high_samples)
        self.assertLess(high_avg, low_avg)

    def test_rainshadow_can_reduce_moisture_deterministically(self) -> None:
        class StubClimateGen(ClimateGen):
            def _noise01(self, channel: str, q: int, r: int) -> float:
                return 0.5

            def _orographic_barrier(self, q: int, r: int) -> float:
                if q == 9:
                    return 1.0
                if q == 7:
                    return 0.0
                return 0.0

        climate_gen = StubClimateGen(seed=1, config=build_world_config(WorldProfile.DEV))

        dry_leeward = climate_gen.get_tile(8, 0, TerrainType.PLAINS, 0.4).moisture

        class WetStubClimateGen(StubClimateGen):
            def _orographic_barrier(self, q: int, r: int) -> float:
                if q == 7:
                    return 1.0
                if q == 9:
                    return 0.0
                return 0.0

        wetter_windward = WetStubClimateGen(seed=1, config=build_world_config(WorldProfile.DEV)).get_tile(8, 0, TerrainType.PLAINS, 0.4).moisture
        self.assertLess(dry_leeward, wetter_windward)

    def test_orographic_and_coastal_moisture_bias(self) -> None:
        climate_gen = ClimateGen(seed=909, config=build_world_config(WorldProfile.DEV))

        coast = climate_gen.get_tile(3, -4, TerrainType.COAST, 0.3).moisture
        inland = climate_gen.get_tile(3, -4, TerrainType.PLAINS, 0.3).moisture
        mountain = climate_gen.get_tile(8, 5, TerrainType.MOUNTAINS, 0.92).moisture
        plains = climate_gen.get_tile(8, 5, TerrainType.PLAINS, 0.4).moisture

        self.assertGreaterEqual(coast, inland)
        self.assertGreaterEqual(mountain, plains)

    def test_wrap_x_is_deterministic_for_climate(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        climate_gen = ClimateGen(seed=909, config=config)

        first = climate_gen.get_tile(10, 4, TerrainType.PLAINS, 0.4)
        wrapped = climate_gen.get_tile(10 + config.width, 4, TerrainType.PLAINS, 0.4)
        self.assertEqual(first, wrapped)


if __name__ == "__main__":
    unittest.main()
