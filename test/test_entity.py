# entity.py

from draftsman.entity import *

from schema import SchemaError

from unittest import TestCase


class EntityTesting(TestCase):
    def test_set_tags(self):
        container = Container("wooden-chest")
        container.set_tags({"wee": 500, "hello": "world"})
        container.set_tag("addition", 1 + 1)

        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "tags": {
                    "wee": 500,
                    "hello": "world",
                    "addition": 2
                }
            }
        )

        # Removing by setting to None
        container.set_tag("addition", None)
        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "tags": {
                    "wee": 500,
                    "hello": "world",
                }
            }
        )

        # Remove non-existant key should do nothing
        container.set_tag("unknown", None)
        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "tags": {
                    "wee": 500,
                    "hello": "world",
                }
            }
        )

        # Resetting tags to empty should omit it based on its lambda func
        container.set_tags({})
        self.assertEqual(
            container.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
            }
        )

    def test_to_dict(self):
        class TestEntity(Entity):
            pass

        # TODO
        pass

    def test_set_position(self):
        iron_chest = Container("iron-chest")
        iron_chest.set_absolute_position(1.23, 1.34)
        self.assertAlmostEqual(iron_chest.position, {"x": 1.23, "y": 1.34})
        self.assertEqual(iron_chest.grid_position, [1, 1])

        with self.assertRaises(SchemaError):
            iron_chest.set_absolute_position("fish", 10)

        iron_chest.set_grid_position(10, 10.1) # should cast float to int
        self.assertEqual(iron_chest.grid_position, [10, 10])
        self.assertAlmostEqual(iron_chest.position, {"x": 10.5, "y": 10.5})

        with self.assertRaises(SchemaError):
            iron_chest.set_absolute_position(1.0, "raw-fish")

    def test_iter(self):
        container = Container("wooden-chest")
        values = dict()
        for key, value in container:
            values[key] = value

        values["exports"] = None # Make our lives easier

        self.assertEqual(
            values,
            {
                "exports": None,
                "name": "wooden-chest",
                "circuit_wire_max_distance": 9,
                "id": None,
                "width": 1,
                "height": 1,
                "power_connectable": False,
                "dual_power_connectable": False,
                "circuit_connectable": True,
                "dual_circuit_connectable": False,
                "double_grid_aligned": False,
                "position": {"x": 0.5, "y": 0.5},
                "grid_position": [0, 0],
                "tags": {},
                "inventory_size": 16,
                "bar": None,
                "unused_args": {},
                "connections": {}
            }
        )

    def test_repr(self):
        class TestEntity(Entity):
            pass

        test = TestEntity("loader")
        self.assertEqual(
            str(test),
            "<Entity>{'name': 'loader', 'position': {'x': 0.5, 'y': 1.0}}"
        )

    def test_get_aabb(self):
        # TODO: get the AABB of the entity so we can test if they overlap one
        # another when we get to blueprint
        pass

# =============================================================================
# Mixins (Alphabetical)
# =============================================================================

class CircuitConditionMixinTesting(TestCase):
    def test_set_enable_disable(self):
        transport_belt = TransportBelt()
        transport_belt.set_enable_disable(True)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_enable_disable": True
            }
        )

        transport_belt.set_enable_disable(None)
        self.assertEqual(transport_belt.control_behavior, {})

        with self.assertRaises(SchemaError):
            transport_belt.set_enable_disable("True")

    def test_set_enabled_condition(self):
        transport_belt = TransportBelt()
        # Valid
        transport_belt.set_enabled_condition(None)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "comparator": "<",
                    "constant": 0
                }
            }
        )
        transport_belt.set_enabled_condition("signal-A", ">", -10)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "comparator": ">",
                    "constant": -10
                }
            }
        )
        transport_belt.set_enabled_condition("signal-A", "<=", "signal-B")
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "comparator": "≤",
                    "second_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    }
                }
            }
        )
        transport_belt.set_enabled_condition("signal-A", "≤", "signal-B")
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "comparator": "≤",
                    "second_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    }
                }
            }
        )
        transport_belt.set_enabled_condition("signal-A", "!=", "signal-B")
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "comparator": "≠",
                    "second_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    }
                }
            }
        )

        # Errors
        # Constant first
        with self.assertRaises(SchemaError):
            transport_belt.set_enabled_condition(10, ">", "signal-B")
        # Invalid A
        with self.assertRaises(SchemaError):
            transport_belt.set_enabled_condition(TypeError, ">", "signal-B")
        # Invalid Operation
        with self.assertRaises(SchemaError):
            transport_belt.set_enabled_condition("signal-A", "hmm", "signal-B")
        # Invalid B
        with self.assertRaises(SchemaError):
            transport_belt.set_enabled_condition("signal-A", ">", TypeError)

    def test_remove_enabled_condition(self): # TODO delete
        transport_belt = TransportBelt()
        transport_belt.set_enabled_condition(None)
        transport_belt.remove_enabled_condition()
        self.assertEqual(
            transport_belt.control_behavior,
            {}
        )

    def test_normalize_circuit_condition(self): # TODO delete
        transport_belt = TransportBelt(control_behavior = {})
        self.assertEqual(
            transport_belt.to_dict(),
            {
                "name": "transport-belt",
                "position": {"x": 0.5, "y": 0.5},
            }
        )
        transport_belt = TransportBelt(
            control_behavior = {
                "circuit_condition": {}
            }
        )
        self.assertEqual(
            transport_belt.to_dict(),
            {
                "name": "transport-belt",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "circuit_condition": {}
                }
            }
        )
        transport_belt = TransportBelt(
            control_behavior = {
                "circuit_condition": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "second_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    }
                }
            }
        )
        self.assertEqual(
            transport_belt.to_dict(),
            {
                "name": "transport-belt",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {
                    "circuit_condition": {
                        "first_signal": {
                            "name": "signal-A",
                            "type": "virtual"
                        },
                        "second_signal": {
                            "name": "signal-B",
                            "type": "virtual"
                        }
                    }
                }
            }
        )

################################################################################

class CircuitConnectableMixinTesting(TestCase):
    def test_add_circuit_connection(self):
        container1 = Container("steel-chest", id = "c1", position = [-1, 0])
        container2 = Container("steel-chest", id = "c2", position = [ 1, 0])

        # Redundant, thats what the constructor uses
        #container.set_connections()

        # When writing entity connections, I want each function to only modify
        # the calling entity; this means in order to setup a "normal" connection
        # you have to call the function twice, once to connect entity A to 
        # entity B and again to connect entity B to entity A:
        container1.add_circuit_connection("red", container2)
        #container2.add_circuit_connection("red", container1)
        # Note that this connection cannot be realized unless put into a 
        # `Blueprint` object, as each entity has no knowledge of what the id's 
        # of other entities are.
        # Also note that its impossible to set an entity to connect to an int 
        # `entity_number` instead of a string `id`. It wouldn't make much sense
        # anyway; how do you figure out the `entity_number` of an entity that 
        # currently isn't in any blueprint?
        self.assertEqual(
            container1.to_dict(),
            {
                "name": "steel-chest",
                "position": {"x": -0.5, "y": 0.5},
                "connections": {
                    "1": {
                        "red": [
                            {"entity_id": "c2"}
                        ]
                    }
                }
            }
        )
        self.assertEqual(
            container2.to_dict(),
            {
                "name": "steel-chest",
                "position": {"x": 1.5, "y": 0.5},
                "connections": {
                    "1": {
                        "red": [
                            {"entity_id": "c1"}
                        ]
                    }
                }
            }
        )
        # Test duplicate connection
        container2.add_circuit_connection("red", container1)
        self.assertEqual(
            container1.to_dict(),
            {
                "name": "steel-chest",
                "position": {"x": -0.5, "y": 0.5},
                "connections": {
                    "1": {
                        "red": [
                            {"entity_id": "c2"}
                        ]
                    }
                }
            }
        )
        self.assertEqual(
            container2.to_dict(),
            {
                "name": "steel-chest",
                "position": {"x": 1.5, "y": 0.5},
                "connections": {
                    "1": {
                        "red": [
                            {"entity_id": "c1"}
                        ]
                    }
                }
            }
        )

        # set_connections to None
        container1.set_connections(None)
        self.assertEqual(container1.connections, {})

        # Test when the same side and color dict already exists
        container3 = Container(id = "test")
        container2.add_circuit_connection("red", container3)
        self.assertEqual(
            container2.to_dict(),
            {
                "name": "steel-chest",
                "position": {"x": 1.5, "y": 0.5},
                "connections": {
                    "1": {
                        "red": [
                            {"entity_id": "c1"},
                            {"entity_id": "test"}
                        ]
                    }
                }
            }
        )

        # Test multiple connection points
        arithmetic_combinator = ArithmeticCombinator(id = "a")
        decider_combinator = DeciderCombinator(id = "d")
        arithmetic_combinator.add_circuit_connection("green", arithmetic_combinator, 1, 2)
        decider_combinator.add_circuit_connection("red", arithmetic_combinator, 1, 2)
        self.assertEqual(
            arithmetic_combinator.connections,
            {
                "1": {
                    "green": [
                        {"entity_id": "a", "circuit_id": 2}
                    ]
                },
                "2": {
                    "green": [
                        {"entity_id": "a", "circuit_id": 1}
                    ],
                    "red": [
                        {"entity_id": "d", "circuit_id": 1}
                    ]
                }
            }
        )
        self.assertEqual(
            decider_combinator.connections,
            {
                "1": {
                    "red": [
                        {"entity_id": "a", "circuit_id": 2}
                    ]
                }
            }
        )
        

        # Warnings
        # Warn if source or target side is not 1 on entity that is not dual 
        # connectable
        with self.assertWarns(UserWarning):
            container1.add_circuit_connection("green", container2, 1, 2)
        with self.assertWarns(UserWarning):
            container2.add_circuit_connection("green", container1, 2, 1)
        # Warn if connection being made is over too long a distance
        with self.assertWarns(UserWarning):
            container4 = Container(position = [100, 100], id = "no error pls")
            container2.add_circuit_connection("green", container4)

        # Errors
        with self.assertRaises(InvalidWireType):
            container1.add_circuit_connection("wrong", container2)

        with self.assertRaises(TypeError):
            container1.add_circuit_connection("red", SchemaError)
        
        with self.assertRaises(ValueError):
            container_with_no_id = Container()
            container1.add_circuit_connection("red", container_with_no_id)

        with self.assertRaises(InvalidConnectionSide):
            container1.add_circuit_connection("red", container2, "fish", 2)
        with self.assertRaises(InvalidConnectionSide):
            container2.add_circuit_connection("red", container2, 2, "fish")

        with self.assertRaises(EntityNotCircuitConnectable):
            not_circuit_connectable = Splitter("fast-splitter", id = "no error pls")
            container1.add_circuit_connection("red", not_circuit_connectable)

    def test_remove_circuit_connection(self):
        container1 = Container(id = "testing1", position = [0, 0])
        container2 = Container(id = "testing2", position = [1, 0])

        # Null case
        container1.remove_circuit_connection("red", container2)
        self.assertEqual(
            container1.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
            }
        )
        self.assertEqual(
            container2.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 1.5, "y": 0.5},
            }
        )

        # Normal Operation
        container1.add_circuit_connection("red", container2)
        container2.add_circuit_connection("green", container1)
        container1.remove_circuit_connection("red", container2)
        self.assertEqual(
            container1.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "connections": {
                    "1": {
                        "green": [
                            {"entity_id": "testing2"}
                        ]
                    }
                }
            }
        )
        self.assertEqual(
            container2.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 1.5, "y": 0.5},
                "connections": {
                    "1": {
                        "green": [
                            {"entity_id": "testing1"}
                        ]
                    }
                }
            }
        )

        # Redundant operation
        container1.remove_circuit_connection("red", container1)
        self.assertEqual(
            container1.to_dict(),
            {
                "name": "wooden-chest",
                "position": {"x": 0.5, "y": 0.5},
                "connections": {
                    "1": {
                        "green": [
                            {"entity_id": "testing2"}
                        ]
                    }
                }
            }
        )
        # Test multiple connection points
        arithmetic_combinator = ArithmeticCombinator(id = "a")
        decider_combinator = DeciderCombinator(id = "d")
        constant_combinator = ConstantCombinator(id = "c")
        
        arithmetic_combinator.add_circuit_connection("green", decider_combinator)
        arithmetic_combinator.add_circuit_connection("green", decider_combinator, 1, 2)
        arithmetic_combinator.add_circuit_connection("green", arithmetic_combinator, 1, 2)
        arithmetic_combinator.add_circuit_connection("red", decider_combinator, 2, 1)
        arithmetic_combinator.add_circuit_connection("red", decider_combinator, 2, 2)
        constant_combinator.add_circuit_connection("red", decider_combinator, 1, 2)

        arithmetic_combinator.remove_circuit_connection("green", decider_combinator)
        arithmetic_combinator.remove_circuit_connection("green", decider_combinator, 1, 2)
        arithmetic_combinator.remove_circuit_connection("green", arithmetic_combinator, 1, 2)
        arithmetic_combinator.remove_circuit_connection("red", decider_combinator, 2, 1)
        arithmetic_combinator.remove_circuit_connection("red", decider_combinator, 2, 2)

        self.assertEqual(
            arithmetic_combinator.connections,
            {}
        )
        self.assertEqual(
            decider_combinator.connections,
            {
                "2": {
                    "red": [
                        {"entity_id": "c"}
                    ]
                }
            }
        )
        self.assertEqual(
            constant_combinator.connections,
            {
                "1": {
                    "red": [
                        {"entity_id": "d", "circuit_id": 2}
                    ]
                }
            }
        )

        # Errors
        with self.assertRaises(InvalidWireType):
            container1.remove_circuit_connection("wrong", container2)

        with self.assertRaises(TypeError):
            container1.remove_circuit_connection("red", SchemaError)
        
        with self.assertRaises(ValueError):
            container_with_no_id = Container()
            container1.remove_circuit_connection("red", container_with_no_id)

        with self.assertRaises(InvalidConnectionSide):
            container1.remove_circuit_connection("red", container2, "fish", 2)
        with self.assertRaises(InvalidConnectionSide):
            container2.remove_circuit_connection("red", container2, 2, "fish")

################################################################################

class CircuitReadContentsMixinTesting(TestCase):
    def test_set_read_contents(self):
        transport_belt = TransportBelt()
        transport_belt.set_read_contents(True)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_read_hand_contents": True
            }
        )
        transport_belt.set_read_contents(None)
        self.assertEqual(transport_belt.control_behavior, {})

        with self.assertRaises(TypeError):
            transport_belt.set_read_contents("wrong")

    def test_set_read_mode(self):
        transport_belt = TransportBelt()
        transport_belt.set_read_mode(ReadMode.HOLD)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_contents_read_mode": 1
            }
        )
        transport_belt.set_read_mode(None)
        self.assertEqual(transport_belt.control_behavior, {})

        with self.assertRaises(TypeError):
            transport_belt.set_read_mode("wrong")

################################################################################

class CircuitReadHandMixinTesting(TestCase):
    def test_set_read_contents(self):
        inserter = Inserter()
        inserter.set_read_hand_contents(True)
        self.assertEqual(
            inserter.control_behavior,
            {
                "circuit_read_hand_contents": True
            }
        )
        inserter.set_read_hand_contents(None)
        self.assertEqual(inserter.control_behavior, {})

        with self.assertRaises(TypeError):
            inserter.set_read_hand_contents("wrong")

    def test_set_read_mode(self):
        inserter = Inserter()
        inserter.set_read_mode(ReadMode.HOLD)
        self.assertEqual(
            inserter.control_behavior,
            {
                "circuit_hand_read_mode": 1
            }
        )
        inserter.set_read_mode(None)
        self.assertEqual(inserter.control_behavior, {})

        with self.assertRaises(TypeError):
            inserter.set_read_mode("wrong")

################################################################################

class CircuitReadResourceMixinTesting(TestCase):
    def test_set_read_resources(self):
        pass

    def test_set_read_mode(self):
        pass

################################################################################

class ColorMixinTesting(TestCase):
    def test_set_color(self):
        train_stop = TrainStop()
        # Valid 4 args
        train_stop.set_color(0.1, 0.1, 0.1, 0.1)
        self.assertEqual(
            train_stop.color,
            {"r": 0.1, "g": 0.1, "b": 0.1, "a": 0.1}
        )
        # Valid 3 args
        train_stop.set_color(0.1, 0.1, 0.1)
        self.assertEqual(
            train_stop.color,
            {"r": 0.1, "g": 0.1, "b": 0.1, "a": 1.0}
        )
        # None
        train_stop.remove_color()
        self.assertEqual(
            train_stop.color,
            None
        )

        with self.assertRaises(SchemaError):
            train_stop.set_color("wrong", 1.0, 1.0)


################################################################################

class ControlBehaviorMixinTesting(TestCase):
    def test_set_control_behavior(self):
        pass # unnecessary?

################################################################################

class DirectionalMixinTesting(TestCase):
    def test_set_direction(self):
        storage_tank = StorageTank()
        storage_tank.set_direction(Direction.SOUTH)
        self.assertEqual(
            storage_tank.to_dict(),
            {
                "name": "storage-tank",
                "position": {"x": 1.5, "y": 1.5},
                "direction": 4
            }
        )
        # Default testing
        storage_tank.set_direction(Direction.NORTH)
        self.assertEqual(
            storage_tank.to_dict(),
            {
                "name": "storage-tank",
                "position": {"x": 1.5, "y": 1.5},
            }
        )
        # Warnings
        with self.assertWarns(UserWarning):
            storage_tank.set_direction(Direction.NORTHEAST)
        # Errors
        with self.assertRaises(SchemaError):
            storage_tank.set_direction("1000")

    def test_set_position(self):
        storage_tank = StorageTank()
        storage_tank.set_absolute_position(1.23, 1.34)
        self.assertEqual(storage_tank.position, {"x": 1.23, "y": 1.34})
        self.assertEqual(storage_tank.grid_position, [0, 0])

        with self.assertRaises(SchemaError):
            storage_tank.set_absolute_position("fish", 10)

        storage_tank.set_grid_position(10, 10.1) # should cast float to int
        self.assertEqual(storage_tank.grid_position, [10, 10])
        self.assertEqual(storage_tank.position, {"x": 11.5, "y": 11.5})

        with self.assertRaises(SchemaError):
            storage_tank.set_absolute_position(1.0, "raw-fish")

################################################################################

class DoubleGridAlignedMixinTesting(TestCase):
    pass

################################################################################

class EightWayDirectionalMixinTesting(TestCase):
    def test_set_direction(self):
        pass

################################################################################

class FiltersMixinTesting(TestCase):
    def test_set_item_filter(self):
        inserter = FilterInserter()

        inserter.set_item_filter(0, "small-lamp")
        self.assertEqual(
            inserter.filters,
            [
                {"index": 1, "name": "small-lamp"}
            ]
        )
        inserter.set_item_filter(1, "burner-inserter")
        self.assertEqual(
            inserter.filters,
            [
                {"index": 1, "name": "small-lamp"}, 
                {"index": 2, "name": "burner-inserter"}
            ]
        )

        inserter.set_item_filter(0, "fast-transport-belt")
        self.assertEqual(
            inserter.filters,
            [
                {"index": 1, "name": "fast-transport-belt"}, 
                {"index": 2, "name": "burner-inserter"}
            ]
        )

        inserter.set_item_filter(0, None)
        self.assertEqual(
            inserter.filters,
            [ 
                {"index": 2, "name": "burner-inserter"}
            ]
        )

        # Warnings
        # with self.assertWarns(UserWarning):
        #     inserter.set_item_filter(100, "small-lamp")

        # Errors
        with self.assertRaises(InvalidItemID):
            inserter.set_item_filter(0, "incorrect")

    def test_set_item_filters(self):
        inserter = FilterInserter()

        inserter.set_item_filters(
            ["transport-belt", "fast-transport-belt", "express-transport-belt"]
        )
        self.assertEqual(
            inserter.filters,
            [
                {"index": 1, "name": "transport-belt"},
                {"index": 2, "name": "fast-transport-belt"},
                {"index": 3, "name": "express-transport-belt"},
            ]
        )
        
        inserter.set_item_filters(
            [
                {"index": 1, "name": "transport-belt"},
                {"index": 2, "name": "fast-transport-belt"},
                {"index": 3, "name": "express-transport-belt"}
            ]
        )
        self.assertEqual(
            inserter.filters,
            [
                {"index": 1, "name": "transport-belt"},
                {"index": 2, "name": "fast-transport-belt"},
                {"index": 3, "name": "express-transport-belt"},
            ]
        )

        inserter.set_item_filters(None)
        self.assertEqual(inserter.filters, None)

        # Warnings
        # Outside of index range
        # with self.assertWarns(UserWarning):
        #     inserter.set_item_filters(
        #         {"index": 1, "name": "transport-belt"},
        #         {"index": 100, "name": "fast-transport-belt"},
        #         {"index": 3, "name": "express-transport-belt"}
        #     )

        # Errors
        with self.assertRaises(InvalidItemID):
            inserter.set_item_filters(
                ["transport-belt", "incorrect", "express-transport-belt"]
            )
        
        with self.assertRaises(InvalidItemID):
            inserter.set_item_filters(
                [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "incorrect"},
                    {"index": 3, "name": "express-transport-belt"}
                ]
            )
        


################################################################################

class InfinitySettingsMixinTesting(TestCase):
    def test_set_infinity_settings(self):
        pass

################################################################################

class InventoryMixinTesting(TestCase):
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

################################################################################

class InventoryFilterMixinTesting(TestCase):
    def test_set_inventory_filter(self):
        cargo_wagon = CargoWagon()
        cargo_wagon.set_inventory_filter(0, "transport-belt")
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "transport-belt"}
                ]
            }
        )
        cargo_wagon.set_inventory_filter(1, "fast-transport-belt")
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "fast-transport-belt"}
                ]
            }
        )
        cargo_wagon.set_inventory_filter(0, "express-transport-belt")
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "express-transport-belt"},
                    {"index": 2, "name": "fast-transport-belt"}
                ]
            }
        )
        cargo_wagon.set_inventory_filter(0, None)
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 2, "name": "fast-transport-belt"}
                ]
            }
        )

        # Warnings
        # Warn when filter index outside of wagon size
        # with self.assertWarns(UserWarning):
        #     cargo_wagon.set_inventory_filter(1000, "stone")

        # Errors
        with self.assertRaises(SchemaError):
            cargo_wagon.set_inventory_filter("double", "incorrect")
        with self.assertRaises(InvalidItemID):
            cargo_wagon.set_inventory_filter(0, "incorrect")

    def test_set_inventory_filters(self):
        cargo_wagon = CargoWagon()
        cargo_wagon.set_inventory_filters(["transport-belt", "fast-transport-belt"])
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "fast-transport-belt"}
                ]
            }
        )
        cargo_wagon.set_inventory_filters([
            {"index": 1, "name": "express-transport-belt"},
            {"index": 2, "name": "fast-transport-belt"}
        ])
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "express-transport-belt"},
                    {"index": 2, "name": "fast-transport-belt"}
                ]
            }
        )
        cargo_wagon.set_inventory_filters(None)
        self.assertEqual(cargo_wagon.inventory, {})

        # Warnings
        # Warn if index is out of range
        # TODO

        # Errors
        with self.assertRaises(InvalidItemID):
            cargo_wagon.set_inventory_filters(["incorrect1", "incorrect2"])

    def test_set_bar_index(self):
        cargo_wagon = CargoWagon()
        cargo_wagon.set_bar_index(10)
        self.assertEqual(
            cargo_wagon.inventory,
            {"bar": 10}
        )
        cargo_wagon.set_bar_index(None)
        self.assertEqual(cargo_wagon.inventory, {})

        # Warnings
        # Out of index range warning
        with self.assertWarns(UserWarning):
            cargo_wagon.set_bar_index(100)

        # Errors
        with self.assertRaises(SchemaError):
            cargo_wagon.set_bar_index("incorrect")

################################################################################

class IOTypeMixinTesting(TestCase):
    def test_set_io_type(self):
        pass # unnecessary?

################################################################################

class LogisticConditionMixinTesting(TestCase):
    def test_connect_to_logistic_network(self):
        transport_belt = TransportBelt()
        transport_belt.set_connect_to_logistic_network(True)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "connect_to_logistic_network": True
            }
        )

        transport_belt.set_connect_to_logistic_network(None)
        self.assertEqual(transport_belt.control_behavior, {})

        with self.assertRaises(TypeError):
            transport_belt.set_connect_to_logistic_network("True")

    def test_set_logistic_condition(self):
        transport_belt = TransportBelt()
        # Valid
        transport_belt.set_logistic_condition(None)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "logistic_condition": {
                    "comparator": "<",
                    "constant": 0
                }
            }
        )
        transport_belt.set_logistic_condition("signal-A", ">", -10)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "logistic_condition": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "comparator": ">",
                    "constant": -10
                }
            }
        )
        transport_belt.set_logistic_condition("signal-A", "<=", "signal-B")
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "logistic_condition": {
                    "first_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "comparator": "≤",
                    "second_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    }
                }
            }
        )

        # Errors
        # Constant first
        with self.assertRaises(SchemaError):
            transport_belt.set_logistic_condition(10, ">", "signal-B")
        # Invalid A
        with self.assertRaises(SchemaError):
            transport_belt.set_logistic_condition(TypeError, ">", "signal-B")
        # Invalid Operation
        with self.assertRaises(SchemaError):
            transport_belt.set_logistic_condition("signal-A", "hmm", "signal-B")
        # Invalid B
        with self.assertRaises(SchemaError):
            transport_belt.set_logistic_condition("signal-A", ">", TypeError)

    def test_remove_logistic_condition(self): # TODO delete
        transport_belt = TransportBelt()
        transport_belt.set_logistic_condition(None)
        transport_belt.remove_logistic_condition()
        self.assertEqual(
            transport_belt.control_behavior,
            {}
        )

################################################################################

class ModeOfOperationMixinTesting(TestCase):
    def test_set_mode_of_operation(self):
        inserter = Inserter()
        inserter.set_mode_of_operation(None)
        self.assertEqual(
            inserter.control_behavior,
            {}
        )
        inserter.set_mode_of_operation(ModeOfOperation.ENABLE_DISABLE)
        self.assertEqual(
            inserter.control_behavior,
            {}
        )
        inserter.set_mode_of_operation(ModeOfOperation.NONE)
        self.assertEqual(
            inserter.control_behavior,
            {
                "circuit_mode_of_operation": ModeOfOperation.NONE
            }
        )
        # Errors
        with self.assertRaises(TypeError):
            inserter.set_mode_of_operation("wrong")


################################################################################

class OrientationMixinTesting(TestCase):
    def test_set_orientation(self):
        locomotive = Locomotive()
        locomotive.set_orientation(0.25)
        self.assertEqual(
            locomotive.to_dict(),
            {
                "name": "locomotive",
                "position": {"x": 1.0, "y": 3.0},
                "orientation": 0.25
            }
        )
        locomotive.set_orientation(None)
        self.assertEqual(locomotive.orientation, None)
        with self.assertRaises(SchemaError):
            locomotive.set_orientation("incorrect")


################################################################################

class PowerConnectableMixinTesting(TestCase):
    def test_add_power_connection(self):
        substation1 = ElectricPole("substation", id = "1")
        substation2 = ElectricPole("substation", id = "2")
        power_switch = PowerSwitch(id = "p")

        substation1.add_power_connection(substation2)
        self.assertEqual(substation1.neighbours, ["2"])
        self.assertEqual(substation2.neighbours, ["1"])
        substation2.add_power_connection(substation1)
        self.assertEqual(substation1.neighbours, ["2"])
        self.assertEqual(substation2.neighbours, ["1"])

        substation1.add_power_connection(power_switch)
        self.assertEqual(substation1.neighbours, ["2"])
        self.assertEqual(
            power_switch.connections, 
            {
                "Cu0": [
                    {"entity_id": "1", "wire_id": 0}
                ]
            }
        )
        power_switch.add_power_connection(substation1)
        self.assertEqual(substation1.neighbours, ["2"])
        self.assertEqual(
            power_switch.connections, 
            {
                "Cu0": [
                    {"entity_id": "1", "wire_id": 0}
                ]
            }
        )
        substation2.add_power_connection(power_switch)
        substation2.add_power_connection(power_switch)
        self.assertEqual(substation2.neighbours, ["1"])
        self.assertEqual(
            power_switch.connections, 
            {
                "Cu0": [
                    {"entity_id": "1", "wire_id": 0},
                    {"entity_id": "2", "wire_id": 0}
                ]
            }
        )
        power_switch.add_power_connection(substation2, side = 2)
        self.assertEqual(
            power_switch.connections, 
            {
                "Cu0": [
                    {"entity_id": "1", "wire_id": 0},
                    {"entity_id": "2", "wire_id": 0}
                ],
                "Cu1": [
                    {"entity_id": "2", "wire_id": 0}
                ]
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            other = ElectricPole(position = [100, 0], id = "other")
            substation1.add_power_connection(other)

        # Errors
        with self.assertRaises(EntityNotPowerConnectable):
            substation1.add_power_connection(TransportBelt(id = "whatever"))
        with self.assertRaises(Exception):
            power_switch.add_power_connection(PowerSwitch())

        # Make sure correct even after errors
        self.assertEqual(substation1.neighbours, ["2", "other"])
        self.assertEqual(
            power_switch.connections, 
            {
                "Cu0": [
                    {"entity_id": "1", "wire_id": 0},
                    {"entity_id": "2", "wire_id": 0}
                ],
                "Cu1": [
                    {"entity_id": "2", "wire_id": 0}
                ]
            }
        )

        # Test removing
        substation1.remove_power_connection(substation2)
        substation1.remove_power_connection(substation2)
        self.assertEqual(substation1.neighbours, ["other"])
        self.assertEqual(substation2.neighbours, [])

        substation1.remove_power_connection(power_switch)
        substation1.remove_power_connection(power_switch)
        self.assertEqual(substation1.neighbours, ["other"])
        self.assertEqual(
            power_switch.connections, 
            {
                "Cu0": [
                    {"entity_id": "2", "wire_id": 0}
                ],
                "Cu1": [
                    {"entity_id": "2", "wire_id": 0}
                ]
            }
        )

        substation1.add_power_connection(power_switch)
        power_switch.remove_power_connection(substation2, side = 1)
        power_switch.remove_power_connection(substation2, side = 1)
        power_switch.remove_power_connection(substation1)
        power_switch.remove_power_connection(substation1)
        self.assertEqual(
            power_switch.connections, 
            {
                "Cu1": [
                    {"entity_id": "2", "wire_id": 0}
                ]
            }
        )
        substation2.remove_power_connection(power_switch, side = 2)
        substation2.remove_power_connection(power_switch, side = 2)
        self.assertEqual(power_switch.connections, {})

################################################################################

class ReadRailSignalMixinTesting(TestCase):
    def test_set_output_signals(self):
        rail_signal = RailSignal()
        rail_signal.set_red_output_signal("signal-A")
        self.assertEqual(
            rail_signal.control_behavior,
            {
                "red_output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )
        rail_signal.set_red_output_signal(None)
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(InvalidSignalID):
            rail_signal.set_red_output_signal("wrong")

        rail_signal.set_yellow_output_signal("signal-A")
        self.assertEqual(
            rail_signal.control_behavior,
            {
                "yellow_output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )
        rail_signal.set_yellow_output_signal(None)
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(InvalidSignalID):
            rail_signal.set_yellow_output_signal("wrong")

        rail_signal.set_green_output_signal("signal-A")
        self.assertEqual(
            rail_signal.control_behavior,
            {
                "green_output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )
        rail_signal.set_green_output_signal(None)
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(InvalidSignalID):
            rail_signal.set_green_output_signal("wrong")

################################################################################

class RecipeMixinTesting(TestCase):
    def test_set_recipe(self):
        pass

################################################################################

class RequestFiltersMixinTesting(TestCase):
    def test_set_request_filter(self):
        storage_chest = LogisticStorageContainer()
        storage_chest.set_request_filter(0, "stone", 100)
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 1, "name": "stone", "count": 100}
            ]
        )
        storage_chest.set_request_filter(1, "copper-ore", 200)
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 1, "name": "stone", "count": 100},
                {"index": 2, "name": "copper-ore", "count": 200}
            ]
        )
        storage_chest.set_request_filter(0, "iron-ore", 1000)
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 1, "name": "iron-ore", "count": 1000},
                {"index": 2, "name": "copper-ore", "count": 200}
            ]
        )
        storage_chest.set_request_filter(0, None)
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 2, "name": "copper-ore", "count": 200}
            ]
        )
        # test default
        storage_chest.set_request_filter(2, "fast-transport-belt")
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 2, "name": "copper-ore", "count": 200},
                {"index": 3, "name": "fast-transport-belt", "count": 0}
            ]
        )

        # Warnings
        # TODO: warn if index out of range

        # Errors
        with self.assertRaises(SchemaError):
            storage_chest.set_request_filter("incorrect", "iron-ore", 100)
        with self.assertRaises(InvalidItemID):
            storage_chest.set_request_filter(1, "incorrect", 100)
        with self.assertRaises(SchemaError):
            storage_chest.set_request_filter(1, "iron-ore", "incorrect")

    def test_set_request_filters(self):
        storage_chest = LogisticStorageContainer()
        storage_chest.set_request_filters(
            [("iron-ore", 200), ("copper-ore", 1000), ("small-lamp", 50)]
        )
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 1, "name": "iron-ore", "count": 200},
                {"index": 2, "name": "copper-ore", "count": 1000},
                {"index": 3, "name": "small-lamp", "count": 50}
            ]
        )
        storage_chest.set_request_filters(
            [("iron-ore", 200)]
        )
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 1, "name": "iron-ore", "count": 200}
            ]
        )
        # Errors
        with self.assertRaises(InvalidItemID):
            storage_chest.set_request_filters(
                [("iron-ore", 200), ("incorrect", 100)]
            )
        # Make sure that filters are unchanged if command fails
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 1, "name": "iron-ore", "count": 200}
            ]
        )
        with self.assertRaises(SchemaError):
            storage_chest.set_request_filters("very wrong")

################################################################################

class RequestItemsMixinTesting(TestCase):
    def test_set_item_requests(self):
        pass

    def test_set_item_request(self):
        pass

    # def test_remove_item_request(self):
    #     pass

################################################################################

class StackSizeMixinTesting(TestCase):
    def test_set_stack_size_override(self):
        inserter = Inserter()
        inserter.set_stack_size_override(1)
        self.assertEqual(inserter.override_stack_size, 1)

        with self.assertRaises(SchemaError):
            inserter.set_stack_size_override("100,000")

    def test_set_circuit_stack_size_enabled(self):
        inserter = Inserter()
        inserter.set_circuit_stack_size_enabled(True)
        self.assertEqual(
            inserter.control_behavior,
            {
                "circuit_set_stack_size": True
            }
        )

        inserter.set_circuit_stack_size_enabled(None)
        self.assertEqual(inserter.control_behavior, {})

        with self.assertRaises(SchemaError):
            inserter.set_circuit_stack_size_enabled("incorrect")

    def test_set_stack_control_signal(self):
        inserter = Inserter()
        inserter.set_stack_control_signal("signal-A")
        self.assertEqual(
            inserter.control_behavior,
            {
                "stack_control_input_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )

        inserter.set_stack_control_signal(None)
        self.assertEqual(inserter.control_behavior, {})

        with self.assertRaises(InvalidSignalID):
            inserter.set_stack_control_signal("wrong_name_lol")

        with self.assertRaises(TypeError):
            inserter.set_stack_control_signal(TypeError)

# =============================================================================
# Factory function new_entity()
# =============================================================================

class EntityFactoryTesting(TestCase):
    def test_new_entity(self):
        self.assertIsInstance(
            new_entity("wooden-chest"),
            Container
        )
        self.assertIsInstance(
            new_entity("storage-tank"),
            StorageTank
        )
        self.assertIsInstance(
            new_entity("transport-belt"),
            TransportBelt
        )
        self.assertIsInstance(
            new_entity("underground-belt"),
            UndergroundBelt
        )
        self.assertIsInstance(
            new_entity("splitter"),
            Splitter
        )
        self.assertIsInstance(
            new_entity("burner-inserter"),
            Inserter
        )
        self.assertIsInstance(
            new_entity("filter-inserter"),
            FilterInserter
        )
        self.assertIsInstance(
            new_entity("loader"),
            Loader
        )
        self.assertIsInstance(
            new_entity("small-electric-pole"),
            ElectricPole
        )
        self.assertIsInstance(
            new_entity("pipe"),
            Pipe
        )
        self.assertIsInstance(
            new_entity("pipe-to-ground"),
            UndergroundPipe
        )
        self.assertIsInstance(
            new_entity("pump"),
            Pump
        )
        self.assertIsInstance(
            new_entity("straight-rail"),
            StraightRail
        )
        self.assertIsInstance(
            new_entity("curved-rail"),
            CurvedRail
        )
        self.assertIsInstance(
            new_entity("train-stop"),
            TrainStop
        )
        self.assertIsInstance(
            new_entity("rail-signal"),
            RailSignal
        )
        self.assertIsInstance(
            new_entity("rail-chain-signal"),
            RailChainSignal
        )
        self.assertIsInstance(
            new_entity("locomotive"),
            Locomotive
        )
        self.assertIsInstance(
            new_entity("cargo-wagon"),
            CargoWagon
        )
        self.assertIsInstance(
            new_entity("fluid-wagon"),
            FluidWagon
        )
        self.assertIsInstance(
            new_entity("artillery-wagon"),
            ArtilleryWagon
        )
        self.assertIsInstance(
            new_entity("logistic-chest-storage"),
            LogisticStorageContainer
        )
        self.assertIsInstance(
            new_entity("logistic-chest-buffer"),
            LogisticBufferContainer
        )
        self.assertIsInstance(
            new_entity("logistic-chest-requester"),
            LogisticRequestContainer
        )
        self.assertIsInstance(
            new_entity("roboport"),
            Roboport
        )
        self.assertIsInstance(
            new_entity("small-lamp"),
            Lamp
        )
        self.assertIsInstance(
            new_entity("arithmetic-combinator"),
            ArithmeticCombinator
        )
        self.assertIsInstance(
            new_entity("decider-combinator"),
            DeciderCombinator
        )
        self.assertIsInstance(
            new_entity("constant-combinator"),
            ConstantCombinator
        )
        self.assertIsInstance(
            new_entity("power-switch"),
            PowerSwitch
        )
        self.assertIsInstance(
            new_entity("programmable-speaker"),
            ProgrammableSpeaker
        )
        self.assertIsInstance(
            new_entity("boiler"),
            Boiler
        )
        self.assertIsInstance(
            new_entity("steam-engine"),
            Generator
        )
        self.assertIsInstance(
            new_entity("solar-panel"),
            SolarPanel
        )
        self.assertIsInstance(
            new_entity("accumulator"),
            Accumulator
        )
        self.assertIsInstance(
            new_entity("nuclear-reactor"),
            Reactor
        )
        self.assertIsInstance(
            new_entity("heat-pipe"),
            HeatPipe
        )
        self.assertIsInstance(
            new_entity("burner-mining-drill"),
            MiningDrill
        )
        self.assertIsInstance(
            new_entity("offshore-pump"),
            OffshorePump
        )
        self.assertIsInstance(
            new_entity("stone-furnace"),
            Furnace
        )
        self.assertIsInstance(
            new_entity("assembling-machine-1"),
            AssemblingMachine
        )
        self.assertIsInstance(
            new_entity("lab"),
            Lab
        )
        self.assertIsInstance(
            new_entity("beacon"),
            Beacon
        )
        self.assertIsInstance(
            new_entity("rocket-silo"),
            RocketSilo
        )
        self.assertIsInstance(
            new_entity("land-mine"),
            LandMine
        )
        self.assertIsInstance(
            new_entity("stone-wall"),
            Wall
        )
        self.assertIsInstance(
            new_entity("gate"),
            Gate
        )
        self.assertIsInstance(
            new_entity("gun-turret"),
            Turret
        )
        self.assertIsInstance(
            new_entity("radar"),
            Radar
        )
        self.assertIsInstance(
            new_entity("electric-energy-interface"),
            ElectricEnergyInterface
        )
        self.assertIsInstance(
            new_entity("linked-chest"),
            LinkedContainer
        )
        self.assertIsInstance(
            new_entity("heat-interface"),
            HeatInterface
        )
        self.assertIsInstance(
            new_entity("linked-belt"),
            LinkedBelt
        )
        self.assertIsInstance(
            new_entity("infinity-chest"),
            InfinityContainer
        )
        self.assertIsInstance(
            new_entity("infinity-pipe"),
            InfinityPipe
        )
        self.assertIsInstance(
            new_entity("burner-generator"),
            BurnerGenerator
        )

        self.assertRaises(
            InvalidEntityID,
            new_entity,
            "I have a lot of entities that I need to test..."
        )