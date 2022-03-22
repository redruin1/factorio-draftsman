# test_logistic_active_container.py

from draftsman.entity import LogisticActiveContainer, logistic_active_containers
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

from unittest import TestCase
import warnings

class ContainerTesting(TestCase):
    def test_constructor_init(self):
        active_chest = LogisticActiveContainer(
            "logistic-chest-active-provider", 
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
            active_chest.to_dict(),
            {
                "name": "logistic-chest-active-provider",
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
        active_chest = LogisticActiveContainer(
            "logistic-chest-active-provider", 
            position = {"x": 15.5, "y": 1.5}, bar = 5,
            tags = {
                "A": "B"
            }
        )
        self.assertEqual(
            active_chest.to_dict(),
            {
                "name": "logistic-chest-active-provider",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {
                    "A": "B"
                }
            }
        )
        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LogisticActiveContainer(
                "logistic-chest-active-provider", 
                position = [0, 0], 
                invalid_keyword = "100"
            )
        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityError):
            LogisticActiveContainer("this is not an active provider chest")
        
        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(TypeError):
            LogisticActiveContainer(
                "logistic-chest-active-provider", 
                id = 25
            )

        with self.assertRaises(TypeError):
            LogisticActiveContainer(
                "logistic-chest-active-provider", 
                position = "invalid"
            )

        with self.assertRaises(TypeError):
            LogisticActiveContainer(
                "logistic-chest-active-provider", 
                bar = "not even trying"
            )

        with self.assertRaises(TypeError):
            LogisticActiveContainer(
                "logistic-chest-active-provider", 
                connections = {
                    "this is": ["very", "wrong"]
                }
            )

    def test_power_and_circuit_flags(self):
        for container_name in logistic_active_containers:
            container = LogisticActiveContainer(container_name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)