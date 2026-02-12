"""Central world configuration and coordinate canonicalization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WorldProfile(str, Enum):
    """Named world-size profiles."""

    DEV = "DEV"
    TARGET = "TARGET"


@dataclass(frozen=True)
class WorldConfig:
    """Canonical world dimensions and wrapping behavior."""

    profile: WorldProfile
    width: int
    height: int
    target_size: tuple[int, int] = (4000, 2000)
    dev_size: tuple[int, int] = (512, 256)
    macro_size: tuple[int, int] = (500, 250)
    chunk_size: tuple[int, int] = (64, 64)
    wrap_x: bool = True
    wrap_y: bool = False

    @property
    def q_min(self) -> int:
        return -(self.width // 2)

    @property
    def q_max(self) -> int:
        return self.q_min + self.width - 1

    @property
    def r_min(self) -> int:
        return -(self.height // 2)

    @property
    def r_max(self) -> int:
        return self.r_min + self.height - 1

    def is_r_in_bounds(self, r: int) -> bool:
        return self.r_min <= r <= self.r_max

    def canonicalize(self, q: int, r: int) -> tuple[int, int] | None:
        """Return canonical world coordinates or None for out-of-world rows."""
        if not self.is_r_in_bounds(r):
            return None

        if self.wrap_x:
            q = ((q - self.q_min) % self.width) + self.q_min
        elif q < self.q_min or q > self.q_max:
            return None

        return q, r


def build_world_config(profile: WorldProfile) -> WorldConfig:
    """Build a concrete world configuration for a profile."""
    if profile == WorldProfile.TARGET:
        width, height = 4000, 2000
    else:
        width, height = 512, 256

    return WorldConfig(profile=profile, width=width, height=height)


def default_world_config() -> WorldConfig:
    """Default active world configuration used by game bootstrap and tests."""
    return build_world_config(WorldProfile.DEV)
