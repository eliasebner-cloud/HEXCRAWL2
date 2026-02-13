"""Deterministic seed-based world generation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import math
from collections import OrderedDict

from hexcrawl.core.hex_math import AXIAL_DIRECTIONS
from hexcrawl.world.hydrology import HydrologyModel
from hexcrawl.world.tectonics import BoundaryData, BoundaryKind, PlateData, PlateType, TectonicsModel
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
    BOUNDARY_FALLOFF_RADIUS = 3

    def __init__(self, seed: int, config: WorldConfig | None = None) -> None:
        self.seed = int(seed)
        self.config = default_world_config() if config is None else config
        self._height_cache_maxsize = self._resolve_cache_maxsize()
        self._tile_cache_maxsize = self._resolve_cache_maxsize()
        self._raw_height_cache_maxsize = self._resolve_cache_maxsize()
        self._boundary_influence_cache_maxsize = self._resolve_cache_maxsize()
        self._raw_height_cache: OrderedDict[tuple[int, int], float] = OrderedDict()
        self._boundary_influence_cache: OrderedDict[tuple[int, int], float] = OrderedDict()
        self._height_cache: OrderedDict[tuple[int, int], float] = OrderedDict()
        self._tile_cache: OrderedDict[tuple[int, int], WorldTile] = OrderedDict()
        self._tectonics = TectonicsModel(seed=self.seed, config=self.config)
        self._hydrology = HydrologyModel(
            seed=self.seed + 3,
            config=self.config,
            height_fn=self._height_at,
            is_ocean_fn=lambda q, r: self._is_ocean_height(self._height_at(q, r)),
        )

    def get_tile(self, q: int, r: int) -> WorldTile:
        """Return deterministic tile data for axial hex coordinates."""
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return WorldTile(height=0.0, terrain_type=TerrainType.OCEAN)

        cq, cr = canonical
        cached_tile = self._cache_get(self._tile_cache, canonical)
        if cached_tile is not None:
            return cached_tile

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

        tile = WorldTile(height=height, terrain_type=terrain)
        self._cache_set(self._tile_cache, canonical, tile, self._tile_cache_maxsize)
        return tile

    def _height_at(self, q: int, r: int) -> float:
        cached_height = self._cache_get(self._height_cache, (q, r))
        if cached_height is not None:
            return cached_height

        smoothed_height = self._smoothed_height_at(q, r)

        clamped = max(0.0, min(1.0, smoothed_height))
        self._cache_set(self._height_cache, (q, r), clamped, self._height_cache_maxsize)
        return clamped

    def _raw_height_at(self, q: int, r: int) -> float:
        cached_height = self._cache_get(self._raw_height_cache, (q, r))
        if cached_height is not None:
            return cached_height

        x, y = self._normalized_world_pos(q, r)
        base_height = self._fbm_height(x, y)

        plate = self._tectonics.plate_at(q, r)

        plate_bias = 0.0
        if plate is not None:
            if plate.plate_type == PlateType.CONTINENTAL:
                plate_bias = 0.09
            else:
                plate_bias = -0.09

        boundary_bias = self._boundary_falloff_influence_at(q, r)

        height = base_height + plate_bias + boundary_bias
        clamped = max(0.0, min(1.0, height))
        self._cache_set(self._raw_height_cache, (q, r), clamped, self._raw_height_cache_maxsize)
        return clamped

    def _smoothed_height_at(self, q: int, r: int) -> float:
        center = self._raw_height_at(q, r)
        total = center * 0.60
        total_weight = 0.60

        for dq, dr in AXIAL_DIRECTIONS:
            neighbor = self.config.canonicalize(q + dq, r + dr)
            if neighbor is None:
                continue
            total += self._raw_height_at(*neighbor) * 0.40 / len(AXIAL_DIRECTIONS)
            total_weight += 0.40 / len(AXIAL_DIRECTIONS)

        if total_weight == 0.0:
            return center
        return total / total_weight

    def _boundary_falloff_influence_at(self, q: int, r: int) -> float:
        cached = self._cache_get(self._boundary_influence_cache, (q, r))
        if cached is not None:
            return cached

        radius = self.BOUNDARY_FALLOFF_RADIUS
        weighted_sum = 0.0
        total_weight = 0.0

        for dq in range(-radius, radius + 1):
            for dr in range(-radius, radius + 1):
                ds = -dq - dr
                distance = max(abs(dq), abs(dr), abs(ds))
                if distance > radius:
                    continue

                sample = self.config.canonicalize(q + dq, r + dr)
                if sample is None:
                    continue

                weight = (radius + 1 - distance) / (radius + 1)
                if weight <= 0.0:
                    continue

                sample_plate = self._tectonics.plate_at(*sample)
                sample_boundary = self._tectonics.boundary_at(*sample)
                weighted_sum += self._boundary_bias_at(sample[0], sample[1], sample_plate, sample_boundary) * weight
                total_weight += weight

        influence = 0.0 if total_weight == 0.0 else weighted_sum / total_weight
        self._cache_set(
            self._boundary_influence_cache,
            (q, r),
            influence,
            self._boundary_influence_cache_maxsize,
        )
        return influence

    def _boundary_bias_at(
        self,
        q: int,
        r: int,
        plate: PlateData | None,
        boundary: BoundaryData | None,
    ) -> float:
        if plate is None or boundary is None:
            return 0.0

        boundary_bias = 0.0
        if boundary.kind == BoundaryKind.CONVERGENT:
            boundary_bias += 0.20 * boundary.strength
            if plate is not None and plate.plate_type == PlateType.OCEANIC:
                for dq, dr in AXIAL_DIRECTIONS:
                    neighbor = self._tectonics.plate_at(q + dq, r + dr)
                    if neighbor is None or neighbor.plate_id == plate.plate_id:
                        continue
                    if neighbor.plate_type == PlateType.CONTINENTAL:
                        boundary_bias -= 0.18 * boundary.strength
                        break
        elif boundary.kind == BoundaryKind.DIVERGENT:
            if plate is not None and plate.plate_type == PlateType.OCEANIC:
                boundary_bias += 0.05 * boundary.strength
            else:
                boundary_bias -= 0.16 * boundary.strength
        elif boundary.kind == BoundaryKind.TRANSFORM:
            boundary_bias += 0.03 * boundary.strength
        return boundary_bias

    def _resolve_cache_maxsize(self) -> int:
        if self.config.profile.value == "DEV":
            return self.config.width * self.config.height
        return 200_000

    @staticmethod
    def _cache_get(cache: OrderedDict[tuple[int, int], object], key: tuple[int, int]) -> object | None:
        value = cache.get(key)
        if value is None:
            return None
        cache.move_to_end(key)
        return value

    @staticmethod
    def _cache_set(
        cache: OrderedDict[tuple[int, int], object],
        key: tuple[int, int],
        value: object,
        maxsize: int,
    ) -> None:
        cache[key] = value
        cache.move_to_end(key)
        while len(cache) > maxsize:
            cache.popitem(last=False)

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
        y_period = freq if self.config.wrap_y else None

        n00 = self._lattice_noise(ix0, iy0, x_period, y_period)
        n10 = self._lattice_noise(ix1, iy0, x_period, y_period)
        n01 = self._lattice_noise(ix0, iy1, x_period, y_period)
        n11 = self._lattice_noise(ix1, iy1, x_period, y_period)

        ux = self._smoothstep(fx)
        uy = self._smoothstep(fy)

        nx0 = self._lerp(n00, n10, ux)
        nx1 = self._lerp(n01, n11, ux)
        return self._lerp(nx0, nx1, uy)

    def _lattice_noise(self, ix: int, iy: int, x_period: int, y_period: int | None) -> float:
        wrapped_x = ix % x_period
        wrapped_y = iy if y_period is None else iy % y_period
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

    def get_river_strength(self, q: int, r: int) -> int:
        return self._hydrology.river_strength(q, r)

    def get_flow_to(self, q: int, r: int) -> tuple[int, int] | None:
        return self._hydrology.flow_to(q, r)

    def is_lake(self, q: int, r: int) -> bool:
        return self._hydrology.is_lake(q, r)
