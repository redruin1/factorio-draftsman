# test_storagetank.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import StorageTank, storage_tanks, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class StorageTankTesting(unittest.TestCase):
    def test_constructor_init(self):
        storage_tank = StorageTank(
            "storage-tank",
            tile_position=[15, 3],
            direction=Direction.NORTH,
            connections={
                "1": {
                    "red": [
                        {"entity_id": 2},
                        {"entity_id": 2, "circuit_id": 1},
                    ]
                }
            },
        )
        assert storage_tank.to_dict() == {
            "name": "storage-tank",
            "position": {"x": 16.5, "y": 4.5},
            # "direction": 0, # not here because 0 is the default direction
            "connections": {
                "1": {
                    "red": [
                        {"entity_id": 2},
                        {"entity_id": 2, "circuit_id": 1},
                    ]
                }
            },
        }
        storage_tank = StorageTank(
            "storage-tank",
            position={"x": 16.5, "y": 4.5},
            direction=Direction.EAST,
            tags={"A": "B"},
        )
        assert storage_tank.to_dict() == {
            "name": "storage-tank",
            "position": {"x": 16.5, "y": 4.5},
            "direction": 2,
            "tags": {"A": "B"},
        }
        # Warnings
        with pytest.warns(DraftsmanWarning):
            StorageTank(position=[0, 0], direction=Direction.WEST, invalid_keyword=5)

        # Errors
        # Raises InvalidEntityID when not in containers
        with pytest.raises(InvalidEntityError):
            StorageTank("this is not a storage tank")

        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            StorageTank("storage-tank", id=25)

        with pytest.raises(TypeError):
            StorageTank("storage-tank", position=TypeError)

        with pytest.raises(ValueError):
            StorageTank("storage-tank", direction="incorrect")

        # TODO: move to validate
        # with pytest.raises(DataFormatError):
        #     StorageTank("storage-tank", connections={"this is": ["very", "wrong"]})

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
