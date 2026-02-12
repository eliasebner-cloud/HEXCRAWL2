"""Deterministic seed-based world generation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib

from hexcrawl.core.hex_math import AXIAL_DIRECTIONS


class TerrainType(str, Enum):
    """Supported terrain classes for world-map coloring."""

    OCEAN = "OCEAN"
    COAST = "COAST"
    PLAINS = "PLAINS"
    HILLS = "HILLS"
    MOUNTAINS = "MOUNTAINS"
    SNOW = "SNOW"


@dataclass(frozen=True)
class WorldTile:
    """Generated world tile data for a single axial coordinate."""

    height: float
    terrain_type: TerrainType


class WorldGen:
    """Simple deterministic worldgen based on per-hex hashed noise."""

    OCEAN_THRESHOLD = 0.36
    PLAINS_THRESHOLD = 0.55
    HILLS_THRESHOLD = 0.72
    MOUNTAINS_THRESHOLD = 0.88

    def __init__(self, seed: int) -> None:
        self.seed = int(seed)

    def get_tile(self, q: int, r: int) -> WorldTile:
        """Return deterministic tile data for axial hex coordinates."""
        height = self._height_at(q, r)

        if self._is_ocean_height(height):
            terrain = TerrainType.OCEAN
        elif self._has_ocean_neighbor(q, r):
            terrain = TerrainType.COAST
        elif height < self.PLAINS_THRESHOLD:
            terrain = TerrainType.PLAINS
        elif height < self.HILLS_THRESHOLD:
            terrain = TerrainType.HILLS
        elif height < self.MOUNTAINS_THRESHOLD:
            terrain = TerrainType.MOUNTAINS
        else:
            terrain = TerrainType.SNOW

        return WorldTile(height=height, terrain_type=terrain)

    def _height_at(self, q: int, r: int) -> float:
        raw = self._noise_u64(q, r)
        return raw / float((1 << 64) - 1)

    def _noise_u64(self, q: int, r: int) -> int:
        msg = f"{self.seed}:{q}:{r}".encode("utf-8")
        digest = hashlib.blake2b(msg, digest_size=8).digest()
        return int.from_bytes(digest, byteorder="big", signed=False)

    def _is_ocean_height(self, height: float) -> bool:
        return height < self.OCEAN_THRESHOLD

    def _has_ocean_neighbor(self, q: int, r: int) -> bool:
        for dq, dr in AXIAL_DIRECTIONS:
            neighbor_height = self._height_at(q + dq, r + dr)
            if self._is_ocean_height(neighbor_height):
                return True
        return False
