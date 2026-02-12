"""Tests for world configuration and coordinate canonicalization."""

from __future__ import annotations

import unittest

from hexcrawl.world.world_config import WorldProfile, build_world_config


class TestWorldConfig(unittest.TestCase):
    def test_wrap_x_canonicalizes_multiple_offsets(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        q_min = config.q_min
        q_max = config.q_max

        self.assertEqual(config.canonicalize(q_min, 0), (q_min, 0))
        self.assertEqual(config.canonicalize(q_max + 1, 0), (q_min, 0))
        self.assertEqual(config.canonicalize(q_min - 1, 0), (q_max, 0))
        self.assertEqual(config.canonicalize(q_min + config.width * 3 + 7, 0), (q_min + 7, 0))

    def test_out_of_bounds_r_is_rejected(self) -> None:
        config = build_world_config(WorldProfile.DEV)

        self.assertIsNone(config.canonicalize(0, config.r_min - 1))
        self.assertIsNone(config.canonicalize(0, config.r_max + 1))
        self.assertEqual(config.canonicalize(0, config.r_min), (0, config.r_min))
        self.assertEqual(config.canonicalize(0, config.r_max), (0, config.r_max))


if __name__ == "__main__":
    unittest.main()
