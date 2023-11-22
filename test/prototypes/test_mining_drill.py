# test_mining_drill.py

from draftsman.constants import MiningDrillReadMode, ValidationMode
from draftsman.entity import MiningDrill, mining_drills, Container
from draftsman.error import InvalidEntityError, InvalidItemError, DataFormatError
from draftsman.warning import (
    ModuleCapacityWarning,
    ItemLimitationWarning,
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


class TestMiningDrill:
    def test_constructor_init(self):
        drill = MiningDrill(
            "electric-mining-drill",
            items={"productivity-module": 1, "productivity-module-2": 1},
        )
        assert drill.to_dict() == {
            "name": "electric-mining-drill",
            "position": {"x": 1.5, "y": 1.5},
            "items": {"productivity-module": 1, "productivity-module-2": 1},
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            MiningDrill(unused_keyword="whatever")
        with pytest.warns(UnknownKeywordWarning):
            MiningDrill(control_behavior={"unused": "keyword"})
        # with pytest.warns(ModuleCapacityWarning): # TODO
        #     MiningDrill("electric-mining-drill", items={"productivity-module": 5})
        with pytest.warns(UnknownEntityWarning):
            MiningDrill("not a mining drill")

        # Errors
        with pytest.raises(DataFormatError):
            MiningDrill(items="incorrect")
        with pytest.raises(DataFormatError):
            MiningDrill(connections="incorrect")
        with pytest.raises(DataFormatError):
            MiningDrill(control_behavior="incorrect")

    def test_set_item_request(self):
        mining_drill = MiningDrill("electric-mining-drill")
        mining_drill.set_item_request("speed-module-3", 3)
        assert mining_drill.to_dict() == {
            "name": "electric-mining-drill",
            "position": {"x": 1.5, "y": 1.5},
            "items": {"speed-module-3": 3},
        }
        with pytest.warns(ModuleCapacityWarning):
            mining_drill.set_item_request("productivity-module-3", 3)
        assert mining_drill.to_dict() == {
            "name": "electric-mining-drill",
            "position": {"x": 1.5, "y": 1.5},
            "items": {"speed-module-3": 3, "productivity-module-3": 3},
        }

        with pytest.warns(ModuleCapacityWarning):
            mining_drill.set_item_request("speed-module-3", 2)
        assert mining_drill.items == {"speed-module-3": 2, "productivity-module-3": 3}

        mining_drill.set_item_request("speed-module-3", None)
        assert mining_drill.items == {"productivity-module-3": 3}

        with pytest.warns(ItemLimitationWarning):
            mining_drill.set_item_request("iron-ore", 2)

        with pytest.warns(UnknownItemWarning):
            mining_drill.set_item_request("incorrect", 2)

    def test_set_read_resources(self):
        mining_drill = MiningDrill()
        mining_drill.read_resources = True
        assert mining_drill.read_resources == True

        mining_drill.read_resources = None
        assert mining_drill.read_resources == None

        with pytest.raises(DataFormatError):
            mining_drill.read_resources = "incorrect"

        mining_drill.validate_assignment = "none"
        assert mining_drill.validate_assignment == ValidationMode.NONE

        mining_drill.read_resources = "incorrect"
        assert mining_drill.read_resources == "incorrect"
        assert mining_drill.to_dict() == {
            "name": "burner-mining-drill",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"circuit_read_resources": "incorrect"},
        }

    def test_set_read_mode(self):
        mining_drill = MiningDrill()
        mining_drill.read_mode = MiningDrillReadMode.UNDER_DRILL
        assert mining_drill.read_mode == MiningDrillReadMode.UNDER_DRILL

        mining_drill.read_mode = None
        assert mining_drill.read_mode == None

        with pytest.raises(DataFormatError):
            mining_drill.read_mode = "incorrect"

        mining_drill.validate_assignment = "none"
        assert mining_drill.validate_assignment == ValidationMode.NONE

        mining_drill.read_mode = "incorrect"
        assert mining_drill.read_mode == "incorrect"
        assert mining_drill.to_dict() == {
            "name": "burner-mining-drill",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"circuit_resource_read_mode": "incorrect"},
        }

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
        assert drill1.total_module_slots == 3
        assert drill1.module_slots_occupied == 0
        assert drill1.allowed_modules == {
            "effectivity-module",
            "effectivity-module-2",
            "effectivity-module-3",
            "productivity-module",
            "productivity-module-2",
            "productivity-module-3",
            "speed-module",
            "speed-module-2",
            "speed-module-3",
        }
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
