"""Deterministic lightweight erosion/polish helpers for world generation."""

from __future__ import annotations

from collections import OrderedDict

from hexcrawl.core.hex_math import AXIAL_DIRECTIONS
from hexcrawl.world.world_config import WorldConfig


class ErosionModel:
    """Applies deterministic river-carving and local smoothing on height fields."""

    def __init__(
        self,
        config: WorldConfig,
        base_height_fn,
        river_strength_fn,
        flow_to_fn,
    ) -> None:
        self.config = config
        self._base_height_fn = base_height_fn
        self._river_strength_fn = river_strength_fn
        self._flow_to_fn = flow_to_fn

        self._cache_maxsize = self._resolve_cache_maxsize()
        self._height_cache: OrderedDict[tuple[int, int], float] = OrderedDict()
        self._valley_cache: OrderedDict[tuple[int, int], float] = OrderedDict()

        # WG-6 tuning: lightweight, deterministic visual polish.
        self._carving_threshold = 180
        self._max_carve_depth = 0.08
        self._neighbor_relax_weight = 0.24

    def eroded_height(self, q: int, r: int) -> float:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return 0.0

        cached = self._cache_get(self._height_cache, canonical)
        if cached is not None:
            return cached

        cq, cr = canonical
        center_carved = self._carved_height_at(cq, cr)

        neighbor_values: list[float] = []
        for dq, dr in AXIAL_DIRECTIONS:
            neighbor = self.config.canonicalize(cq + dq, cr + dr)
            if neighbor is None:
                continue
            neighbor_values.append(self._carved_height_at(*neighbor))

        if neighbor_values:
            neighbor_mean = sum(neighbor_values) / len(neighbor_values)
            polished = (center_carved * (1.0 - self._neighbor_relax_weight)) + (
                neighbor_mean * self._neighbor_relax_weight
            )
        else:
            polished = center_carved

        clamped = max(0.0, min(1.0, polished))
        self._cache_set(self._height_cache, canonical, clamped, self._cache_maxsize)
        return clamped

    def valley_strength(self, q: int, r: int) -> float:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return 0.0

        cached = self._cache_get(self._valley_cache, canonical)
        if cached is not None:
            return cached

        strength = self._valley_strength_at(*canonical)
        self._cache_set(self._valley_cache, canonical, strength, self._cache_maxsize)
        return strength

    def _carved_height_at(self, q: int, r: int) -> float:
        base = self._base_height_fn(q, r)
        carved = base - self.valley_strength(q, r)
        return max(0.0, min(1.0, carved))

    def _valley_strength_at(self, q: int, r: int) -> float:
        river_strength = self._river_strength_fn(q, r)
        if river_strength < self._carving_threshold:
            return 0.0

        # Increase carve depth with larger rivers while keeping it bounded.
        normalized = min(1.0, (river_strength - self._carving_threshold) / float(self._carving_threshold * 8))
        local = self._max_carve_depth * normalized

        # Strengthen carving for downstream trunk segments.
        if self._flow_to_fn(q, r) is not None:
            local *= 1.15

        return min(self._max_carve_depth, local)

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
