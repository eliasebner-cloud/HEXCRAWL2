"""Deterministic seed-based world generation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import math

from hexcrawl.core.hex_math import AXIAL_DIRECTIONS
from hexcrawl.world.world_config import WorldConfig, default_world_config


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
    """Deterministic worldgen with correlated macro-scale height fields."""

    OCEAN_THRESHOLD = 0.36
    PLAINS_THRESHOLD = 0.55
    HILLS_THRESHOLD = 0.72
    MOUNTAINS_THRESHOLD = 0.88

    def __init__(self, seed: int, config: WorldConfig | None = None) -> None:
        self.seed = int(seed)
        self.config = default_world_config() if config is None else config

    def get_tile(self, q: int, r: int) -> WorldTile:
        """Return deterministic tile data for axial hex coordinates."""
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return WorldTile(height=0.0, terrain_type=TerrainType.OCEAN)

        cq, cr = canonical
        height = self._height_at(cq, cr)

        if self._is_ocean_height(height):
            terrain = TerrainType.OCEAN
        elif self._has_ocean_neighbor(cq, cr):
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
        x, y = self._normalized_world_pos(q, r)
        height = self._fbm_height(x, y)
        return max(0.0, min(1.0, height))

    def _normalized_world_pos(self, q: int, r: int) -> tuple[float, float]:
        """Map canonical axial coordinates into normalized [0,1) world space."""
        x = (q - self.config.q_min) / self.config.width
        y = (r - self.config.r_min) / self.config.height
        return x, y

    def _fbm_height(self, x: float, y: float) -> float:
        """Fractal value noise for large connected continents and ocean basins."""
        frequencies = (2, 4, 8, 16)
        amplitudes = (0.60, 0.25, 0.10, 0.05)
        total = 0.0

        for freq, amplitude in zip(frequencies, amplitudes):
            total += amplitude * self._value_noise(x, y, freq)

        continent_mask = self._value_noise(x, y, 2)
        total = (total * 0.70) + (continent_mask * 0.30)

        radial = math.sin((y - 0.5) * math.pi)
        total -= 0.08 * abs(radial)

        return total

    def _value_noise(self, x: float, y: float, freq: int) -> float:
        """Continuous value noise with explicit x-periodicity for wrap seams."""
        sx = x * freq
        sy = y * freq

        ix0 = math.floor(sx)
        iy0 = math.floor(sy)
        fx = sx - ix0
        fy = sy - iy0

        ix1 = ix0 + 1
        iy1 = iy0 + 1

        x_period = freq
        y_period = freq

        n00 = self._lattice_noise(ix0, iy0, x_period, y_period)
        n10 = self._lattice_noise(ix1, iy0, x_period, y_period)
        n01 = self._lattice_noise(ix0, iy1, x_period, y_period)
        n11 = self._lattice_noise(ix1, iy1, x_period, y_period)

        ux = self._smoothstep(fx)
        uy = self._smoothstep(fy)

        nx0 = self._lerp(n00, n10, ux)
        nx1 = self._lerp(n01, n11, ux)
        return self._lerp(nx0, nx1, uy)

    def _lattice_noise(self, ix: int, iy: int, x_period: int, y_period: int) -> float:
        wrapped_x = ix % x_period
        wrapped_y = iy % y_period
        raw = self._noise_u64(wrapped_x, wrapped_y)
        return raw / float((1 << 64) - 1)

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    @staticmethod
    def _smoothstep(t: float) -> float:
        return t * t * (3.0 - 2.0 * t)

    def _noise_u64(self, q: int, r: int) -> int:
        msg = f"{self.seed}:{q}:{r}".encode("utf-8")
        digest = hashlib.blake2b(msg, digest_size=8).digest()
        return int.from_bytes(digest, byteorder="big", signed=False)

    def _is_ocean_height(self, height: float) -> bool:
        return height < self.OCEAN_THRESHOLD

    def _has_ocean_neighbor(self, q: int, r: int) -> bool:
        for dq, dr in AXIAL_DIRECTIONS:
            neighbor = self.config.canonicalize(q + dq, r + dr)
            if neighbor is None:
                return True
            neighbor_height = self._height_at(*neighbor)
            if self._is_ocean_height(neighbor_height):
                return True
        return False
