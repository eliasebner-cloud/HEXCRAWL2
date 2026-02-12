"""Simple split time model for local realtime and manual world stepping."""

from __future__ import annotations


class TimeModel:
    """Tracks continuous local elapsed time and manual world ticks."""

    def __init__(self) -> None:
        self.local_elapsed_seconds = 0.0
        self.world_tick_count = 0

    def update(self, dt: float) -> None:
        """Advance local realtime by frame delta seconds."""
        self.local_elapsed_seconds += max(0.0, dt)

    def world_step(self, ticks: int = 1) -> None:
        """Advance world time by the requested positive number of ticks."""
        self.world_tick_count += max(0, ticks)

    @property
    def local_elapsed_mmss(self) -> str:
        """Return local elapsed time as MM:SS."""
        total_seconds = int(self.local_elapsed_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
