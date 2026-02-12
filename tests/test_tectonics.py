"""Tests for deterministic tectonic plate generation."""

from __future__ import annotations

import unittest

from hexcrawl.world.tectonics import BoundaryKind, TectonicsModel
from hexcrawl.world.world_config import WorldProfile, build_world_config


class TestTectonics(unittest.TestCase):
    def test_deterministic_plate_and_boundary_outputs(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        first = TectonicsModel(seed=1337, config=config)
        second = TectonicsModel(seed=1337, config=config)

        coords = [(-25, 8), (0, 0), (13, 17), (87, -30)]
        for q, r in coords:
            self.assertEqual(first.plate_at(q, r), second.plate_at(q, r))
            self.assertEqual(first.boundary_at(q, r), second.boundary_at(q, r))

    def test_wrap_x_plate_identity(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        tectonics = TectonicsModel(seed=2025, config=config)

        q, r = 22, -11
        self.assertEqual(tectonics.plate_at(q, r), tectonics.plate_at(q + config.width, r))

    def test_plate_diversity_in_sample_window(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        tectonics = TectonicsModel(seed=1, config=config)

        found_plate_ids: set[int] = set()
        for q in range(-40, 41, 4):
            for r in range(-30, 31, 4):
                plate = tectonics.plate_at(q, r)
                self.assertIsNotNone(plate)
                found_plate_ids.add(plate.plate_id)

        self.assertGreaterEqual(len(found_plate_ids), 3)

    def test_boundary_kind_and_strength_ranges(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        tectonics = TectonicsModel(seed=42, config=config)

        for q in range(-20, 21, 5):
            for r in range(-20, 21, 5):
                boundary = tectonics.boundary_at(q, r)
                self.assertIn(boundary.kind, set(BoundaryKind))
                self.assertGreaterEqual(boundary.strength, 0.0)
                self.assertLessEqual(boundary.strength, 1.0)


if __name__ == "__main__":
    unittest.main()
