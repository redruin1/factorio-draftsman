# test_deconstruction_planner.py

from draftsman import __factorio_version_info__
from draftsman.classes.deconstruction_planner import DeconstructionPlanner, EntityFilter, TileFilter
from draftsman.constants import FilterMode, TileSelectionMode, ValidationMode
from draftsman.error import DataFormatError
from draftsman.signatures import AttrsIcon
from draftsman.utils import encode_version
from draftsman.warning import DraftsmanWarning, UnknownEntityWarning, UnknownTileWarning

import pytest


class TestDeconstructionPlannerTesting:
    def test_constructor(self):
        # Nothing
        decon_planner = DeconstructionPlanner()
        assert decon_planner.to_dict()["deconstruction_planner"] == {
            "item": "deconstruction-planner",
            "version": encode_version(*__factorio_version_info__),
        }

        # String
        decon_planner = DeconstructionPlanner.from_string(
            "0eNqrVkpJTc7PKy4pKk0uyczPiy/ISczLSy1SsqpWKk4tKcnMSy9WssorzcnRUcosSc1VskLToAvToKNUllpUDBRRsjKyMDQxtzQyNzUDIhOL2loAsN4j2w=="
        )
        assert decon_planner.to_dict()["deconstruction_planner"] == {
            "item": "deconstruction-planner",
            "version": encode_version(1, 1, 61),
        }

        # Dict
        # TODO: change this so it's identical to Entity(**entity_dict)
        test_planner = {
            "deconstruction_planner": {
                "settings": {
                    "tile_filter_mode": FilterMode.BLACKLIST,
                    "trees_and_rocks_only": True,
                }
            }
        }
        decon_planner = DeconstructionPlanner.from_dict(test_planner)
        assert decon_planner.to_dict()["deconstruction_planner"] == {
            "item": "deconstruction-planner",
            "settings": {
                "tile_filter_mode": FilterMode.BLACKLIST,
                "trees_and_rocks_only": True,
            },
            "version": encode_version(*__factorio_version_info__),
        }

        # TODO: reimplement
        # with pytest.warns(DraftsmanWarning):
        #     DeconstructionPlanner.from_dict(
        #         {"deconstruction_planner": {"something": "incorrect"}, "index": 1}
        #     )

        invalid_data = {
            "deconstruction_planner": {
                "item": "deconstruction-planner",
                "version": "incorrect",
                "settings": {"description": 100},
            }
        }
        with pytest.raises(DataFormatError):
            DeconstructionPlanner.from_dict(invalid_data)

        # TODO: reimplement
        # broken_planner = DeconstructionPlanner.from_dict(invalid_data, validation="none")
        # assert broken_planner.version == "incorrect"
        # assert broken_planner.description == 100
        # # Fix
        # broken_planner.version = __factorio_version_info__
        # broken_planner.description = "an actual string"
        # broken_planner.validate().reissue_all()  # No errors or warnings

    def test_entity_filter_count(self):
        assert DeconstructionPlanner().entity_filter_count == 30

    def test_tile_filter_count(self):
        assert DeconstructionPlanner().tile_filter_count == 30

    def test_set_icons(self):
        decon_planner = DeconstructionPlanner()
        assert decon_planner.icons == []

        decon_planner.icons = [
            "signal-A",
            {"index": 2, "signal": {"name": "signal-B", "type": "virtual"}},
        ]
        assert decon_planner.icons == [
            AttrsIcon(signal="signal-A", index=1),
            AttrsIcon(signal="signal-B", index=2),
        ]

    def test_set_entity_filter_mode(self):
        decon_planner = DeconstructionPlanner()

        decon_planner.entity_filter_mode = FilterMode.WHITELIST
        assert decon_planner.entity_filter_mode == FilterMode.WHITELIST

        decon_planner.entity_filter_mode = FilterMode.BLACKLIST
        assert decon_planner.entity_filter_mode == FilterMode.BLACKLIST

        # Errors
        with pytest.raises(DataFormatError):
            decon_planner.entity_filter_mode = "incorrect"

    def test_set_entity_filters(self):
        decon_planner = DeconstructionPlanner()

        # Test Verbose
        decon_planner.entity_filters = [
            {"name": "transport-belt", "index": 0},
            {"name": "fast-transport-belt", "index": 1},
        ]
        assert decon_planner.entity_filters == [
            EntityFilter(**{"name": "transport-belt", "index": 0}),
            EntityFilter(**{"name": "fast-transport-belt", "index": 1}),
        ]

        # Test Abridged
        decon_planner.set_entity_filters("transport-belt", "fast-transport-belt")
        assert decon_planner.entity_filters == [
            EntityFilter(**{"name": "transport-belt", "index": 0}),
            EntityFilter(**{"name": "fast-transport-belt", "index": 1}),
        ]

        # Test unknown entity
        with pytest.warns(UnknownEntityWarning):
            decon_planner.entity_filters = ["unknown-thingy"]
            assert decon_planner.entity_filters == [
                EntityFilter(**{"name": "unknown-thingy", "index": 0}),
            ]

        with pytest.raises(DataFormatError):
            decon_planner.entity_filters = "incorrect"

    def test_set_trees_and_rocks_only(self):
        decon_planner = DeconstructionPlanner()
        assert decon_planner.trees_and_rocks_only == False

        decon_planner.trees_and_rocks_only = True
        assert decon_planner.trees_and_rocks_only == True

        # Errors
        with pytest.raises(DataFormatError):
            decon_planner.trees_and_rocks_only = "incorrect"

    def test_set_tile_filter_mode(self):
        decon_planner = DeconstructionPlanner()

        decon_planner.tile_filter_mode = FilterMode.WHITELIST
        assert decon_planner.tile_filter_mode == FilterMode.WHITELIST

        decon_planner.tile_filter_mode = FilterMode.BLACKLIST
        assert decon_planner.tile_filter_mode == FilterMode.BLACKLIST

        # Errors
        with pytest.raises(DataFormatError):
            decon_planner.tile_filter_mode = "incorrect"

    def test_set_tile_filters(self):
        decon_planner = DeconstructionPlanner()

        # Test Verbose
        decon_planner.tile_filters = [
            {"name": "concrete", "index": 0},
            {"name": "stone-path", "index": 1},
        ]
        assert decon_planner.tile_filters == [
            TileFilter(**{"name": "concrete", "index": 0}),
            TileFilter(**{"name": "stone-path", "index": 1}),
        ]

        # Test Abridged
        decon_planner.set_tile_filters("concrete", "stone-path")
        assert decon_planner.tile_filters == [
            TileFilter(**{"name": "concrete", "index": 0}),
            TileFilter(**{"name": "stone-path", "index": 1}),
        ]

        # Test unknown entity
        with pytest.warns(UnknownTileWarning):
            decon_planner.tile_filters = ["unknown-thingy"]
            assert decon_planner.tile_filters == [
                TileFilter(**{"name": "unknown-thingy", "index": 0}),
            ]

        with pytest.raises(DataFormatError):
            decon_planner.tile_filters = "incorrect"

    def test_tile_selection_mode(self):
        decon_planner = DeconstructionPlanner()

        decon_planner.tile_selection_mode = TileSelectionMode.NORMAL
        assert decon_planner.tile_selection_mode == TileSelectionMode.NORMAL

        decon_planner.tile_selection_mode = TileSelectionMode.NEVER
        assert decon_planner.tile_selection_mode == TileSelectionMode.NEVER

        # Errors
        with pytest.raises(DataFormatError):
            decon_planner.tile_selection_mode = "incorrect"

    def test_set_entity_filter(self):
        decon_planner = DeconstructionPlanner()

        # Normal case
        decon_planner.set_entity_filter(0, "transport-belt")
        decon_planner.set_entity_filter(1, "fast-transport-belt")
        assert decon_planner.entity_filters == [
            EntityFilter(**{"name": "transport-belt", "index": 0}),
            EntityFilter(**{"name": "fast-transport-belt", "index": 1}),
        ]

        # Duplicate case
        decon_planner.set_entity_filter(0, "transport-belt")
        assert decon_planner.entity_filters == [
            EntityFilter(**{"name": "transport-belt", "index": 0}),
            EntityFilter(**{"name": "fast-transport-belt", "index": 1}),
        ]

        # None case
        decon_planner.set_entity_filter(0, None)
        assert decon_planner.entity_filters == [
            EntityFilter(**{"name": "fast-transport-belt", "index": 1})
        ]

        # TODO
        # with pytest.raises(DataFormatError):
        #     decon_planner.set_entity_filter("incorrect", None)

        with pytest.raises(DataFormatError):
            decon_planner.set_entity_filter("incorrect", "incorrect")

    def test_set_tile_filter(self):
        decon_planner = DeconstructionPlanner()

        # Normal case
        decon_planner.set_tile_filter(0, "concrete")
        decon_planner.set_tile_filter(1, "stone-path")
        assert decon_planner.tile_filters == [
            TileFilter(**{"name": "concrete", "index": 0}),
            TileFilter(**{"name": "stone-path", "index": 1}),
        ]

        # Duplicate case
        decon_planner.set_tile_filter(0, "concrete")
        assert decon_planner.tile_filters == [
            TileFilter(**{"name": "concrete", "index": 0}),
            TileFilter(**{"name": "stone-path", "index": 1}),
        ]

        # None case
        decon_planner.set_tile_filter(0, None)
        assert decon_planner.tile_filters == [
            TileFilter(**{"name": "stone-path", "index": 1})
        ]

        # TODO
        # with pytest.raises(DataFormatError):
        #     decon_planner.set_tile_filter("incorrect", None)

        with pytest.raises(DataFormatError):
            decon_planner.set_tile_filter("incorrect", "incorrect")
