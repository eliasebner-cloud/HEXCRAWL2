"""Deterministic climate and biome helpers for world hexes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
from collections import OrderedDict

from hexcrawl.world.world_config import WorldConfig, default_world_config
from hexcrawl.world.worldgen import TerrainType


class BiomeType(str, Enum):
    """Biome classes used for climate debug/rendering."""

    OCEAN = "OCEAN"
    COASTAL = "COASTAL"
    DESERT = "DESERT"
    SAVANNA = "SAVANNA"
    GRASSLAND = "GRASSLAND"
    TEMPERATE_FOREST = "TEMPERATE_FOREST"
    TAIGA = "TAIGA"
    TUNDRA = "TUNDRA"
    ALPINE = "ALPINE"


@dataclass(frozen=True)
class ClimateTile:
    """Climate data derived for a single axial coordinate."""

    heat: float
    moisture: float
    biome_type: BiomeType


class ClimateGen:
    """Seeded deterministic climate mapping from axial hex to biome."""

    def __init__(self, seed: int, config: WorldConfig | None = None) -> None:
        self.seed = int(seed)
        self.config = default_world_config() if config is None else config
        self._cache_maxsize = self._resolve_cache_maxsize()
        self._climate_cache: OrderedDict[tuple[int, int], tuple[TerrainType, float, ClimateTile]] = OrderedDict()

    def get_tile(self, q: int, r: int, terrain_type: TerrainType, height: float) -> ClimateTile:
        """Return deterministic heat/moisture and biome for one hex."""
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return ClimateTile(heat=0.0, moisture=0.0, biome_type=BiomeType.OCEAN)

        cq, cr = canonical
        cached_entry = self._climate_cache.get((cq, cr))
        if cached_entry is not None:
            cached_terrain, cached_height, cached_tile = cached_entry
            if cached_terrain == terrain_type and cached_height == height:
                self._climate_cache.move_to_end((cq, cr))
                return cached_tile

        heat = self._heat_at(cq, cr, height)
        moisture = self._moisture_at(cq, cr, terrain_type, height)

        if terrain_type == TerrainType.COAST:
            moisture = min(1.0, moisture + 0.16)

        biome_type = self._biome_for(terrain_type, height, heat, moisture)
        tile = ClimateTile(heat=heat, moisture=moisture, biome_type=biome_type)
        self._climate_cache[(cq, cr)] = (terrain_type, height, tile)
        self._climate_cache.move_to_end((cq, cr))
        while len(self._climate_cache) > self._cache_maxsize:
            self._climate_cache.popitem(last=False)
        return tile

    def _resolve_cache_maxsize(self) -> int:
        if self.config.profile.value == "DEV":
            return self.config.width * self.config.height
        return 200_000

    def _latitude_factor(self, r: int) -> float:
        center_r = (self.config.r_min + self.config.r_max) / 2.0
        max_dist = max(1.0, (self.config.height - 1) / 2.0)
        return self._clamp01(abs(r - center_r) / max_dist)

    def _heat_at(self, q: int, r: int, height: float) -> float:
        # Broad latitudinal pattern with moderate local variation.
        latitude = self._latitude_factor(r)
        latitude_heat = 1.0 - latitude
        macro_noise = self._noise01("heat_macro", q // 4, r // 4)
        local_noise = self._noise01("heat_local", q, r)
        altitude_cooling = self._clamp01(height) * 0.48
        heat = (latitude_heat * 0.66) + (macro_noise * 0.22) + (local_noise * 0.12)
        return self._clamp01(heat - altitude_cooling)

    def _moisture_at(self, q: int, r: int, terrain_type: TerrainType, height: float) -> float:
        latitude = self._latitude_factor(r)
        equatorial_band = 1.0 - abs(0.45 - latitude) / 0.45
        macro_noise = self._noise01("moisture_macro", q // 5, r // 5)
        local_noise = self._noise01("moisture_local", q, r)
        moisture = (self._clamp01(equatorial_band) * 0.42) + (macro_noise * 0.35) + (local_noise * 0.23)

        if terrain_type == TerrainType.COAST:
            moisture += 0.16

        moisture += self._terrain_orographic_bonus(terrain_type)

        # Prevailing wind from west to east: upwind uplift, leeward rainshadow.
        west_barrier = self._orographic_barrier(q - 1, r)
        east_barrier = self._orographic_barrier(q + 1, r)
        moisture += west_barrier * 0.09
        moisture -= east_barrier * 0.1

        if height > 0.88:
            moisture -= 0.04

        return self._clamp01(moisture)

    @staticmethod
    def _terrain_orographic_bonus(terrain_type: TerrainType) -> float:
        if terrain_type == TerrainType.HILLS:
            return 0.08
        if terrain_type in (TerrainType.MOUNTAINS, TerrainType.SNOW):
            return 0.16
        return 0.0

    def _orographic_barrier(self, q: int, r: int) -> float:
        ridge_noise = self._noise01("ridge", q, r)
        return self._clamp01((ridge_noise - 0.58) / 0.42)

    def _biome_for(
        self,
        terrain_type: TerrainType,
        height: float,
        heat: float,
        moisture: float,
    ) -> BiomeType:
        if terrain_type == TerrainType.OCEAN:
            return BiomeType.OCEAN
        if terrain_type == TerrainType.COAST:
            return BiomeType.COASTAL
        if terrain_type in (TerrainType.MOUNTAINS, TerrainType.SNOW) and (height > 0.9 or heat < 0.25):
            return BiomeType.ALPINE
        if heat < 0.22:
            return BiomeType.TUNDRA
        if heat < 0.38:
            return BiomeType.TAIGA if moisture >= 0.45 else BiomeType.TUNDRA
        if heat > 0.74 and moisture < 0.28:
            return BiomeType.DESERT
        if heat > 0.62 and moisture < 0.5:
            return BiomeType.SAVANNA
        if moisture > 0.62:
            return BiomeType.TEMPERATE_FOREST
        return BiomeType.GRASSLAND

    def _noise01(self, channel: str, q: int, r: int) -> float:
        msg = f"{self.seed}:{channel}:{q}:{r}".encode("utf-8")
        digest = hashlib.blake2b(msg, digest_size=8).digest()
        raw = int.from_bytes(digest, byteorder="big", signed=False)
        return raw / float((1 << 64) - 1)

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))
