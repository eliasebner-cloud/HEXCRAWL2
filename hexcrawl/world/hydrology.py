"""Deterministic hydrology model derived from final world heights."""

from __future__ import annotations

from collections import OrderedDict
from math import inf

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
        overflow_radius: int = 10,
    ) -> None:
        self.seed = int(seed)
        self.config = config
        self._height_fn = height_fn
        self._is_ocean_fn = is_ocean_fn

        self._cache_maxsize = self._resolve_cache_maxsize()
        self._overflow_radius = max(1, int(overflow_radius))
        self._supports_global_build = (self.config.width * self.config.height) <= self._cache_maxsize
        self._flow_cache: OrderedDict[tuple[int, int], tuple[int, int] | None] = OrderedDict()
        self._accumulation_cache: OrderedDict[tuple[int, int], int] = OrderedDict()
        self._river_strength_cache: OrderedDict[tuple[int, int], int] = OrderedDict()
        self._lake_cache: OrderedDict[tuple[int, int], bool] = OrderedDict()
        self._height_cache: OrderedDict[tuple[int, int], float] = OrderedDict()
        self._built = False

    def flow_to(self, q: int, r: int) -> tuple[int, int] | None:
        canonical = self.config.canonicalize(q, r)
        if canonical is None:
            return None
        self._ensure_built()
        if not self._supports_global_build and canonical not in self._flow_cache:
            self._cache_set(
                self._flow_cache,
                canonical,
                self._resolve_flow(canonical[0], canonical[1], heights={}),
                self._cache_maxsize,
            )
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
        if not self._supports_global_build and canonical not in self._lake_cache:
            is_lake = (not self._is_ocean_fn(*canonical)) and self.flow_to(*canonical) is None
            self._cache_set(self._lake_cache, canonical, is_lake, self._cache_maxsize)
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

        self._break_cycles(nodes)

        base: dict[tuple[int, int], int] = {coord: 0 if self._is_ocean_fn(*coord) else 1 for coord in nodes}
        upstreams: dict[tuple[int, int], list[tuple[int, int]]] = {coord: [] for coord in nodes}
        for coord in nodes:
            downstream = self._flow_cache[coord]
            if downstream is not None:
                upstreams[downstream].append(coord)

        accum: dict[tuple[int, int], int] = {}

        def compute(coord: tuple[int, int]) -> int:
            if coord in accum:
                return accum[coord]
            total = base[coord]
            for upstream in upstreams[coord]:
                total += compute(upstream)
            accum[coord] = total
            return total

        for coord in nodes:
            compute(coord)

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

    def _break_cycles(self, nodes: list[tuple[int, int]]) -> None:
        state: dict[tuple[int, int], int] = {}

        def dfs(coord: tuple[int, int]) -> None:
            state[coord] = 1
            nxt = self._flow_cache.get(coord)
            if nxt is not None:
                nxt_state = state.get(nxt, 0)
                if nxt_state == 0:
                    dfs(nxt)
                elif nxt_state == 1:
                    self._cache_set(self._flow_cache, coord, None, self._cache_maxsize)
            state[coord] = 2

        for coord in nodes:
            if state.get(coord, 0) == 0:
                dfs(coord)

    def _resolve_flow(
        self,
        q: int,
        r: int,
        heights: dict[tuple[int, int], float],
    ) -> tuple[int, int] | None:
        if self._is_ocean_fn(q, r):
            return None

        current = self._height_at(q, r, heights)
        best_neighbor: tuple[int, int] | None = None
        best_height = current

        for dq, dr in AXIAL_DIRECTIONS:
            neighbor = self.config.canonicalize(q + dq, r + dr)
            if neighbor is None:
                continue
            neighbor_height = self._height_at(neighbor[0], neighbor[1], heights)
            if neighbor_height < best_height:
                best_height = neighbor_height
                best_neighbor = neighbor

        if best_neighbor is not None:
            return best_neighbor
        return self._resolve_overflow(q, r, current, heights)

    def _resolve_overflow(
        self,
        q: int,
        r: int,
        sink_height: float,
        heights: dict[tuple[int, int], float],
    ) -> tuple[int, int] | None:
        source = (q, r)
        queue: list[tuple[int, int]] = [source]
        distance: dict[tuple[int, int], int] = {source: 0}
        parent: dict[tuple[int, int], tuple[int, int]] = {}
        best: tuple[float, int, int, int] | None = None
        best_coord: tuple[int, int] | None = None

        idx = 0
        while idx < len(queue):
            coord = queue[idx]
            idx += 1
            dist = distance[coord]
            if dist >= self._overflow_radius:
                continue

            for dq, dr in AXIAL_DIRECTIONS:
                neighbor = self.config.canonicalize(coord[0] + dq, coord[1] + dr)
                if neighbor is None or neighbor in distance:
                    continue

                distance[neighbor] = dist + 1
                parent[neighbor] = coord
                queue.append(neighbor)

                outlet_height = self._height_at(neighbor[0], neighbor[1], heights)
                if self._is_ocean_fn(*neighbor):
                    outlet_height = -inf
                elif outlet_height >= sink_height:
                    continue

                rank = (outlet_height, distance[neighbor], neighbor[0], neighbor[1])
                if best is None or rank < best:
                    best = rank
                    best_coord = neighbor

        if best_coord is None:
            return None

        step = best_coord
        while parent.get(step) and parent[step] != source:
            step = parent[step]
        return step

    def _height_at(
        self,
        q: int,
        r: int,
        heights: dict[tuple[int, int], float],
    ) -> float:
        coord = (q, r)
        if coord in heights:
            return heights[coord]
        if coord in self._height_cache:
            value = self._height_cache[coord]
            self._height_cache.move_to_end(coord)
            return value
        value = self._height_fn(q, r)
        self._cache_set(self._height_cache, coord, value, self._cache_maxsize)
        heights[coord] = value
        return value

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
