# test_lab.py

from draftsman.constants import InventoryType
from draftsman.entity import Lab, labs, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    BlueprintInsertPlan,
    ItemID,
    ItemInventoryPositions,
    InventoryPosition,
)
from draftsman.warning import (
    ModuleCapacityWarning,
    ItemLimitationWarning,
    UnknownEntityWarning,
)

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_lab():
    if len(labs) == 0:
        return None
    return Lab(
        "lab",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        item_requests=[
            BlueprintInsertPlan(
                id="productivity-module-3",
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.lab_modules,
                            stack=0,
                        )
                    ]
                ),
            )
        ],
        tags={"blah": "blah"},
    )


class TestLab:
    def test_contstructor_init(self):
        lab = Lab()

        with pytest.warns(UnknownEntityWarning):
            Lab("this is not a lab").validate().reissue_all()

    def test_inputs(self):
        lab = Lab("lab")

        # TODO: how should this be verified on different data versions?
        assert lab.inputs == [
            "automation-science-pack",
            "logistic-science-pack",
            "military-science-pack",
            "chemical-science-pack",
            "production-science-pack",
            "utility-science-pack",
            "space-science-pack",
            "metallurgic-science-pack",
            "agricultural-science-pack",
            "electromagnetic-science-pack",
            "cryogenic-science-pack",
            "promethium-science-pack",
        ]

        with pytest.warns(UnknownEntityWarning):
            lab = Lab("unknown")
        assert lab.inputs is None

    def test_allowed_effects(self):
        lab = Lab("lab")
        assert lab.allowed_effects == {
            "speed",
            "pollution",
            "productivity",
            "quality",
            "consumption",
        }

    def test_request_modules(self):
        lab = Lab("lab")
        lab.request_modules("productivity-module-3", (0, 1), "legendary")
        assert lab.item_requests == [
            BlueprintInsertPlan(
                id=ItemID(name="productivity-module-3", quality="legendary"),
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.lab_modules,
                            stack=0,
                        ),
                        InventoryPosition(
                            inventory=InventoryType.lab_modules,
                            stack=1,
                        ),
                    ]
                ),
            )
        ]

    # def test_set_item_request(self):
    #     lab = Lab("lab")

    #     lab.set_item_request("productivity-module-3", 2)
    #     assert lab.items == {"productivity-module-3": 2}
    #     assert lab.module_slots_occupied == 2

    #     # Warnings
    #     with pytest.warns(ModuleCapacityWarning):
    #         lab.set_item_request("speed-module-2", 2)
    #     assert lab.items == {"productivity-module-3": 2, "speed-module-2": 2}
    #     assert lab.module_slots_occupied == 4

    #     lab.set_item_request("speed-module-2", None)
    #     assert lab.items == {"productivity-module-3": 2}

    #     lab.set_item_request("automation-science-pack", 10)
    #     assert lab.items == {"productivity-module-3": 2, "automation-science-pack": 10}
    #     assert lab.module_slots_occupied == 2

    #     # Warnings
    #     with pytest.warns(ItemLimitationWarning):
    #         lab.set_item_request("iron-plate", 100)
    #     assert lab.items == {
    #         "productivity-module-3": 2,
    #         "automation-science-pack": 10,
    #         "iron-plate": 100,
    #     }

    #     # Errors
    #     lab.items = {}
    #     assert lab.module_slots_occupied == 0

    #     with pytest.raises(DataFormatError):
    #         lab.set_item_request(TypeError, 100)
    #     with pytest.warns(UnknownItemWarning):
    #         lab.set_item_request("unknown", 100)
    #     with pytest.raises(DataFormatError):
    #         lab.set_item_request("logistic-science-pack", TypeError)
    #     with pytest.raises(DataFormatError):
    #         lab.set_item_request("logistic-science-pack", -1)

    #     assert lab.items == {"unknown": 100}
    #     assert lab.module_slots_occupied == 0

    def test_request_modules(self):
        lab = Lab("lab")
        assert lab.module_slots_occupied == 0

        lab.request_modules("productivity-module-3", (0, 1), quality="legendary")
        assert lab.module_slots_occupied == 2
        assert lab.item_requests == [
            BlueprintInsertPlan(
                id={"name": "productivity-module-3", "quality": "legendary"},
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.lab_modules,
                            stack=0,
                        ),
                        InventoryPosition(
                            inventory=InventoryType.lab_modules,
                            stack=1,
                        ),
                    ]
                ),
            )
        ]

    def test_mergable_with(self):
        lab1 = Lab("lab")
        lab2 = Lab("lab", tags={"some": "stuff"})

        assert lab1.mergable_with(lab1)

        assert lab1.mergable_with(lab2)
        assert lab2.mergable_with(lab1)

        lab2.tile_position = (1, 1)
        assert not lab1.mergable_with(lab2)

    def test_merge(self):
        lab1 = Lab("lab")
        lab2 = Lab("lab", tags={"some": "stuff"})

        lab1.merge(lab2)
        del lab2

        assert lab1.tags == {"some": "stuff"}

    def test_eq(self):
        lab1 = Lab("lab")
        lab2 = Lab("lab")

        assert lab1 == lab2

        lab1.tags = {"some": "stuff"}

        assert lab1 != lab2

        container = Container()

        assert lab1 != container
        assert lab2 != container

        # hashable
        assert isinstance(lab1, Hashable)
