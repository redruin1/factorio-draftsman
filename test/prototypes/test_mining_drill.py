# test_mining_drill.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.constants import (
    Direction,
    MiningDrillReadMode,
    ValidationMode,
    InventoryType,
)
from draftsman.data import mods
from draftsman.entity import MiningDrill, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    BlueprintInsertPlan,
    ItemInventoryPositions,
    InventoryPosition,
    Condition,
)
import draftsman.validators
from draftsman.warning import (
    UnknownEntityWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_mining_drill():
    return MiningDrill(
        "electric-mining-drill",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        circuit_enabled=True,
        circuit_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        connect_to_logistic_network=True,
        logistic_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        read_resources=False,
        read_mode=MiningDrillReadMode.TOTAL_PATCH,
        item_requests=[
            BlueprintInsertPlan(
                id="speed-module-3",
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.MINING_DRILL_MODULES,
                            stack=1,
                        )
                    ]
                ),
            )
        ],
        tags={"blah": "blah"},
    )


class TestMiningDrill:
    def test_constructor_init(self):
        drill = MiningDrill(
            "electric-mining-drill",
        )
        assert drill.to_dict() == {
            "name": "electric-mining-drill",
            "position": {"x": 1.5, "y": 1.5},
        }

        # Warnings
        # with pytest.warns(ModuleCapacityWarning): # TODO
        #     drill = MiningDrill("electric-mining-drill")
        #     drill.validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            MiningDrill("not a mining drill").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            MiningDrill(item_requests="incorrect").validate().reissue_all()
        with pytest.raises(DataFormatError):
            MiningDrill(tags="incorrect").validate().reissue_all()

    def test_allowed_effects(self):
        furnace = MiningDrill("burner-mining-drill")
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            assert furnace.allowed_effects == set()
        else:
            assert furnace.allowed_effects == set()

        furnace = MiningDrill("electric-mining-drill")
        # if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
        #     assert furnace.allowed_effects == {
        #         "speed",
        #         "productivity",
        #         "pollution",
        #         "consumption",
        #     }
        # else:
        assert furnace.allowed_effects == {
            "speed",
            "productivity",
            "quality",
            "pollution",
            "consumption",
        }

        with pytest.warns(UnknownEntityWarning):
            furnace = MiningDrill("unknown-mining-drill")
        assert furnace.allowed_effects == None

    def test_set_item_request(self):
        mining_drill = MiningDrill("electric-mining-drill")
        mining_drill.set_item_request(
            "speed-module-3", 3, inventory=InventoryType.MINING_DRILL_MODULES
        )
        assert mining_drill.to_dict(version=(1, 0)) == {
            "name": "electric-mining-drill",
            "position": {"x": 1.5, "y": 1.5},
            "items": {"speed-module-3": 3},
        }
        assert mining_drill.to_dict(version=(2, 0)) == {
            "name": "electric-mining-drill",
            "position": {"x": 1.5, "y": 1.5},
            "items": [
                {
                    "id": {"name": "speed-module-3"},
                    "items": {
                        "in_inventory": [
                            {
                                "inventory": 2,
                                "stack": 0,
                                "count": 3,
                            }
                        ]
                    },
                }
            ],
        }
        # TODO: reimplement
        # with pytest.warns(ModuleCapacityWarning):
        #     mining_drill.set_item_request("productivity-module-3", 3)
        # assert mining_drill.to_dict() == {
        #     "name": "electric-mining-drill",
        #     "position": {"x": 1.5, "y": 1.5},
        #     "items": {"speed-module-3": 3, "productivity-module-3": 3},
        # }

        # with pytest.warns(ModuleCapacityWarning):
        #     mining_drill.set_item_request("speed-module-3", 2)
        # assert mining_drill.items == {"speed-module-3": 2, "productivity-module-3": 3}

        # mining_drill.set_item_request("speed-module-3", None)
        # assert mining_drill.items == {"productivity-module-3": 3}

        # with pytest.warns(ItemLimitationWarning):
        #     mining_drill.set_item_request("iron-ore", 2)

        # with pytest.warns(UnknownItemWarning):
        #     mining_drill.set_item_request("incorrect", 2)

    def test_set_modules(self):
        mining_drill = MiningDrill("electric-mining-drill")

        mining_drill.request_modules("speed-module-3", 0)
        assert mining_drill.item_requests == [
            BlueprintInsertPlan(
                id={"name": "speed-module-3"},
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.MINING_DRILL_MODULES,
                            stack=0,
                            count=1,
                        ),
                    ],
                ),
            )
        ]

        mining_drill.request_modules("speed-module-3", (1, 2))
        assert mining_drill.item_requests == [
            BlueprintInsertPlan(
                id={"name": "speed-module-3"},
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.MINING_DRILL_MODULES,
                            stack=0,
                            count=1,
                        ),
                        InventoryPosition(
                            inventory=InventoryType.MINING_DRILL_MODULES,
                            stack=1,
                            count=1,
                        ),
                        InventoryPosition(
                            inventory=InventoryType.MINING_DRILL_MODULES,
                            stack=2,
                            count=1,
                        ),
                    ],
                ),
            )
        ]

        mining_drill.request_modules("productivity-module-3", range(3), "legendary")
        assert mining_drill.item_requests == [
            BlueprintInsertPlan(
                id={"name": "productivity-module-3", "quality": "legendary"},
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.MINING_DRILL_MODULES,
                            stack=0,
                            count=1,
                        ),
                        InventoryPosition(
                            inventory=InventoryType.MINING_DRILL_MODULES,
                            stack=1,
                            count=1,
                        ),
                        InventoryPosition(
                            inventory=InventoryType.MINING_DRILL_MODULES,
                            stack=2,
                            count=1,
                        ),
                    ],
                ),
            )
        ]

    def test_set_read_resources(self):
        mining_drill = MiningDrill("burner-mining-drill")
        assert mining_drill.read_resources == True

        mining_drill.read_resources = False
        assert mining_drill.read_resources == False

        with pytest.raises(DataFormatError):
            mining_drill.read_resources = "incorrect"

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            mining_drill.read_resources = "incorrect"
            assert mining_drill.read_resources == "incorrect"
            assert mining_drill.to_dict() == {
                "name": "burner-mining-drill",
                "position": {"x": 1, "y": 1},
                "control_behavior": {"circuit_read_resources": "incorrect"},
            }

    def test_set_read_mode(self):
        mining_drill = MiningDrill("burner-mining-drill")
        assert mining_drill.read_mode == MiningDrillReadMode.UNDER_DRILL

        mining_drill.read_mode = MiningDrillReadMode.TOTAL_PATCH
        assert mining_drill.read_mode == MiningDrillReadMode.TOTAL_PATCH

        with pytest.raises(ValueError):
            mining_drill.read_mode = "incorrect"

    def test_mergable_with(self):
        drill1 = MiningDrill("electric-mining-drill")
        drill2 = MiningDrill(
            "electric-mining-drill",
            # items={"productivity-module": 1, "productivity-module-2": 1},
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
            item_requests=[
                {
                    "id": {"name": "productivity-module"},
                    "items": {
                        "in_inventory": [{"inventory": 2, "stack": 0, "count": 1}]
                    },
                },
                {
                    "id": {"name": "productivity-module-2"},
                    "items": {
                        "in_inventory": [{"inventory": 2, "stack": 1, "count": 1}]
                    },
                },
            ],
            tags={"some": "stuff"},
        )
        assert drill2.module_slots_occupied == 2

        drill1.merge(drill2)
        del drill2

        assert drill1.item_requests == [
            BlueprintInsertPlan(
                **{
                    "id": "productivity-module",
                    "items": {
                        "in_inventory": [{"inventory": 2, "stack": 0, "count": 1}]
                    },
                }
            ),
            BlueprintInsertPlan(
                **{
                    "id": "productivity-module-2",
                    "items": {
                        "in_inventory": [{"inventory": 2, "stack": 1, "count": 1}]
                    },
                }
            ),
        ]
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
