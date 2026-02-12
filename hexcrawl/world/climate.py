"""Deterministic climate and biome helpers for world hexes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib

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

    def __init__(self, seed: int) -> None:
        self.seed = int(seed)

    def get_tile(self, q: int, r: int, terrain_type: TerrainType, height: float) -> ClimateTile:
        """Return deterministic heat/moisture and biome for one hex."""
        heat = self._heat_at(q, r)
        moisture = self._moisture_at(q, r)

        if terrain_type == TerrainType.COAST:
            moisture = min(1.0, moisture + 0.16)

        biome_type = self._biome_for(terrain_type, height, heat, moisture)
        return ClimateTile(heat=heat, moisture=moisture, biome_type=biome_type)

    def _heat_at(self, q: int, r: int) -> float:
        # Soft latitudinal cooling plus local noise variation.
        latitude = min(1.0, abs(r) / 48.0)
        latitude_heat = 1.0 - latitude
        noise = self._noise01("heat", q, r)
        return self._clamp01((latitude_heat * 0.7) + (noise * 0.3))

    def _moisture_at(self, q: int, r: int) -> float:
        return self._noise01("moisture", q, r)

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
