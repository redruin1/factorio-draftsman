# test_locomotive.py

from draftsman.constants import Orientation, Inventory
from draftsman.entity import Locomotive, locomotives, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    Color,
    BlueprintInsertPlan,
    ItemInventoryPositions,
    InventoryPosition,
    EquipmentComponent,
)
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_locomotive():
    if len(locomotives) == 0:
        return None
    return Locomotive(
        "cargo-wagon",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        orientation=Orientation.EAST,
        color=(0.5, 0.5, 0.5),
        item_requests=[
            BlueprintInsertPlan(
                id="coal",
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=Inventory.fuel, stack=0, count=50
                        )
                    ]
                ),
            ),
            BlueprintInsertPlan(
                id="energy-shield-equipment",
                items=ItemInventoryPositions(grid_count=1),
            ),
        ],
        equipment=[
            EquipmentComponent(equipment="energy-shield-equipment", position=(0, 0))
        ],
        enable_logistics_while_moving=False,
        tags={"blah": "blah"},
        validate_assignment="none",
    )


class TestLocomotive:
    def test_constructor_init(self):
        locomotive = Locomotive(
            "locomotive",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
            color=[0.0, 1.0, 0.0],
        )
        assert locomotive.to_dict() == {
            "name": "locomotive",
            "position": {"x": 1.0, "y": 1.0},
            "orientation": 0.75,
            "color": {"r": 0.0, "g": 1.0, "b": 0.0},
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Locomotive("this is not a locomotive").validate().reissue_all()
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with pytest.raises(DataFormatError):
            Locomotive("locomotive", orientation="wrong").validate().reissue_all()
        with pytest.raises(DataFormatError):
            Locomotive("locomotive", color="also wrong").validate().reissue_all()

    def test_color(self):
        assert Locomotive("locomotive").color == Color(
            234 / 255, 17 / 255, 0, 127 / 255
        )

    def test_mergable_with(self):
        train1 = Locomotive("locomotive")
        train2 = Locomotive("locomotive", color=(100, 100, 100), tags={"some": "stuff"})

        assert train1.mergable_with(train1)

        assert train1.mergable_with(train2)
        assert train2.mergable_with(train1)

        train2.orientation = 0.5
        assert not train1.mergable_with(train2)

    def test_merge(self):
        train1 = Locomotive("locomotive")
        train2 = Locomotive("locomotive", color=(100, 100, 100), tags={"some": "stuff"})

        train1.merge(train2)
        del train2

        assert train1.color == Color(r=100, g=100, b=100)
        assert train1.tags == {"some": "stuff"}

        assert train1.to_dict() == {
            "name": "locomotive",
            "position": {"x": 1.0, "y": 3.0},
            "color": {"r": 100, "g": 100, "b": 100},
            "tags": {"some": "stuff"},
        }

    def test_eq(self):
        train1 = Locomotive("locomotive")
        train2 = Locomotive("locomotive")

        assert train1 == train2

        train1.tags = {"some": "stuff"}

        assert train1 != train2

        container = Container()

        assert train1 != container
        assert train2 != container

        # hashable
        assert isinstance(train1, Hashable)
