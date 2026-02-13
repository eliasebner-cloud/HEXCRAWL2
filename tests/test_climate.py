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

            def _ocean_fetch_bonus(self, q: int, r: int, wind_dir: int) -> float:
                return 0.0

            def _scan_barrier_strength(self, q: int, r: int, direction: int) -> float:
                if direction > 0:
                    return 1.0
                return 0.0

        class WetStubClimateGen(StubClimateGen):
            def _scan_barrier_strength(self, q: int, r: int, direction: int) -> float:
                if direction < 0:
                    return 1.0
                return 0.0

        config = build_world_config(WorldProfile.DEV)
        mid_lat_r = int((config.r_min + config.r_max) / 2) + int(config.height * 0.22)

        dry_leeward = StubClimateGen(seed=1, config=config).get_tile(
            8, mid_lat_r, TerrainType.PLAINS, 0.4
        ).moisture
        wetter_windward = WetStubClimateGen(seed=1, config=config).get_tile(
            8, mid_lat_r, TerrainType.PLAINS, 0.4
        ).moisture
        self.assertLess(dry_leeward, wetter_windward)

    def test_orographic_and_coastal_moisture_bias(self) -> None:
        climate_gen = ClimateGen(seed=909, config=build_world_config(WorldProfile.DEV))

        coast = climate_gen.get_tile(3, -4, TerrainType.COAST, 0.3).moisture
        inland = climate_gen.get_tile(3, -4, TerrainType.PLAINS, 0.3).moisture
        mountain = climate_gen.get_tile(8, 5, TerrainType.MOUNTAINS, 0.92).moisture
        plains = climate_gen.get_tile(8, 5, TerrainType.PLAINS, 0.4).moisture

        self.assertGreaterEqual(coast, inland)
        self.assertGreaterEqual(mountain, plains)

    def test_climate_cache_uses_canonical_wrap_x_key(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        climate_gen = ClimateGen(seed=909, config=config)

        base_q, base_r = 21, -11
        wrapped_q = base_q + config.width

        climate_gen.get_tile(base_q, base_r, TerrainType.PLAINS, 0.45)
        cache_size_after_first = len(climate_gen._climate_cache)
        climate_gen.get_tile(wrapped_q, base_r, TerrainType.PLAINS, 0.45)

        self.assertEqual(len(climate_gen._climate_cache), cache_size_after_first)

    def test_wrap_x_is_deterministic_for_climate(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        climate_gen = ClimateGen(seed=909, config=config)

        first = climate_gen.get_tile(10, 4, TerrainType.PLAINS, 0.4)
        wrapped = climate_gen.get_tile(10 + config.width, 4, TerrainType.PLAINS, 0.4)
        self.assertEqual(first, wrapped)

    def test_wind_bands_follow_expected_zonal_directions(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        climate_gen = ClimateGen(seed=909, config=config)

        equator_r = int((config.r_min + config.r_max) / 2)
        tropical_r = equator_r
        mid_lat_r = equator_r + int(config.height * 0.22)
        polar_r = config.r_max

        self.assertEqual(climate_gen.wind_band_label(tropical_r), "E->W")
        self.assertEqual(climate_gen.wind_band_label(mid_lat_r), "W->E")
        self.assertEqual(climate_gen.wind_band_label(polar_r), "E->W")

    def test_ocean_fetch_wrap_and_downwind_moisture_bias(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        climate_gen = ClimateGen(seed=909, config=config)

        found_pair: tuple[int, int, int] | None = None
        equator_r = int((config.r_min + config.r_max) / 2)
        search_r_values = [equator_r + offset for offset in (0, 6, -6, 12, -12)]

        for r in search_r_values:
            if not config.is_r_in_bounds(r):
                continue
            wind_dir = climate_gen._wind_dir(r)
            for q in range(config.q_min, config.q_min + 96):
                if not climate_gen._is_ocean_source_tile(q, r):
                    continue
                near = config.canonicalize(q + wind_dir, r)
                inland = config.canonicalize(q + (wind_dir * 8), r)
                if near is None or inland is None:
                    continue
                found_pair = (near[0], inland[0], r)
                break
            if found_pair is not None:
                break

        self.assertIsNotNone(found_pair, "Expected to find at least one ocean-fetch sample pair")
        assert found_pair is not None
        near_q, inland_q, r = found_pair

        near_tile = climate_gen.get_tile(near_q, r, TerrainType.PLAINS, 0.35)
        wrapped_near_tile = climate_gen.get_tile(near_q + config.width, r, TerrainType.PLAINS, 0.35)
        inland_tile = climate_gen.get_tile(inland_q, r, TerrainType.PLAINS, 0.35)

        self.assertEqual(near_tile, wrapped_near_tile)
        self.assertGreaterEqual(near_tile.moisture, inland_tile.moisture)


if __name__ == "__main__":
    unittest.main()
