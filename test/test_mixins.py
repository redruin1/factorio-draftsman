# test_mixins.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from tkinter import W

from draftsman.constants import *
from draftsman.entity import *
from draftsman.error import *
from draftsman.warning import *

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class CircuitConditionMixinTesting(unittest.TestCase):
    def test_set_enable_disable(self):
        transport_belt = TransportBelt()
        transport_belt.enable_disable = True
        self.assertEqual(transport_belt.enable_disable, True)
        self.assertEqual(
            transport_belt.control_behavior, {"circuit_enable_disable": True}
        )

        transport_belt.enable_disable = None
        self.assertEqual(transport_belt.control_behavior, {})

        with self.assertRaises(TypeError):
            transport_belt.enable_disable = "True"

    def test_set_circuit_condition(self):
        transport_belt = TransportBelt()
        # Valid
        transport_belt.set_circuit_condition(None)
        self.assertEqual(
            transport_belt.control_behavior,
            {"circuit_condition": {"comparator": "<", "constant": 0}},
        )
        transport_belt.set_circuit_condition("signal-A", ">", -10)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": ">",
                    "constant": -10,
                }
            },
        )
        transport_belt.set_circuit_condition("signal-A", "==", -10)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "constant": -10,
                }
            },
        )
        transport_belt.set_circuit_condition("signal-A", "<=", "signal-B")
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≤",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )
        transport_belt.set_circuit_condition("signal-A", "≤", "signal-B")
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≤",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )
        transport_belt.set_circuit_condition("signal-A", "!=", "signal-B")
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≠",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )

        # Errors
        # Constant first
        with self.assertRaises(DataFormatError):
            transport_belt.set_circuit_condition(10, ">", "signal-B")
        # Invalid A
        with self.assertRaises(DataFormatError):
            transport_belt.set_circuit_condition(TypeError, ">", "signal-B")
        # Invalid Operation
        with self.assertRaises(DataFormatError):
            transport_belt.set_circuit_condition("signal-A", "hmm", "signal-B")
        # Invalid B
        with self.assertRaises(DataFormatError):
            transport_belt.set_circuit_condition("signal-A", ">", TypeError)

    def test_remove_circuit_condition(self):  # TODO delete
        transport_belt = TransportBelt()
        transport_belt.set_circuit_condition(None)
        transport_belt.remove_circuit_condition()
        self.assertEqual(transport_belt.control_behavior, {})

    def test_normalize_circuit_condition(self):  # TODO delete
        transport_belt = TransportBelt(control_behavior={})
        self.assertEqual(
            transport_belt.to_dict(),
            {
                "name": "transport-belt",
                "position": {"x": 0.5, "y": 0.5},
            },
        )
        transport_belt = TransportBelt(control_behavior={"circuit_condition": {}})
        self.assertEqual(
            transport_belt.to_dict(),
            {
                "name": "transport-belt",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {"circuit_condition": {}},
            },
        )
        transport_belt = TransportBelt(
            control_behavior={
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "second_signal": {"name": "signal-B", "type": "virtual"},
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
                        "first_signal": {"name": "signal-A", "type": "virtual"},
                        "second_signal": {"name": "signal-B", "type": "virtual"},
                    }
                },
            },
        )


################################################################################


class CircuitConnectableMixinTesting(unittest.TestCase):
    pass


################################################################################


class CircuitReadContentsMixinTesting(unittest.TestCase):
    def test_set_read_contents(self):
        transport_belt = TransportBelt()
        transport_belt.read_contents = True
        self.assertEqual(transport_belt.read_contents, True)
        self.assertEqual(
            transport_belt.control_behavior, {"circuit_read_hand_contents": True}
        )
        transport_belt.read_contents = None
        self.assertEqual(transport_belt.control_behavior, {})

        with self.assertRaises(TypeError):
            transport_belt.read_contents = "wrong"

    def test_set_read_mode(self):
        transport_belt = TransportBelt()
        # transport_belt.set_read_mode(ReadMode.HOLD)
        transport_belt.read_mode = ReadMode.HOLD
        self.assertEqual(transport_belt.read_mode, ReadMode.HOLD)
        self.assertEqual(
            transport_belt.control_behavior, {"circuit_contents_read_mode": 1}
        )
        # transport_belt.set_read_mode(None)
        transport_belt.read_mode = None
        self.assertEqual(transport_belt.control_behavior, {})

        with self.assertRaises(ValueError):
            transport_belt.read_mode = "wrong"


################################################################################


class CircuitReadHandMixinTesting(unittest.TestCase):
    def test_set_read_contents(self):
        inserter = Inserter()
        inserter.read_hand_contents = True
        self.assertEqual(inserter.read_hand_contents, True)
        self.assertEqual(
            inserter.control_behavior, {"circuit_read_hand_contents": True}
        )
        inserter.read_hand_contents = None
        self.assertEqual(inserter.control_behavior, {})

        with self.assertRaises(TypeError):
            inserter.read_hand_contents = "wrong"

    def test_set_read_mode(self):
        inserter = Inserter()
        inserter.read_mode = ReadMode.HOLD
        self.assertEqual(inserter.read_mode, ReadMode.HOLD)
        self.assertEqual(inserter.control_behavior, {"circuit_hand_read_mode": 1})
        inserter.read_mode = None
        self.assertEqual(inserter.control_behavior, {})

        with self.assertRaises(ValueError):
            inserter.read_mode = "wrong"


################################################################################


class CircuitReadResourceMixinTesting(unittest.TestCase):
    def test_set_read_resources(self):
        pass

    def test_set_read_mode(self):
        pass


################################################################################


class ColorMixinTesting(unittest.TestCase):
    def test_set_color(self):
        train_stop = TrainStop()
        # Valid 4 args
        train_stop.color = (0.1, 0.1, 0.1, 0.1)
        self.assertEqual(train_stop.color, {"r": 0.1, "g": 0.1, "b": 0.1, "a": 0.1})
        # Valid 3 args
        train_stop.color = (0.1, 0.1, 0.1)
        self.assertEqual(train_stop.color, {"r": 0.1, "g": 0.1, "b": 0.1})
        # None
        train_stop.color = None
        self.assertEqual(train_stop.color, None)

        with self.assertRaises(DataFormatError):
            train_stop.color = (1000, 200, 0)

        with self.assertRaises(DataFormatError):
            train_stop.color = ("wrong", 1.0, 1.0)


################################################################################


class ControlBehaviorMixinTesting(unittest.TestCase):
    def test_set_control_behavior(self):
        combinator = ArithmeticCombinator()
        combinator.control_behavior = None
        self.assertEqual(combinator.control_behavior, {})


################################################################################


class DirectionalMixinTesting(unittest.TestCase):
    def test_set_direction(self):
        storage_tank = StorageTank()
        storage_tank.direction = Direction.SOUTH
        self.assertEqual(storage_tank.direction, Direction.SOUTH)
        # Default testing
        storage_tank.direction = Direction.NORTH
        self.assertEqual(storage_tank.direction, Direction.NORTH)
        self.assertEqual(
            storage_tank.to_dict(),
            {"name": storage_tank.name, "position": storage_tank.position},
        )
        storage_tank.direction = None
        self.assertEqual(storage_tank.direction, 0)
        self.assertEqual(
            storage_tank.to_dict(),
            {"name": storage_tank.name, "position": storage_tank.position},
        )
        # Warnings
        with self.assertWarns(DirectionWarning):
            storage_tank.direction = Direction.NORTHEAST
        # Errors
        with self.assertRaises(ValueError):
            storage_tank.direction = "1000"

    def test_set_position(self):
        storage_tank = StorageTank()
        storage_tank.position = (1.23, 1.34)
        self.assertEqual(storage_tank.position, {"x": 1.23, "y": 1.34})
        target_pos = {
            "x": round(storage_tank.position["x"] - storage_tank.tile_width / 2.0),
            "y": round(storage_tank.position["y"] - storage_tank.tile_height / 2.0),
        }
        self.assertEqual(storage_tank.tile_position, target_pos)

        with self.assertRaises(ValueError):
            storage_tank.position = ("fish", 10)

        storage_tank.tile_position = (10, 10.1)  # should cast float to int
        self.assertEqual(storage_tank.tile_position, {"x": 10, "y": 10})
        target_pos = {
            "x": storage_tank.tile_position["x"] + storage_tank.tile_width / 2.0,
            "y": storage_tank.tile_position["y"] + storage_tank.tile_height / 2.0,
        }
        self.assertEqual(storage_tank.position, target_pos)

        with self.assertRaises(ValueError):
            storage_tank.position = (1.0, "raw-fish")


################################################################################


class DoubleGridAlignedMixinTesting(unittest.TestCase):
    def test_set_absolute_position(self):
        rail = StraightRail()
        self.assertEqual(rail.position, {"x": 1.0, "y": 1.0})
        self.assertEqual(rail.tile_position, {"x": 0, "y": 0})
        self.assertEqual(rail.double_grid_aligned, True)
        with self.assertWarns(RailAlignmentWarning):
            rail.position = (2.0, 2.0)


################################################################################


class EightWayDirectionalMixinTesting(unittest.TestCase):
    def test_set_direction(self):
        rail = StraightRail()
        rail.direction = 6
        self.assertEqual(rail.direction, Direction.WEST)
        rail.direction = None
        self.assertEqual(rail.direction, Direction.NORTH)
        with self.assertRaises(ValueError):
            rail.direction = ValueError


################################################################################


class FiltersMixinTesting(unittest.TestCase):
    def test_set_item_filter(self):
        inserter = FilterInserter()

        inserter.set_item_filter(0, "small-lamp")
        self.assertEqual(inserter.filters, [{"index": 1, "name": "small-lamp"}])
        inserter.set_item_filter(1, "burner-inserter")
        self.assertEqual(
            inserter.filters,
            [
                {"index": 1, "name": "small-lamp"},
                {"index": 2, "name": "burner-inserter"},
            ],
        )

        inserter.set_item_filter(0, "fast-transport-belt")
        self.assertEqual(
            inserter.filters,
            [
                {"index": 1, "name": "fast-transport-belt"},
                {"index": 2, "name": "burner-inserter"},
            ],
        )

        inserter.set_item_filter(0, None)
        self.assertEqual(inserter.filters, [{"index": 2, "name": "burner-inserter"}])

        # Errors
        with self.assertRaises(IndexError):
            inserter.set_item_filter(100, "small-lamp")

        with self.assertRaises(InvalidItemError):
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
            ],
        )

        inserter.set_item_filters(
            [
                {"index": 1, "name": "transport-belt"},
                {"index": 2, "name": "fast-transport-belt"},
                {"index": 3, "name": "express-transport-belt"},
            ]
        )
        self.assertEqual(
            inserter.filters,
            [
                {"index": 1, "name": "transport-belt"},
                {"index": 2, "name": "fast-transport-belt"},
                {"index": 3, "name": "express-transport-belt"},
            ],
        )

        inserter.set_item_filters(None)
        self.assertEqual(inserter.filters, None)

        # Errors
        with self.assertRaises(DataFormatError):
            inserter.set_item_filters({"incorrect": "format"})

        with self.assertRaises(IndexError):
            inserter.set_item_filters(
                [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 100, "name": "fast-transport-belt"},
                    {"index": 3, "name": "express-transport-belt"},
                ]
            )

        with self.assertRaises(InvalidItemError):
            inserter.set_item_filters(
                ["transport-belt", "incorrect", "express-transport-belt"]
            )

        with self.assertRaises(InvalidItemError):
            inserter.set_item_filters(
                [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "incorrect"},
                    {"index": 3, "name": "express-transport-belt"},
                ]
            )


################################################################################


class InfinitySettingsMixinTesting(unittest.TestCase):
    def test_set_infinity_settings(self):
        pass


################################################################################


class InventoryMixinTesting(unittest.TestCase):
    def test_bar_index(self):
        container = Container("wooden-chest")
        with self.assertWarns(IndexWarning):
            for i in range(container.inventory_size + 1):
                container.bar = i

        # None case
        container.bar = None
        self.assertEqual(container.bar, None)

        with self.assertRaises(IndexError):
            container.bar = -1

        with self.assertRaises(IndexError):
            container.bar = 100000000  # 100,000,000

        with self.assertRaises(TypeError):
            container.bar = "lmao a string! Who'd do such a dastardly thing????"


################################################################################


class InventoryFilterMixinTesting(unittest.TestCase):
    def test_set_inventory(self):
        cargo_wagon = CargoWagon("cargo-wagon")
        cargo_wagon.inventory = None
        self.assertEqual(cargo_wagon.inventory, {})

    def test_set_inventory_filter(self):
        cargo_wagon = CargoWagon("cargo-wagon")
        cargo_wagon.set_inventory_filter(0, "transport-belt")
        self.assertEqual(
            cargo_wagon.inventory, {"filters": [{"index": 1, "name": "transport-belt"}]}
        )
        cargo_wagon.set_inventory_filter(1, "fast-transport-belt")
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "fast-transport-belt"},
                ]
            },
        )
        cargo_wagon.set_inventory_filter(0, "express-transport-belt")
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "express-transport-belt"},
                    {"index": 2, "name": "fast-transport-belt"},
                ]
            },
        )
        cargo_wagon.set_inventory_filter(0, None)
        self.assertEqual(
            cargo_wagon.inventory,
            {"filters": [{"index": 2, "name": "fast-transport-belt"}]},
        )

        # Errors
        with self.assertRaises(TypeError):
            cargo_wagon.set_inventory_filter("double", "incorrect")
        with self.assertRaises(InvalidItemError):
            cargo_wagon.set_inventory_filter(0, "incorrect")
        with self.assertRaises(IndexError):
            cargo_wagon.set_inventory_filter(50, "stone")

    def test_set_inventory_filters(self):
        cargo_wagon = CargoWagon("cargo-wagon")
        cargo_wagon.set_inventory_filters(["transport-belt", "fast-transport-belt"])
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "transport-belt"},
                    {"index": 2, "name": "fast-transport-belt"},
                ]
            },
        )
        cargo_wagon.set_inventory_filters(
            [
                {"index": 1, "name": "express-transport-belt"},
                {"index": 2, "name": "fast-transport-belt"},
            ]
        )
        self.assertEqual(
            cargo_wagon.inventory,
            {
                "filters": [
                    {"index": 1, "name": "express-transport-belt"},
                    {"index": 2, "name": "fast-transport-belt"},
                ]
            },
        )
        cargo_wagon.set_inventory_filters(None)
        self.assertEqual(cargo_wagon.inventory, {})

        # Warnings
        # Warn if index is out of range
        # TODO

        # Errors
        with self.assertRaises(DataFormatError):
            cargo_wagon.set_inventory_filters(TypeError)

        with self.assertRaises(InvalidItemError):
            cargo_wagon.set_inventory_filters(["incorrect1", "incorrect2"])

    def test_set_bar_index(self):
        cargo_wagon = CargoWagon()
        cargo_wagon.bar = 10
        self.assertEqual(cargo_wagon.bar, 10)
        self.assertEqual(cargo_wagon.inventory, {"bar": 10})
        cargo_wagon.bar = None
        self.assertEqual(cargo_wagon.inventory, {})

        # Warnings
        # Out of index range warning
        with self.assertWarns(IndexWarning):
            cargo_wagon.bar = 100

        # Errors
        with self.assertRaises(TypeError):
            cargo_wagon.bar = "incorrect"

        with self.assertRaises(IndexError):
            cargo_wagon.bar = -1

        with self.assertRaises(IndexError):
            cargo_wagon.bar = 100000000  # 100,000,000


################################################################################


class IOTypeMixinTesting(unittest.TestCase):
    def test_set_io_type(self):
        belt = UndergroundBelt()
        # belt.io_type = "input"

        with self.assertRaises(TypeError):
            belt.io_type = TypeError

        with self.assertRaises(ValueError):
            belt.io_type = "not correct"


################################################################################


class LogisticConditionMixinTesting(unittest.TestCase):
    def test_connect_to_logistic_network(self):
        transport_belt = TransportBelt()
        transport_belt.connect_to_logistic_network = True
        self.assertEqual(transport_belt.connect_to_logistic_network, True)
        self.assertEqual(
            transport_belt.control_behavior, {"connect_to_logistic_network": True}
        )

        transport_belt.connect_to_logistic_network = None
        self.assertEqual(transport_belt.control_behavior, {})

        with self.assertRaises(TypeError):
            transport_belt.connect_to_logistic_network = "True"

    def test_set_logistic_condition(self):
        transport_belt = TransportBelt()
        # Valid
        transport_belt.set_logistic_condition(None)
        self.assertEqual(
            transport_belt.control_behavior,
            {"logistic_condition": {"comparator": "<", "constant": 0}},
        )
        transport_belt.set_logistic_condition("signal-A", ">", -10)
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "logistic_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": ">",
                    "constant": -10,
                }
            },
        )
        transport_belt.set_logistic_condition("signal-A", "<=", "signal-B")
        self.assertEqual(
            transport_belt.control_behavior,
            {
                "logistic_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≤",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )

        # Errors
        # Constant first
        with self.assertRaises(DataFormatError):
            transport_belt.set_logistic_condition(10, ">", "signal-B")
        # Invalid A
        with self.assertRaises(DataFormatError):
            transport_belt.set_logistic_condition(TypeError, ">", "signal-B")
        # Invalid Operation
        with self.assertRaises(DataFormatError):
            transport_belt.set_logistic_condition("signal-A", "hmm", "signal-B")
        # Invalid B
        with self.assertRaises(DataFormatError):
            transport_belt.set_logistic_condition("signal-A", ">", TypeError)

    def test_remove_logistic_condition(self):  # TODO delete
        transport_belt = TransportBelt()
        transport_belt.set_logistic_condition(None)
        transport_belt.remove_logistic_condition()
        self.assertEqual(transport_belt.control_behavior, {})


################################################################################


class InserterModeOfOperationMixinTesting(unittest.TestCase):
    def test_set_mode_of_operation(self):
        inserter = Inserter()
        inserter.mode_of_operation = None
        self.assertEqual(inserter.mode_of_operation, None)
        self.assertEqual(inserter.control_behavior, {})
        # Default
        inserter.mode_of_operation = InserterModeOfOperation.ENABLE_DISABLE
        self.assertEqual(
            inserter.control_behavior,
            {"circuit_mode_of_operation": InserterModeOfOperation.ENABLE_DISABLE},
        )
        inserter.mode_of_operation = InserterModeOfOperation.NONE
        self.assertEqual(
            inserter.control_behavior,
            {"circuit_mode_of_operation": InserterModeOfOperation.NONE},
        )
        # Errors
        with self.assertRaises(ValueError):
            inserter.mode_of_operation = "wrong"


################################################################################


class LogisticModeOfOperationMixinTesting(unittest.TestCase):
    def test_set_mode_of_operation(self):
        requester = LogisticRequestContainer()
        requester.mode_of_operation = None
        self.assertEqual(requester.mode_of_operation, None)
        self.assertEqual(requester.control_behavior, {})
        # Default
        requester.mode_of_operation = LogisticModeOfOperation.SEND_CONTENTS
        self.assertEqual(
            requester.control_behavior,
            {"circuit_mode_of_operation": LogisticModeOfOperation.SEND_CONTENTS},
        )
        requester.mode_of_operation = LogisticModeOfOperation.SET_REQUESTS
        self.assertEqual(
            requester.control_behavior,
            {"circuit_mode_of_operation": LogisticModeOfOperation.SET_REQUESTS},
        )
        # Errors
        with self.assertRaises(ValueError):
            requester.mode_of_operation = "wrong"


################################################################################


class OrientationMixinTesting(unittest.TestCase):
    def test_set_orientation(self):
        locomotive = Locomotive()
        locomotive.orientation = 0.25
        self.assertEqual(
            locomotive.to_dict(),
            {
                "name": "locomotive",
                "position": {"x": 1.0, "y": 3.0},
                "orientation": 0.25,
            },
        )
        locomotive.orientation = None
        self.assertEqual(locomotive.orientation, None)

        with self.assertWarns(ValueWarning):
            locomotive.orientation = 2.0

        with self.assertRaises(TypeError):
            locomotive.orientation = "incorrect"


################################################################################


class PowerConnectableMixinTesting(unittest.TestCase):
    def test_set_neighbours(self):
        substation = ElectricPole("substation")
        substation.neighbours = None
        self.assertEqual(substation.neighbours, [])
        with self.assertRaises(DataFormatError):
            substation.neighbours = {"completely", "wrong"}

    # def test_add_power_connection(self):
    #     substation1 = ElectricPole("substation", id="1")
    #     substation2 = ElectricPole("substation", id="2")
    #     power_switch = PowerSwitch(id="p")

    #     substation1.add_power_connection(substation2)
    #     self.assertEqual(substation1.neighbours, ["2"])
    #     self.assertEqual(substation2.neighbours, ["1"])
    #     substation2.add_power_connection(substation1)
    #     self.assertEqual(substation1.neighbours, ["2"])
    #     self.assertEqual(substation2.neighbours, ["1"])

    #     substation1.add_power_connection(power_switch)
    #     self.assertEqual(substation1.neighbours, ["2"])
    #     self.assertEqual(
    #         power_switch.connections, {"Cu0": [{"entity_id": "1", "wire_id": 0}]}
    #     )
    #     power_switch.add_power_connection(substation1)
    #     self.assertEqual(substation1.neighbours, ["2"])
    #     self.assertEqual(
    #         power_switch.connections, {"Cu0": [{"entity_id": "1", "wire_id": 0}]}
    #     )
    #     substation2.add_power_connection(power_switch)
    #     substation2.add_power_connection(power_switch)
    #     self.assertEqual(substation2.neighbours, ["1"])
    #     self.assertEqual(
    #         power_switch.connections,
    #         {
    #             "Cu0": [
    #                 {"entity_id": "1", "wire_id": 0},
    #                 {"entity_id": "2", "wire_id": 0},
    #             ]
    #         },
    #     )
    #     power_switch.add_power_connection(substation2, side=2)
    #     self.assertEqual(
    #         power_switch.connections,
    #         {
    #             "Cu0": [
    #                 {"entity_id": "1", "wire_id": 0},
    #                 {"entity_id": "2", "wire_id": 0},
    #             ],
    #             "Cu1": [{"entity_id": "2", "wire_id": 0}],
    #         },
    #     )

    #     # Warnings
    #     with self.assertWarns(ConnectionDistanceWarning):
    #         other = ElectricPole(position=[100, 0], id="other")
    #         substation1.add_power_connection(other)

    #     # Errors
    #     with self.assertRaises(EntityNotPowerConnectableError):
    #         substation1.add_power_connection(TransportBelt(id="whatever"))
    #     with self.assertRaises(Exception):
    #         power_switch.add_power_connection(PowerSwitch())

    #     # Make sure correct even after errors
    #     self.assertEqual(substation1.neighbours, ["2", "other"])
    #     self.assertEqual(
    #         power_switch.connections,
    #         {
    #             "Cu0": [
    #                 {"entity_id": "1", "wire_id": 0},
    #                 {"entity_id": "2", "wire_id": 0},
    #             ],
    #             "Cu1": [{"entity_id": "2", "wire_id": 0}],
    #         },
    #     )

    #     # Test removing
    #     substation1.remove_power_connection(substation2)
    #     substation1.remove_power_connection(substation2)
    #     self.assertEqual(substation1.neighbours, ["other"])
    #     self.assertEqual(substation2.neighbours, [])

    #     substation1.remove_power_connection(power_switch)
    #     substation1.remove_power_connection(power_switch)
    #     self.assertEqual(substation1.neighbours, ["other"])
    #     self.assertEqual(
    #         power_switch.connections,
    #         {
    #             "Cu0": [{"entity_id": "2", "wire_id": 0}],
    #             "Cu1": [{"entity_id": "2", "wire_id": 0}],
    #         },
    #     )

    #     substation1.add_power_connection(power_switch)
    #     power_switch.remove_power_connection(substation2, side=1)
    #     power_switch.remove_power_connection(substation2, side=1)
    #     power_switch.remove_power_connection(substation1)
    #     power_switch.remove_power_connection(substation1)
    #     self.assertEqual(
    #         power_switch.connections, {"Cu1": [{"entity_id": "2", "wire_id": 0}]}
    #     )
    #     substation2.remove_power_connection(power_switch, side=2)
    #     substation2.remove_power_connection(power_switch, side=2)
    #     self.assertEqual(power_switch.connections, {})


################################################################################


class ReadRailSignalMixinTesting(unittest.TestCase):
    def test_set_output_signals(self):
        rail_signal = RailSignal()
        rail_signal.red_output_signal = "signal-A"
        self.assertEqual(
            rail_signal.red_output_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            rail_signal.control_behavior,
            {"red_output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        rail_signal.red_output_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            rail_signal.control_behavior,
            {"red_output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        rail_signal.red_output_signal = None
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(DataFormatError):
            rail_signal.red_output_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            rail_signal.red_output_signal = "incorrect"

        rail_signal.yellow_output_signal = "signal-A"
        self.assertEqual(
            rail_signal.yellow_output_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            rail_signal.control_behavior,
            {"yellow_output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        rail_signal.yellow_output_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            rail_signal.control_behavior,
            {"yellow_output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        rail_signal.yellow_output_signal = None
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(DataFormatError):
            rail_signal.yellow_output_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            rail_signal.yellow_output_signal = "wrong"

        rail_signal.green_output_signal = "signal-A"
        self.assertEqual(
            rail_signal.green_output_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            rail_signal.control_behavior,
            {"green_output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        rail_signal.green_output_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            rail_signal.control_behavior,
            {"green_output_signal": {"name": "signal-A", "type": "virtual"}},
        )
        rail_signal.green_output_signal = None
        self.assertEqual(rail_signal.control_behavior, {})
        with self.assertRaises(DataFormatError):
            rail_signal.green_output_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            rail_signal.green_output_signal = "mistake"


################################################################################


class RecipeMixinTesting(unittest.TestCase):
    def test_set_recipe(self):
        machine = AssemblingMachine()

        with self.assertRaises(TypeError):
            machine.recipe = TypeError


################################################################################


class RequestFiltersMixinTesting(unittest.TestCase):
    def test_set_request_filter(self):
        storage_chest = LogisticStorageContainer()
        storage_chest.set_request_filter(0, "stone", 100)
        self.assertEqual(
            storage_chest.request_filters, [{"index": 1, "name": "stone", "count": 100}]
        )
        storage_chest.set_request_filter(1, "copper-ore", 200)
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 1, "name": "stone", "count": 100},
                {"index": 2, "name": "copper-ore", "count": 200},
            ],
        )
        storage_chest.set_request_filter(0, "iron-ore", 1000)
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 1, "name": "iron-ore", "count": 1000},
                {"index": 2, "name": "copper-ore", "count": 200},
            ],
        )
        storage_chest.set_request_filter(0, None)
        self.assertEqual(
            storage_chest.request_filters,
            [{"index": 2, "name": "copper-ore", "count": 200}],
        )
        # test default
        storage_chest.set_request_filter(2, "fast-transport-belt")
        self.assertEqual(
            storage_chest.request_filters,
            [
                {"index": 2, "name": "copper-ore", "count": 200},
                {"index": 3, "name": "fast-transport-belt", "count": 100},
            ],
        )

        # Errors
        with self.assertRaises(TypeError):
            storage_chest.set_request_filter("incorrect", "iron-ore", 100)
        with self.assertRaises(InvalidItemError):
            storage_chest.set_request_filter(1, "incorrect", 100)
        with self.assertRaises(TypeError):
            storage_chest.set_request_filter(1, "iron-ore", "incorrect")
        with self.assertRaises(IndexError):
            storage_chest.set_request_filter(-1, "iron-ore", 100)
        with self.assertRaises(IndexError):
            storage_chest.set_request_filter(1000, "iron-ore", 100)
        with self.assertRaises(ValueError):
            storage_chest.set_request_filter(1, "iron-ore", -1)

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
                {"index": 3, "name": "small-lamp", "count": 50},
            ],
        )
        storage_chest.set_request_filters([("iron-ore", 200)])
        self.assertEqual(
            storage_chest.request_filters,
            [{"index": 1, "name": "iron-ore", "count": 200}],
        )
        # Errors
        with self.assertRaises(InvalidItemError):
            storage_chest.set_request_filters([("iron-ore", 200), ("incorrect", 100)])
        # Make sure that filters are unchanged if command fails
        self.assertEqual(
            storage_chest.request_filters,
            [{"index": 1, "name": "iron-ore", "count": 200}],
        )
        with self.assertRaises(DataFormatError):
            storage_chest.set_request_filters("very wrong")


################################################################################


class RequestItemsMixinTesting(unittest.TestCase):
    def test_set_item_request(self):
        pass

    def test_set_item_requests(self):
        pass

    # def test_remove_item_request(self):
    #     pass


################################################################################


class StackSizeMixinTesting(unittest.TestCase):
    def test_set_stack_size_override(self):
        inserter = Inserter()
        inserter.override_stack_size = 1
        self.assertEqual(inserter.override_stack_size, 1)

        with self.assertRaises(TypeError):
            inserter.override_stack_size = "100,000"

    def test_set_circuit_stack_size_enabled(self):
        inserter = Inserter()
        inserter.circuit_stack_size_enabled = True
        self.assertEqual(inserter.circuit_stack_size_enabled, True)
        self.assertEqual(inserter.control_behavior, {"circuit_set_stack_size": True})

        inserter.circuit_stack_size_enabled = None
        self.assertEqual(inserter.control_behavior, {})

        with self.assertRaises(TypeError):
            inserter.circuit_stack_size_enabled = "incorrect"

    def test_set_stack_control_signal(self):
        inserter = Inserter()
        inserter.stack_control_signal = "signal-A"
        self.assertEqual(
            inserter.stack_control_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            inserter.control_behavior,
            {"stack_control_input_signal": {"name": "signal-A", "type": "virtual"}},
        )

        inserter.stack_control_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            inserter.control_behavior,
            {"stack_control_input_signal": {"name": "signal-A", "type": "virtual"}},
        )

        inserter.stack_control_signal = None
        self.assertEqual(inserter.control_behavior, {})

        with self.assertRaises(DataFormatError):
            inserter.stack_control_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            inserter.stack_control_signal = "wrong_name_lol"
