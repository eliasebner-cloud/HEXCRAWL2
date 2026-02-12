"""Deterministic tectonic plate model for macro height modulation."""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum

from hexcrawl.core.hex_math import AXIAL_DIRECTIONS
from hexcrawl.world.world_config import WorldConfig, WorldProfile


class PlateType(str, Enum):
    OCEANIC = "OCEANIC"
    CONTINENTAL = "CONTINENTAL"


class BoundaryKind(str, Enum):
    NONE = "NONE"
    CONVERGENT = "CONVERGENT"
    DIVERGENT = "DIVERGENT"
    TRANSFORM = "TRANSFORM"


@dataclass(frozen=True)
class PlateData:
    plate_id: int
    plate_type: PlateType
    motion: tuple[int, int]


@dataclass(frozen=True)
class BoundaryData:
    kind: BoundaryKind
    strength: float


class TectonicsModel:
    """Voronoi-like plate assignment with boundary classification on a wrapped X world."""

    _MOTIONS: tuple[tuple[int, int], ...] = AXIAL_DIRECTIONS

    def __init__(self, seed: int, config: WorldConfig) -> None:
        self.seed = int(seed)
        self.config = config
        self._seeds = self._build_plate_seeds()
        self._cache_maxsize = 200_000 if config.profile == WorldProfile.TARGET else config.width * config.height
        self._plate_cache: OrderedDict[tuple[int, int], PlateData] = OrderedDict()
        self._boundary_cache: OrderedDict[tuple[int, int], BoundaryData] = OrderedDict()

    def plate_at(self, q: int, r: int) -> PlateData | None:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return None
        cached = self._cache_get(self._plate_cache, canonical)
        if cached is not None:
            return cached

        cq, cr = canonical
        plate_id, _, _, _, _ = self._nearest_seed(cq, cr)
        plate = PlateData(
            plate_id=plate_id,
            plate_type=self._plate_type(plate_id),
            motion=self._MOTIONS[self._hash_u64("motion", plate_id) % len(self._MOTIONS)],
        )
        self._cache_put(self._plate_cache, canonical, plate)
        return plate

    def boundary_at(self, q: int, r: int) -> BoundaryData:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return BoundaryData(kind=BoundaryKind.NONE, strength=0.0)
        cached = self._cache_get(self._boundary_cache, canonical)
        if cached is not None:
            return cached

        current = self.plate_at(*canonical)
        assert current is not None
        best = BoundaryData(kind=BoundaryKind.NONE, strength=0.0)

        for dq, dr in AXIAL_DIRECTIONS:
            neighbor = self.config.canonicalize(canonical[0] + dq, canonical[1] + dr)
            if neighbor is None:
                continue
            other = self.plate_at(*neighbor)
            assert other is not None
            if other.plate_id == current.plate_id:
                continue

            kind, strength = self._classify_boundary(current, other, (dq, dr))
            if strength > best.strength:
                best = BoundaryData(kind=kind, strength=strength)

        self._cache_put(self._boundary_cache, canonical, best)
        return best

    def _classify_boundary(
        self,
        current: PlateData,
        other: PlateData,
        direction: tuple[int, int],
    ) -> tuple[BoundaryKind, float]:
        rel_motion = (
            current.motion[0] - other.motion[0],
            current.motion[1] - other.motion[1],
        )
        dir_len_sq = direction[0] * direction[0] + direction[1] * direction[1]
        if dir_len_sq == 0:
            return BoundaryKind.NONE, 0.0

        normal_component = (rel_motion[0] * direction[0] + rel_motion[1] * direction[1]) / float(dir_len_sq)
        tangent = (direction[1], -direction[0])
        tangent_len_sq = tangent[0] * tangent[0] + tangent[1] * tangent[1]
        tangential_component = (
            (rel_motion[0] * tangent[0] + rel_motion[1] * tangent[1]) / float(tangent_len_sq)
            if tangent_len_sq
            else 0.0
        )

        n_abs = abs(normal_component)
        t_abs = abs(tangential_component)

        if normal_component >= 0.25:
            return BoundaryKind.CONVERGENT, min(1.0, n_abs / 2.5)
        if normal_component <= -0.25:
            return BoundaryKind.DIVERGENT, min(1.0, n_abs / 2.5)
        return BoundaryKind.TRANSFORM, min(1.0, max(0.0, t_abs / 2.5))

    def _cache_get(self, cache: OrderedDict[tuple[int, int], PlateData | BoundaryData], key: tuple[int, int]) -> PlateData | BoundaryData | None:
        value = cache.get(key)
        if value is not None:
            cache.move_to_end(key)
        return value

    def _cache_put(
        self,
        cache: OrderedDict[tuple[int, int], PlateData | BoundaryData],
        key: tuple[int, int],
        value: PlateData | BoundaryData,
    ) -> None:
        cache[key] = value
        cache.move_to_end(key)
        if len(cache) > self._cache_maxsize:
            cache.popitem(last=False)

    def _build_plate_seeds(self) -> tuple[tuple[int, int, int], ...]:
        plate_count = max(12, min(96, (self.config.width * self.config.height) // 4096))
        seeds: list[tuple[int, int, int]] = []
        for plate_id in range(plate_count):
            sq = self.config.q_min + (self._hash_u64("seed_q", plate_id) % self.config.width)
            sr = self.config.r_min + (self._hash_u64("seed_r", plate_id) % self.config.height)
            seeds.append((plate_id, sq, sr))
        return tuple(seeds)

    def _nearest_seed(self, q: int, r: int) -> tuple[int, int, int, int, int]:
        best: tuple[int, int, int, int, int] | None = None

        for plate_id, sq, sr in self._seeds:
            for wrap in (-self.config.width, 0, self.config.width):
                dx = q - (sq + wrap)
                dy = r - sr
                dist_sq = dx * dx + dy * dy
                candidate = (dist_sq, plate_id, sq, sr, wrap)
                if best is None or candidate < best:
                    best = candidate

        assert best is not None
        _, plate_id, sq, sr, wrap = best
        return plate_id, sq, sr, wrap, best[0]

    def _plate_type(self, plate_id: int) -> PlateType:
        sample = self._hash_u64("plate_type", plate_id) / float((1 << 64) - 1)
        return PlateType.CONTINENTAL if sample >= 0.45 else PlateType.OCEANIC

    def _hash_u64(self, key: str, value: int) -> int:
        msg = f"{self.seed}:{key}:{value}".encode("utf-8")
        digest = hashlib.blake2b(msg, digest_size=8).digest()
        return int.from_bytes(digest, byteorder="big", signed=False)
