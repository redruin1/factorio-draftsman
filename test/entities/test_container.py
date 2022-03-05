# test_container.py

from draftsman.entity import Container, containers, Splitter
from draftsman.errors import (
    InvalidEntityID, InvalidWireType, InvalidConnectionSide, 
    EntityNotCircuitConnectable
)

from schema import SchemaError

from unittest import TestCase
import warnings

class ContainerTesting(TestCase):
    def test_default_constructor(self):
        default_container = Container()
        hw = default_container.tile_width / 2.0
        hh = default_container.tile_height / 2.0
        self.assertEqual(
            default_container.to_dict(),
            {
                "name": containers[0],
                "position": {"x": hw, "y": hh}
            }
        )

    def test_constructor_init(self):
        wooden_chest = Container("wooden-chest", 
            position = [15, 3], bar = 5, 
            connections = {
                "1": {
                    "red": [
                        {"entity_id": "another_entity"},
                        {"entity_id": 2, "circuit_id": 1}
                    ]
                }
            })
        self.assertEqual(
            wooden_chest.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 15.5, "y": 3.5},
                "bar": 5,
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
        wooden_chest = Container("wooden-chest", 
            position = {"x": 15.5, "y": 1.5}, bar = 5,
            tags = {
                "A": "B"
            }
        )
        self.assertEqual(
            wooden_chest.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {
                    "A": "B"
                }
            }
        )
        # Warnings
        with self.assertWarns(UserWarning):
            Container("wooden-chest", 
                position = [0, 0], invalid_keyword = "100"
            )
        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityID):
            Container("this is not a container")
        
        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(SchemaError):
            Container("wooden-chest", id = 25)

        with self.assertRaises(SchemaError):
            Container("wooden-chest", position = "invalid")

        with self.assertRaises(SchemaError):
            Container("wooden-chest", bar = "not even trying")

        with self.assertRaises(SchemaError):
            Container("wooden-chest", 
                connections = {
                    "this is": ["very", "wrong"]
                }
            )

    def test_power_and_circuit_flags(self):
        for container_name in containers:
            container = Container(container_name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)

    # def test_dimensions(self):
    #     for container_name in containers:
    #         container = Container(container_name)
    #         self.assertEqual(container.tile_width, 1)
    #         self.assertEqual(container.tile_height, 1)

    def test_inventory_sizes(self):
        self.assertEqual(Container("wooden-chest").inventory_size, 16)
        self.assertEqual(Container("iron-chest").inventory_size,   32)
        self.assertEqual(Container("steel-chest").inventory_size,  48)