# test_roboport.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Roboport, roboports
from draftsman.error import InvalidEntityError, InvalidSignalError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class RoboportTesting(TestCase):
    def test_constructor_init(self):
        roboport = Roboport(
            "roboport", tile_position=[1, 1], control_behavior={"read_logistics": True}
        )
        self.assertEqual(
            roboport.to_dict(),
            {
                "name": "roboport",
                "position": {"x": 3.0, "y": 3.0},
                "control_behavior": {"read_logistics": True},
            },
        )

        roboport = Roboport(
            "roboport",
            tile_position=[1, 1],
            control_behavior={
                "read_logistics": True,
                "read_robot_stats": True,
                "available_logistic_output_signal": "signal-A",
                "total_logistic_output_signal": "signal-B",
                "available_construction_output_signal": "signal-C",
                "total_construction_output_signal": "signal-D",
            },
        )
        self.maxDiff = None
        self.assertEqual(
            roboport.to_dict(),
            {
                "name": "roboport",
                "position": {"x": 3.0, "y": 3.0},
                "control_behavior": {
                    "read_logistics": True,
                    "read_robot_stats": True,
                    "available_logistic_output_signal": {
                        "name": "signal-A",
                        "type": "virtual",
                    },
                    "total_logistic_output_signal": {
                        "name": "signal-B",
                        "type": "virtual",
                    },
                    "available_construction_output_signal": {
                        "name": "signal-C",
                        "type": "virtual",
                    },
                    "total_construction_output_signal": {
                        "name": "signal-D",
                        "type": "virtual",
                    },
                },
            },
        )

        roboport = Roboport(
            "roboport",
            tile_position=[1, 1],
            control_behavior={
                "read_logistics": True,
                "read_robot_stats": True,
                "available_logistic_output_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                },
                "total_logistic_output_signal": {"name": "signal-B", "type": "virtual"},
                "available_construction_output_signal": {
                    "name": "signal-C",
                    "type": "virtual",
                },
                "total_construction_output_signal": {
                    "name": "signal-D",
                    "type": "virtual",
                },
            },
        )
        self.maxDiff = None
        self.assertEqual(
            roboport.to_dict(),
            {
                "name": "roboport",
                "position": {"x": 3.0, "y": 3.0},
                "control_behavior": {
                    "read_logistics": True,
                    "read_robot_stats": True,
                    "available_logistic_output_signal": {
                        "name": "signal-A",
                        "type": "virtual",
                    },
                    "total_logistic_output_signal": {
                        "name": "signal-B",
                        "type": "virtual",
                    },
                    "available_construction_output_signal": {
                        "name": "signal-C",
                        "type": "virtual",
                    },
                    "total_construction_output_signal": {
                        "name": "signal-D",
                        "type": "virtual",
                    },
                },
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Roboport("roboport", unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Roboport("this is not a roboport")

    def test_set_read_logistics(self):
        roboport = Roboport()
        roboport.read_logistics = True
        self.assertEqual(roboport.read_logistics, True)
        self.assertEqual(roboport.control_behavior, {"read_logistics": True})
        roboport.read_logistics = None
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(TypeError):
            roboport.read_logistics = "incorrect"

    def test_set_read_robot_stats(self):
        roboport = Roboport()
        roboport.read_robot_stats = True
        self.assertEqual(roboport.read_robot_stats, True)
        self.assertEqual(roboport.control_behavior, {"read_robot_stats": True})
        roboport.read_robot_stats = None
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(TypeError):
            roboport.read_robot_stats = "incorrect"

    def test_set_available_logistics_signal(self):
        roboport = Roboport()
        roboport.available_logistic_signal = "signal-A"
        self.assertEqual(
            roboport.available_logistic_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            roboport.control_behavior,
            {
                "available_logistic_output_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                }
            },
        )
        roboport.available_logistic_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            roboport.control_behavior,
            {
                "available_logistic_output_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                }
            },
        )
        roboport.available_logistic_signal = None
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(TypeError):
            roboport.available_logistic_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            roboport.available_logistic_signal = "incorrect"

    def test_set_total_logistics_signal(self):
        roboport = Roboport()
        roboport.total_logistic_signal = "signal-B"
        self.assertEqual(
            roboport.total_logistic_signal, {"name": "signal-B", "type": "virtual"}
        )
        self.assertEqual(
            roboport.control_behavior,
            {"total_logistic_output_signal": {"name": "signal-B", "type": "virtual"}},
        )
        roboport.total_logistic_signal = {"name": "signal-B", "type": "virtual"}
        self.assertEqual(
            roboport.control_behavior,
            {"total_logistic_output_signal": {"name": "signal-B", "type": "virtual"}},
        )
        roboport.total_logistic_signal = None
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(TypeError):
            roboport.total_logistic_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            roboport.total_logistic_signal = "incorrect"

    def test_set_available_construction_signal(self):
        roboport = Roboport()
        roboport.available_construction_signal = "signal-C"
        self.assertEqual(
            roboport.available_construction_signal,
            {"name": "signal-C", "type": "virtual"},
        )
        self.assertEqual(
            roboport.control_behavior,
            {
                "available_construction_output_signal": {
                    "name": "signal-C",
                    "type": "virtual",
                }
            },
        )
        roboport.available_construction_signal = {"name": "signal-C", "type": "virtual"}
        self.assertEqual(
            roboport.control_behavior,
            {
                "available_construction_output_signal": {
                    "name": "signal-C",
                    "type": "virtual",
                }
            },
        )
        roboport.available_construction_signal = None
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(TypeError):
            roboport.available_construction_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            roboport.available_construction_signal = "incorrect"

    def test_set_total_construction_signal(self):
        roboport = Roboport()
        roboport.total_construction_signal = "signal-D"
        self.assertEqual(
            roboport.total_construction_signal, {"name": "signal-D", "type": "virtual"}
        )
        self.assertEqual(
            roboport.control_behavior,
            {
                "total_construction_output_signal": {
                    "name": "signal-D",
                    "type": "virtual",
                }
            },
        )
        roboport.total_construction_signal = {"name": "signal-D", "type": "virtual"}
        self.assertEqual(
            roboport.control_behavior,
            {
                "total_construction_output_signal": {
                    "name": "signal-D",
                    "type": "virtual",
                }
            },
        )
        roboport.total_construction_signal = None
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(TypeError):
            roboport.total_construction_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            roboport.total_construction_signal = "incorrect"
