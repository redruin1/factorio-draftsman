# test_mining_drill.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import MiningDrillReadMode
from draftsman.entity import MiningDrill, mining_drills, Container
from draftsman.error import InvalidEntityError, InvalidItemError, DataFormatError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleCapacityWarning,
    ItemLimitationWarning,
)

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class MiningDrillTesting(unittest.TestCase):
    def test_constructor_init(self):
        drill = MiningDrill(
            "electric-mining-drill",
            items={"productivity-module": 1, "productivity-module-2": 1},
        )

        # Warnings
        with pytest.warns(DraftsmanWarning):
            MiningDrill(unused_keyword="whatever")
        # TODO: move to validate
        # with pytest.warns(ModuleCapacityWarning):
        #     MiningDrill("electric-mining-drill", items={"productivity-module": 5})

        # Errors
        with pytest.raises(InvalidEntityError):
            MiningDrill("not a mining drill")
        # TODO: move to validate
        # with pytest.raises(DataFormatError):
        #     MiningDrill(control_behavior={"unused_key": "something"})

    def test_set_item_request(self):
        mining_drill = MiningDrill("electric-mining-drill")
        mining_drill.set_item_request("speed-module-3", 3)
        assert mining_drill.to_dict() == {
            "name": "electric-mining-drill",
            "position": {"x": 1.5, "y": 1.5},
            "items": {"speed-module-3": 3},
        }
        # TODO: move to validate/inspect
        # with pytest.warns(ModuleCapacityWarning):
        #     mining_drill.set_item_request("productivity-module-3", 3)
        # assert mining_drill.to_dict() == {
        #     "name": "electric-mining-drill",
        #     "position": {"x": 1.5, "y": 1.5},
        #     "items": {"speed-module-3": 3, "productivity-module-3": 3},
        # }
        mining_drill.set_item_request("speed-module-3", None)
        assert mining_drill.items == {}
        mining_drill.set_item_requests(None)
        assert mining_drill.items == {}
        with pytest.warns(ItemLimitationWarning):
            mining_drill.set_item_request("iron-ore", 2)

        # Errors
        with pytest.raises(InvalidItemError):
            mining_drill.set_item_request("incorrect", 2)

    def test_set_read_resources(self):
        mining_drill = MiningDrill()
        mining_drill.read_resources = True
        assert mining_drill.read_resources == True
        assert mining_drill.control_behavior == {"circuit_read_resources": True}
        mining_drill.read_resources = None
        assert mining_drill.control_behavior == {}
        with pytest.raises(TypeError):
            mining_drill.read_resources = "incorrect"

    def test_set_read_mode(self):
        mining_drill = MiningDrill()
        mining_drill.read_mode = MiningDrillReadMode.UNDER_DRILL
        assert mining_drill.read_mode == MiningDrillReadMode.UNDER_DRILL
        assert mining_drill.control_behavior == {
            "circuit_resource_read_mode": MiningDrillReadMode.UNDER_DRILL
        }
        mining_drill.read_mode = None
        assert mining_drill.control_behavior == {}

        with pytest.raises(ValueError):
            mining_drill.read_mode = "incorrect"

    def test_mergable_with(self):
        drill1 = MiningDrill("electric-mining-drill")
        drill2 = MiningDrill(
            "electric-mining-drill",
            items={"productivity-module": 1, "productivity-module-2": 1},
            tags={"some": "stuff"},
        )

        assert drill1.mergable_with(drill1)

        assert drill1.mergable_with(drill2)
        assert drill2.mergable_with(drill1)

        drill2.tile_position = (1, 1)
        assert not drill1.mergable_with(drill2)

    def test_merge(self):
        drill1 = MiningDrill("electric-mining-drill")
        drill2 = MiningDrill(
            "electric-mining-drill",
            items={"productivity-module": 1, "productivity-module-2": 1},
            tags={"some": "stuff"},
        )

        drill1.merge(drill2)
        del drill2

        assert drill1.items == {"productivity-module": 1, "productivity-module-2": 1}
        assert drill1.tags == {"some": "stuff"}

    def test_eq(self):
        drill1 = MiningDrill("electric-mining-drill")
        drill2 = MiningDrill("electric-mining-drill")

        assert drill1 == drill2

        drill1.tags = {"some": "stuff"}

        assert drill1 != drill2

        container = Container()

        assert drill1 != container
        assert drill2 != container

        # hashable
        assert isinstance(drill1, Hashable)
