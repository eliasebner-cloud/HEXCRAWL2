"""Tests for deterministic tectonic plate generation."""

from __future__ import annotations

import unittest

from hexcrawl.world.tectonics import BoundaryKind, PlateData, PlateType, TectonicsModel
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

    def test_boundary_classification_sign_regression(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        tectonics = TectonicsModel(seed=7, config=config)

        convergent, _ = tectonics._classify_boundary(
            current=PlateData(plate_id=1, plate_type=PlateType.CONTINENTAL, motion=(1, 0)),
            other=PlateData(plate_id=2, plate_type=PlateType.OCEANIC, motion=(-1, 0)),
            direction=(1, 0),
        )
        divergent, _ = tectonics._classify_boundary(
            current=PlateData(plate_id=3, plate_type=PlateType.OCEANIC, motion=(-1, 0)),
            other=PlateData(plate_id=4, plate_type=PlateType.CONTINENTAL, motion=(1, 0)),
            direction=(1, 0),
        )

        self.assertEqual(convergent, BoundaryKind.CONVERGENT)
        self.assertEqual(divergent, BoundaryKind.DIVERGENT)

    def test_caches_are_bounded_and_canonicalized(self) -> None:
        config = build_world_config(WorldProfile.DEV)
        tectonics = TectonicsModel(seed=9, config=config)

        self.assertEqual(tectonics._cache_maxsize, config.width * config.height)

        q, r = 25, 10
        tectonics.plate_at(q, r)
        tectonics.plate_at(q + config.width, r)
        self.assertEqual(len(tectonics._plate_cache), 1)

        maxsize = tectonics._cache_maxsize
        for i in range(maxsize + 25):
            cq = config.q_min + (i % config.width)
            cr = config.r_min + ((i // config.width) % config.height)
            tectonics.plate_at(cq, cr)
            tectonics.boundary_at(cq, cr)

        self.assertLessEqual(len(tectonics._plate_cache), maxsize)
        self.assertLessEqual(len(tectonics._boundary_cache), maxsize)


if __name__ == "__main__":
    unittest.main()
