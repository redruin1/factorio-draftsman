# test_storagetank.py

from draftsman.constants import Direction, LegacyDirection
from draftsman.entity import StorageTank, storage_tanks, Container
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_storage_tank():
    return StorageTank(
        "storage-tank",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


class TestStorageTank:
    def test_constructor_init(self):
        storage_tank = StorageTank(
            "storage-tank",
            tile_position=[15, 3],
            direction=Direction.NORTH,
        )
        assert storage_tank.to_dict() == {
            "name": "storage-tank",
            "position": {"x": 16.5, "y": 4.5},
            # "direction": 0, # default
        }
        storage_tank = StorageTank(
            "storage-tank",
            position={"x": 16.5, "y": 4.5},
            direction=Direction.EAST,
            tags={"A": "B"},
        )
        assert storage_tank.to_dict(version=(1, 0)) == {
            "name": "storage-tank",
            "position": {"x": 16.5, "y": 4.5},
            "direction": LegacyDirection.EAST,
            "tags": {"A": "B"},
        }
        assert storage_tank.to_dict(version=(2, 0)) == {
            "name": "storage-tank",
            "position": {"x": 16.5, "y": 4.5},
            "direction": Direction.EAST,
            "tags": {"A": "B"},
        }
        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            StorageTank.from_dict(
                {
                    "name": "storage-tank",
                    "position": {"x": 16.5, "y": 4.5},
                    "direction": Direction.WEST,
                    "invalid_keyword": 5,
                },
                version=(2, 0),
            )

        with pytest.warns(UnknownEntityWarning):
            StorageTank("this is not a storage tank")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            StorageTank("storage-tank", id=25)

        with pytest.raises(DataFormatError):
            StorageTank("storage-tank", position=DataFormatError)

        with pytest.raises(DataFormatError):
            StorageTank("storage-tank", direction="incorrect")

    def test_power_and_circuit_flags(self):
        for storage_tank_name in storage_tanks:
            container = StorageTank(storage_tank_name)
            assert container.power_connectable == False
            assert container.dual_power_connectable == False
            assert container.circuit_connectable == True
            assert container.dual_circuit_connectable == False

    def test_mergable_with(self):
        tank1 = StorageTank("storage-tank")
        tank2 = StorageTank("storage-tank", tags={"some": "stuff"})

        assert tank1.mergable_with(tank1)

        assert tank1.mergable_with(tank2)
        assert tank2.mergable_with(tank1)

        tank2.tile_position = (1, 1)
        assert not tank1.mergable_with(tank2)

    def test_merge(self):
        tank1 = StorageTank("storage-tank")
        tank2 = StorageTank("storage-tank", tags={"some": "stuff"})

        tank1.merge(tank2)
        del tank2

        assert tank1.tags == {"some": "stuff"}

    def test_eq(self):
        tank1 = StorageTank("storage-tank")
        tank2 = StorageTank("storage-tank")

        assert tank1 == tank2

        tank1.tags = {"some": "stuff"}

        assert tank1 != tank2

        container = Container()

        assert tank1 != container
        assert tank2 != container

        # hashable
        assert isinstance(tank1, Hashable)
