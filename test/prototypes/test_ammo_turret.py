# test_ammo_turret.py

from draftsman.constants import Direction, InventoryType
from draftsman.entity import AmmoTurret, ammo_turrets, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    Condition,
    TargetID,
    BlueprintInsertPlan,
    ItemInventoryPositions,
    InventoryPosition,
)
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_ammo_turret():
    return AmmoTurret(
        "gun-turret",
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
        priority_list=["medium-biter"],
        ignore_unprioritized=True,
        set_priority_list=True,
        set_ignore_unprioritized=True,
        ignore_unlisted_targets_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        read_ammo=False,
        item_requests=[
            BlueprintInsertPlan(
                id="firearm-magazine",
                items=ItemInventoryPositions(
                    in_inventory=[
                        InventoryPosition(
                            inventory=InventoryType.TURRET_AMMO, stack=0, count=200
                        )
                    ]
                ),
            )
        ],
        tags={"blah": "blah"},
    )


class TestAmmoTurret:
    def test_constructor_init(self):
        turret = AmmoTurret("gun-turret")
        turret.validate().reissue_all()
        assert turret.to_dict() == {
            "name": "gun-turret",
            "position": {"x": 1.0, "y": 1.0},
        }

        with pytest.warns(UnknownEntityWarning):
            turret = AmmoTurret("this is not a turret")
            turret.validate().reissue_all()

    def test_flags(self):
        turret = AmmoTurret("gun-turret")
        assert turret.rotatable == True
        assert turret.square == True
        # TODO: move
        # turret = AmmoTurret("flamethrower-turret")
        # assert turret.rotatable == True
        # assert turret.square == False

    def test_priority_condition(self):
        turret = AmmoTurret("gun-turret")
        turret.set_ignore_unlisted_targets_condition("signal-A", ">", "signal-B")
        assert turret.ignore_unlisted_targets_condition == Condition(
            first_signal="signal-A", comparator=">", second_signal="signal-B"
        )

    def test_target_priority_filters(self):
        turret = AmmoTurret("gun-turret")
        turret.priority_list = ["small-biter", "medium-biter"]
        assert turret.priority_list == [
            TargetID(index=0, name="small-biter"),
            TargetID(index=1, name="medium-biter"),
        ]
        assert turret.to_dict(version=(1, 0)) == {
            "name": "gun-turret",
            "position": {"x": 1.0, "y": 1.0},
        }
        assert turret.to_dict(version=(2, 0)) == {
            "name": "gun-turret",
            "position": {"x": 1.0, "y": 1.0},
            "priority_list": [
                {
                    "index": 0,
                    "name": "small-biter",
                },
                {"index": 1, "name": "medium-biter"},
            ],
        }

        turret.priority_list = [
            TargetID(index=0, name="small-biter"),
            TargetID(index=1, name="medium-biter"),
        ]
        assert turret.priority_list == [
            TargetID(index=0, name="small-biter"),
            TargetID(index=1, name="medium-biter"),
        ]
        assert turret.to_dict(version=(2, 0)) == {
            "name": "gun-turret",
            "position": {"x": 1.0, "y": 1.0},
            "priority_list": [
                {
                    "index": 0,
                    "name": "small-biter",
                },
                {"index": 1, "name": "medium-biter"},
            ],
        }

        with pytest.raises(DataFormatError):
            turret.priority_list = [TypeError]
        with pytest.raises(DataFormatError):
            turret.priority_list = TypeError

    def test_mergable_with(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret", tags={"some": "stuff"})

        assert turret1.mergable_with(turret1)

        assert turret1.mergable_with(turret2)
        assert turret2.mergable_with(turret1)

        turret2.tile_position = (1, 1)
        assert not turret1.mergable_with(turret2)

    def test_merge(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret", tags={"some": "stuff"})

        turret1.merge(turret2)
        del turret2

        assert turret1.tags == {"some": "stuff"}

    def test_eq(self):
        turret1 = AmmoTurret("gun-turret")
        turret2 = AmmoTurret("gun-turret")

        assert turret1 == turret2

        turret1.tags = {"some": "stuff"}

        assert turret1 != turret2

        container = Container()

        assert turret1 != container
        assert turret2 != container

        # hashable
        assert isinstance(turret1, Hashable)
