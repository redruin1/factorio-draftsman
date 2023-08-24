# test_deconstruction_planner.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import __factorio_version_info__
from draftsman.classes.deconstruction_planner import DeconstructionPlanner
from draftsman.constants import FilterMode, TileSelectionMode
from draftsman.error import DataFormatError
from draftsman import utils
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class DeconstructionPlannerTesting(unittest.TestCase):
    def test_constructor(self):
        # Nothing
        decon_planner = DeconstructionPlanner()
        assert decon_planner.to_dict()["deconstruction_planner"] == {
            "item": "deconstruction-planner",
            "settings": None,
            "version": utils.encode_version(*__factorio_version_info__),
        }

        # String
        decon_planner = DeconstructionPlanner(
            "0eNqrVkpJTc7PKy4pKk0uyczPiy/ISczLSy1SsqpWKk4tKcnMSy9WssorzcnRUcosSc1VskLToAvToKNUllpUDBRRsjKyMDQxtzQyNzUDIhOL2loAsN4j2w=="
        )
        assert decon_planner.to_dict()["deconstruction_planner"] == {
            "item": "deconstruction-planner",
            "settings": None,
            "version": utils.encode_version(1, 1, 61),
        }

        # Dict
        test_planner = {
            "deconstruction_planner": {
                "settings": {
                    "tile_filter_mode": FilterMode.BLACKLIST,
                    "trees_and_rocks_only": True,
                }
            }
        }
        decon_planner = DeconstructionPlanner(test_planner)
        assert decon_planner.to_dict()["deconstruction_planner"] == {
            "item": "deconstruction-planner",
            "settings": {
                "tile_filter_mode": FilterMode.BLACKLIST,
                "trees_and_rocks_only": True,
            },
            "version": utils.encode_version(*__factorio_version_info__),
        }

        with pytest.warns(DraftsmanWarning):
            DeconstructionPlanner(
                {"deconstruction_planner": {"something": "incorrect"}}
            )

    def test_set_entity_filter_mode(self):
        decon_planner = DeconstructionPlanner()

        decon_planner.entity_filter_mode = FilterMode.WHITELIST
        assert decon_planner.entity_filter_mode == FilterMode.WHITELIST
        assert (
            decon_planner._root["settings"]["entity_filter_mode"]
            == FilterMode.WHITELIST
        )

        decon_planner.entity_filter_mode = FilterMode.BLACKLIST
        assert decon_planner.entity_filter_mode == FilterMode.BLACKLIST
        assert (
            decon_planner._root["settings"]["entity_filter_mode"]
            == FilterMode.BLACKLIST
        )

        decon_planner.entity_filter_mode = None
        assert decon_planner.entity_filter_mode == None
        assert "entity_filter_mode" not in decon_planner._root["settings"]

        # Errors
        with pytest.raises(ValueError):
            decon_planner.entity_filter_mode = "incorrect"

    def test_set_entity_filters(self):
        decon_planner = DeconstructionPlanner()

        # Test Verbose
        decon_planner.entity_filters = [
            {"name": "transport-belt", "index": 1},
            {"name": "fast-transport-belt", "index": 2},
        ]
        assert decon_planner.entity_filters == [
            {"name": "transport-belt", "index": 1},
            {"name": "fast-transport-belt", "index": 2},
        ]

        # Test Abridged
        decon_planner.entity_filters = ["transport-belt", "fast-transport-belt"]
        assert decon_planner.entity_filters == [
            {"name": "transport-belt", "index": 1},
            {"name": "fast-transport-belt", "index": 2},
        ]

        # Errors
        with pytest.raises(DataFormatError):
            decon_planner.entity_filters = "incorrect"

    def test_set_trees_and_rocks_only(self):
        decon_planner = DeconstructionPlanner()

        decon_planner.trees_and_rocks_only = True
        assert decon_planner.trees_and_rocks_only == True
        assert decon_planner._root["settings"]["trees_and_rocks_only"] == True

        decon_planner.trees_and_rocks_only = False
        assert decon_planner.trees_and_rocks_only == False
        assert decon_planner._root["settings"]["trees_and_rocks_only"] == False

        decon_planner.trees_and_rocks_only = None
        assert decon_planner.trees_and_rocks_only == None
        assert "trees_and_rocks_only" not in decon_planner._root["settings"]

        # Errors
        with pytest.raises(TypeError):
            decon_planner.trees_and_rocks_only = "incorrect"

    def test_set_tile_filter_mode(self):
        decon_planner = DeconstructionPlanner()

        decon_planner.tile_filter_mode = FilterMode.WHITELIST
        assert decon_planner.tile_filter_mode == FilterMode.WHITELIST
        assert (
            decon_planner._root["settings"]["tile_filter_mode"] == FilterMode.WHITELIST
        )

        decon_planner.tile_filter_mode = FilterMode.BLACKLIST
        assert decon_planner.tile_filter_mode == FilterMode.BLACKLIST
        assert (
            decon_planner._root["settings"]["tile_filter_mode"] == FilterMode.BLACKLIST
        )

        decon_planner.tile_filter_mode = None
        assert decon_planner.tile_filter_mode == None
        assert "tile_filter_mode" not in decon_planner._root["settings"]

        # Errors
        with pytest.raises(ValueError):
            decon_planner.tile_filter_mode = "incorrect"

    def test_set_tile_filters(self):
        decon_planner = DeconstructionPlanner()

        # Test Verbose
        decon_planner.tile_filters = [
            {"name": "concrete", "index": 1},
            {"name": "stone-path", "index": 2},
        ]
        assert decon_planner.tile_filters == [
            {"name": "concrete", "index": 1},
            {"name": "stone-path", "index": 2},
        ]

        # Test Abridged
        decon_planner.tile_filters = ["concrete", "stone-path"]
        assert decon_planner.tile_filters == [
            {"name": "concrete", "index": 1},
            {"name": "stone-path", "index": 2},
        ]

        # Errors
        with pytest.raises(DataFormatError):
            decon_planner.tile_filters = "incorrect"

    def test_tile_selection_mode(self):
        decon_planner = DeconstructionPlanner()

        decon_planner.tile_selection_mode = TileSelectionMode.NORMAL
        assert decon_planner.tile_selection_mode == TileSelectionMode.NORMAL
        assert (
            decon_planner._root["settings"]["tile_selection_mode"]
            == TileSelectionMode.NORMAL
        )

        decon_planner.tile_selection_mode = TileSelectionMode.NEVER
        assert decon_planner.tile_selection_mode == TileSelectionMode.NEVER
        assert (
            decon_planner._root["settings"]["tile_selection_mode"]
            == TileSelectionMode.NEVER
        )

        # Errors
        with pytest.raises(ValueError):
            decon_planner.tile_selection_mode = "incorrect"

    def test_set_entity_filter(self):
        decon_planner = DeconstructionPlanner()

        # Normal case
        decon_planner.set_entity_filter(0, "transport-belt")
        decon_planner.set_entity_filter(1, "fast-transport-belt")
        assert decon_planner.entity_filters == [
            {"name": "transport-belt", "index": 1},
            {"name": "fast-transport-belt", "index": 2},
        ]

        # Duplicate case
        decon_planner.set_entity_filter(0, "transport-belt")
        assert decon_planner.entity_filters == [
            {"name": "transport-belt", "index": 1},
            {"name": "fast-transport-belt", "index": 2},
        ]

        # None case
        decon_planner.set_entity_filter(0, None)
        assert decon_planner.entity_filters == [
            {"name": "fast-transport-belt", "index": 2}
        ]

        # Errors
        with pytest.raises(IndexError):
            decon_planner.set_entity_filter(100, "transport-belt")

        # TODO: check for invalid input names

    def test_set_tile_filter(self):
        decon_planner = DeconstructionPlanner()

        # Normal case
        decon_planner.set_tile_filter(0, "concrete")
        decon_planner.set_tile_filter(1, "stone-path")
        assert decon_planner.tile_filters == [
            {"name": "concrete", "index": 1},
            {"name": "stone-path", "index": 2},
        ]

        # Duplicate case
        decon_planner.set_tile_filter(0, "concrete")
        assert decon_planner.tile_filters == [
            {"name": "concrete", "index": 1},
            {"name": "stone-path", "index": 2},
        ]

        # None case
        decon_planner.set_tile_filter(0, None)
        assert decon_planner.tile_filters == [{"name": "stone-path", "index": 2}]

        # Errors
        with pytest.raises(IndexError):
            decon_planner.set_tile_filter(100, "concrete")

        # TODO: check for invalid input names
