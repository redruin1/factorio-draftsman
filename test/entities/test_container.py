# test_container.py

from draftsman.entity import Container, containers, Splitter
from draftsman.error import (
    InvalidEntityError, InvalidWireTypeError, InvalidConnectionSideError, 
    EntityNotCircuitConnectableError
)
from draftsman.warning import DraftsmanWarning

from unittest import TestCase
import warnings


class ContainerTesting(TestCase):
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
        with self.assertWarns(DraftsmanWarning):
            Container("wooden-chest", 
                position = [0, 0], invalid_keyword = "100"
            )
        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            Container("this is not a container")
        
        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            Container("wooden-chest", id = 25)

        with self.assertRaises(TypeError):
            Container("wooden-chest", position = "invalid")

        with self.assertRaises(TypeError):
            Container("wooden-chest", bar = "not even trying")

        with self.assertRaises(TypeError):
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