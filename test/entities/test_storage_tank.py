# test_storagetank.py

from draftsman.constants import Direction
from draftsman.entity import StorageTank, storage_tanks
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

from unittest import TestCase
import warnings

warnings.filterwarnings("error")

class StorageTankTesting(TestCase):
    def test_constructor_init(self):
        storage_tank = StorageTank("storage-tank", 
            position = [15, 3], direction = Direction.NORTH,
            connections = {
                "1": {
                    "red": [
                        {"entity_id": "another_entity"},
                        {"entity_id": 2, "circuit_id": 1}
                    ]
                }
            })
        self.assertEqual(
            storage_tank.to_dict(),
            {
                "name": "storage-tank",
                "position": {"x": 16.5, "y": 4.5},
                # "direction": 0, # not here because 0 is the default direction
                "connections": {
                    "1": {
                        "red": [
                            {"entity_id": "another_entity"},
                            {"entity_id": 2, "circuit_id": 1}
                        ]
                    }
                }
            }
        )
        storage_tank = StorageTank("storage-tank", 
            position = {"x": 16.5, "y": 4.5}, direction = Direction.EAST,
            tags = {
                "A": "B"
            }
        )
        self.assertEqual(
            storage_tank.to_dict(),
            {
                "name": "storage-tank",
                "position": {"x": 16.5, "y": 4.5},
                "direction": 2,
                "tags": {
                    "A": "B"
                }
            }
        )
        # Warnings
        with self.assertWarns(DraftsmanWarning):
            StorageTank(
                position = [0, 0], direction = Direction.WEST, invalid_keyword = 5
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            StorageTank("this is not a storage tank")

        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(SchemaError):
            StorageTank("storage-tank", id = 25)

        with self.assertRaises(SchemaError):
            StorageTank("storage-tank", position = "invalid")
        
        with self.assertRaises(SchemaError):
            StorageTank("storage-tank", direction = "incorrect")

        with self.assertRaises(SchemaError):
            StorageTank(
                "storage-tank",
                connections = {
                    "this is": ["very", "wrong"]
                }
            )

    def test_power_and_circuit_flags(self):
        for storage_tank_name in storage_tanks:
            container = StorageTank(storage_tank_name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)