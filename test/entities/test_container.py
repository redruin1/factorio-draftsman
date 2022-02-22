# test_container.py

from draftsman.entity import Container, containers
from draftsman.errors import (
    InvalidEntityID, InvalidWireType, InvalidConnectionSide
)

from schema import SchemaError

from unittest import TestCase
import warnings

class ContainerTesting(TestCase):
    def test_default_constructor(self):
        default_container = Container()
        hw = default_container.width / 2.0
        hh = default_container.height / 2.0
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
        # Errors
        # Raises InvalidEntityID when not in containers
        self.assertRaises(
            InvalidEntityID,
            Container,
            "this is not a container"
        )
        # Raises schema errors when any of the associated data is incorrect
        self.assertRaises(
            SchemaError,
            Container,
            "wooden-chest", id = 25
        )
        self.assertRaises(
            SchemaError,
            Container,
            "wooden-chest", position = "invalid"
        )
        self.assertRaises(
            SchemaError,
            Container,
            "wooden-chest", bar = "not even trying"
        )
        self.assertRaises(
            SchemaError,
            Container,
            "wooden-chest", connections = {
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

    def test_dimensions(self):
        for container_name in containers:
            container = Container(container_name)
            self.assertEqual(container.width, 1)
            self.assertEqual(container.height, 1)

    def test_inventory_sizes(self):
        self.assertEqual(Container("wooden-chest").inventory_size, 16)
        self.assertEqual(Container("iron-chest").inventory_size,   32)
        self.assertEqual(Container("steel-chest").inventory_size,  48)

    def test_set_position(self):
        iron_chest = Container("iron-chest")
        iron_chest.set_absolute_position(1.23, 1.34)
        self.assertAlmostEqual(iron_chest.position, {"x": 1.23, "y": 1.34})
        self.assertEqual(iron_chest.grid_position, [1, 1])

        self.assertRaises(
            SchemaError,
            iron_chest.set_absolute_position,
            "fish", 10
        )

        iron_chest.set_grid_position(10, 10.1) # should cast float to int
        self.assertEqual(iron_chest.grid_position, [10, 10])
        self.assertAlmostEqual(iron_chest.position, {"x": 10.5, "y": 10.5})

        self.assertRaises(
            SchemaError,
            iron_chest.set_grid_position,
            1.0, "raw-fish"
        )

    def test_bar_index(self):
        wooden_chest = Container("wooden-chest")
        with warnings.catch_warnings(record = True) as w:
            for i in range(wooden_chest.inventory_size + 1):
                wooden_chest.set_bar_index(i)
            # Check to make sure 1 warning was issued
            self.assertEqual(len(w), 1)
            self.assertEqual(str(w[-1].message), "Bar index not in range [0, 16)")

        iron_chest = Container("iron-chest")
        with warnings.catch_warnings(record = True) as w:
            for i in range(iron_chest.inventory_size + 1):
                iron_chest.set_bar_index(i)
            # Check to make sure 1 warning was issued
            self.assertEqual(len(w), 1)
            self.assertEqual(str(w[-1].message), "Bar index not in range [0, 32)")

        steel_chest = Container("steel-chest")
        with warnings.catch_warnings(record = True) as w:
            for i in range(steel_chest.inventory_size + 1):
                steel_chest.set_bar_index(i)
            # Check to make sure 1 warning was issued
            self.assertEqual(len(w), 1)
            self.assertEqual(str(w[-1].message), "Bar index not in range [0, 48)")

        # Try self.assertRaises
        self.assertRaises(
            SchemaError, 
            steel_chest.set_bar_index, 
            "lmao a string! Who'd do such a dastardly thing????"
        )

    def test_circuit_connection(self):
        container1 = Container("steel-chest", id = "c1", position = [-1, 0])
        container2 = Container("steel-chest", id = "c2", position = [ 1, 0])

        # Redundant, thats what the constructor uses
        #container.set_connections()

        # When writing entity connections, I want each function to only modify
        # the calling entity; this means in order to setup a "normal" connection
        # you have to call the function twice, once to connect entity A to 
        # entity B and again to connect entity B to entity A:
        container1.add_circuit_connection("red", container2)
        container2.add_circuit_connection("red", container1)
        # Note that this connection cannot be realized unless put into a 
        # `Blueprint` object, as each entity has no knowledge of what the id's 
        # of other entities are.
        # Also note that its impossible to set an entity to connect to an int 
        # `entity_number` instead of a string `id`. It wouldn't make much sense
        # anyway; how do you figure out the `entity_number` of an entity that 
        # currently isn't in any blueprint?
        # Warnings
        with warnings.catch_warnings(record = True) as w:
            container1.add_circuit_connection("green", container2, 1, 2)
            container2.add_circuit_connection("green", container1, 2, 1)
            self.assertEqual(len(w), 2)
            self.assertEqual(
                str(w[0].message), 
                "'target_side' was specified as 2, but entity '<class 'draftsman.entity.Container'>' is not dual circuit connectable"
            )
            self.assertEqual(
                str(w[1].message),
                "'source_side' was specified as 2, but entity '<class 'draftsman.entity.Container'>' is not dual circuit connectable"
            )
        # Invalid
        self.assertRaises(
            InvalidWireType,
            container1.add_circuit_connection,
            "wrong", container2 
        )
        self.assertRaises(
            TypeError,
            container1.add_circuit_connection,
            "red", SchemaError
        )
        self.assertRaises(
            InvalidConnectionSide,
            container1.add_circuit_connection,
            "red", container2, "fish", "2"
        )