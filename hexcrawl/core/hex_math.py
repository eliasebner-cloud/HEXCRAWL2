"""Math helpers for pointy-top axial hex coordinates."""

from __future__ import annotations

import math

SQRT3 = math.sqrt(3)

# Axial neighbor offsets (pointy-top layout).
AXIAL_DIRECTIONS = (
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, 0),
    (-1, 1),
    (0, 1),
)


def axial_to_pixel(q: float, r: float, size: float) -> tuple[float, float]:
    """Convert axial coordinates to pixel center for pointy-top hexes."""
    x = size * (SQRT3 * q + (SQRT3 / 2.0) * r)
    y = size * (1.5 * r)
    return x, y


def pixel_to_axial(x: float, y: float, size: float) -> tuple[float, float]:
    """Convert pixel coordinates into fractional axial coordinates."""
    q = ((SQRT3 / 3.0) * x - (1.0 / 3.0) * y) / size
    r = ((2.0 / 3.0) * y) / size
    return q, r


def cube_round(x: float, y: float, z: float) -> tuple[int, int, int]:
    """Round fractional cube coordinates to the nearest valid hex."""
    rx = round(x)
    ry = round(y)
    rz = round(z)

    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)

    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry

    return int(rx), int(ry), int(rz)


def axial_round(q: float, r: float) -> tuple[int, int]:
    """Round fractional axial coordinates to the nearest integer axial hex."""
    x = q
    z = r
    y = -x - z
    rx, _, rz = cube_round(x, y, z)
    return rx, rz


def axial_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    """Return hex distance between two axial coordinates."""
    aq, ar = a
    bq, br = b
    dx = aq - bq
    dz = ar - br
    dy = -dx - dz
    return int(max(abs(dx), abs(dy), abs(dz)))
