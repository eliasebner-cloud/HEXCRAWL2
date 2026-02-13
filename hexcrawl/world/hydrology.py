"""Deterministic hydrology model derived from final world heights."""

from __future__ import annotations

from collections import OrderedDict

from hexcrawl.core.hex_math import AXIAL_DIRECTIONS
from hexcrawl.world.world_config import WorldConfig


class HydrologyModel:
    """Caches wrap-safe flow direction, accumulation, and lake data.

    Assumption: TARGET-sized worlds currently skip global hydrology prebuild when
    caches are capped below world_size. Chunked hydrology is future work.
    """

    def __init__(
        self,
        seed: int,
        config: WorldConfig,
        height_fn,
        is_ocean_fn,
    ) -> None:
        self.seed = int(seed)
        self.config = config
        self._height_fn = height_fn
        self._is_ocean_fn = is_ocean_fn

        self._cache_maxsize = self._resolve_cache_maxsize()
        self._supports_global_build = (self.config.width * self.config.height) <= self._cache_maxsize
        self._flow_cache: OrderedDict[tuple[int, int], tuple[int, int] | None] = OrderedDict()
        self._accumulation_cache: OrderedDict[tuple[int, int], int] = OrderedDict()
        self._river_strength_cache: OrderedDict[tuple[int, int], int] = OrderedDict()
        self._lake_cache: OrderedDict[tuple[int, int], bool] = OrderedDict()
        self._built = False

    def flow_to(self, q: int, r: int) -> tuple[int, int] | None:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return None
        self._ensure_built()
        return self._flow_cache.get(canonical)

    def accumulation(self, q: int, r: int) -> int:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return 0
        self._ensure_built()
        return self._accumulation_cache.get(canonical, 0)

    def river_strength(self, q: int, r: int) -> int:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return 0
        self._ensure_built()
        return self._river_strength_cache.get(canonical, 0)

    def is_lake(self, q: int, r: int) -> bool:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return False
        self._ensure_built()
        return self._lake_cache.get(canonical, False)

    def _ensure_built(self) -> None:
        if self._built:
            return
        if not self._supports_global_build:
            self._built = True
            return
        self._build_all()
        self._built = True

    def _build_all(self) -> None:
        nodes: list[tuple[int, int]] = []
        heights: dict[tuple[int, int], float] = {}

        for r in range(self.config.r_min, self.config.r_max + 1):
            for q in range(self.config.q_min, self.config.q_max + 1):
                coord = (q, r)
                nodes.append(coord)
                heights[coord] = self._height_fn(q, r)

        for q, r in nodes:
            self._cache_set(self._flow_cache, (q, r), self._resolve_flow(q, r, heights), self._cache_maxsize)

        accum: dict[tuple[int, int], int] = {coord: 0 if self._is_ocean_fn(*coord) else 1 for coord in nodes}
        ordered = sorted(nodes, key=lambda coord: heights[coord], reverse=True)
        for coord in ordered:
            downstream = self._flow_cache[coord]
            if downstream is None:
                continue
            accum[downstream] += accum[coord]

        for coord in nodes:
            is_ocean = self._is_ocean_fn(*coord)
            strength = 0 if is_ocean else accum[coord]
            self._cache_set(self._accumulation_cache, coord, accum[coord], self._cache_maxsize)
            self._cache_set(self._river_strength_cache, coord, strength, self._cache_maxsize)
            self._cache_set(
                self._lake_cache,
                coord,
                (not is_ocean) and self._flow_cache[coord] is None,
                self._cache_maxsize,
            )

    def _resolve_flow(
        self,
        q: int,
        r: int,
        heights: dict[tuple[int, int], float],
    ) -> tuple[int, int] | None:
        if self._is_ocean_fn(q, r):
            return None

        current = heights[(q, r)]
        best_neighbor: tuple[int, int] | None = None
        best_height = current

        for dq, dr in AXIAL_DIRECTIONS:
            neighbor = self.config.canonicalize(q + dq, r + dr)
            if neighbor is None:
                continue
            neighbor_height = heights[neighbor]
            if neighbor_height < best_height:
                best_height = neighbor_height
                best_neighbor = neighbor

        return best_neighbor

    def _resolve_cache_maxsize(self) -> int:
        if self.config.profile.value == "DEV":
            return self.config.width * self.config.height
        return 200_000

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
