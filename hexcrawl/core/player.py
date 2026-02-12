"""Player state shared across world and local map contexts."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Player:
    """Tracks the player's position on the world hex map."""

    q: int = 0
    r: int = 0

    @property
    def hex_pos(self) -> tuple[int, int]:
        """Return the current axial hex position."""
        return self.q, self.r

    def move_to(self, q: int, r: int) -> None:
        """Move the player to a specific axial hex coordinate."""
        self.q = q
        self.r = r
