# test_logistic_request_container.py

from draftsman.entity import LogisticRequestContainer, logistic_request_containers
from draftsman.errors import InvalidEntityID

from schema import SchemaError

from unittest import TestCase

class LogisticRequestContainerTesting(TestCase):
    def test_default_constructor(self):
        request_chest = LogisticRequestContainer()
        hw = request_chest.width / 2.0
        hh = request_chest.height / 2.0
        self.assertEqual(
            request_chest.to_dict(),
            {
                "name": logistic_request_containers[0],
                "position": {"x": hw, "y": hh}
            }
        )

    def test_constructor_init(self):
        request_chest = LogisticRequestContainer("logistic-chest-requester", 
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
            request_chest.to_dict(),
            {
                "name": "logistic-chest-requester",
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
        request_chest = LogisticRequestContainer("logistic-chest-requester", 
            position = {"x": 15.5, "y": 1.5}, bar = 5,
            tags = {
                "A": "B"
            }
        )
        self.assertEqual(
            request_chest.to_dict(),
            {
                "name": "logistic-chest-requester",
                "position": {"x": 15.5, "y": 1.5},
                "bar": 5,
                "tags": {
                    "A": "B"
                }
            }
        )

        request_chest = LogisticRequestContainer(
            request_from_buffers = True,
            request_filters = [
                ("iron-ore", 100)
            ]
        )
        self.assertEqual(
            request_chest.to_dict(),
            {
                "name": "logistic-chest-requester",
                "position": {"x": 0.5, "y": 0.5},
                "request_from_buffers": True,
                "request_filters": [
                    {"index": 1, "name": "iron-ore", "count": 100}
                ]
            }
        )
        # TODO
        # storage_chest = LogisticStorageContainer(
        #     request_filters = [
        #         {"index": 1, "name": "iron-ore", "count": 100}
        #     ]
        # )

        # Warnings
        with self.assertWarns(UserWarning):
            LogisticRequestContainer("logistic-chest-requester", 
                position = [0, 0], invalid_keyword = "100"
            )
        
        # Errors
        # Raises InvalidEntityID when not in containers
        with self.assertRaises(InvalidEntityID):
            LogisticRequestContainer("this is not a logistics storage chest")
        
        # Raises schema errors when any of the associated data is incorrect
        with self.assertRaises(SchemaError):
            LogisticRequestContainer("logistic-chest-requester", id = 25)

        with self.assertRaises(SchemaError):
            LogisticRequestContainer("logistic-chest-requester", position = "invalid")

        with self.assertRaises(SchemaError):
            LogisticRequestContainer("logistic-chest-requester", bar = "not even trying")

        with self.assertRaises(SchemaError):
            LogisticRequestContainer("logistic-chest-requester", 
                connections = {
                    "this is": ["very", "wrong"]
                }
            )

        with self.assertRaises(SchemaError):
            LogisticRequestContainer("logistic-chest-requester", 
                request_filters = {
                    "this is": ["very", "wrong"]
                }
            )

        with self.assertRaises(SchemaError):
            LogisticRequestContainer("logistic-chest-requester", 
                request_from_buffers = "invalid"
            )

    def test_power_and_circuit_flags(self):
        for name in logistic_request_containers:
            container = LogisticRequestContainer(name)
            self.assertEqual(container.power_connectable, False)
            self.assertEqual(container.dual_power_connectable, False)
            self.assertEqual(container.circuit_connectable, True)
            self.assertEqual(container.dual_circuit_connectable, False)

    def test_dimensions(self):
        for name in logistic_request_containers:
            container = LogisticRequestContainer(name)
            self.assertEqual(container.width, 1)
            self.assertEqual(container.height, 1)