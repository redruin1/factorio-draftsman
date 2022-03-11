# test_roboport.py

from draftsman.entity import Roboport, roboports
from draftsman.error import InvalidEntityError, InvalidSignalError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

from unittest import TestCase

class RoboportTesting(TestCase):
    def test_constructor_init(self):
        roboport = Roboport(
            "roboport", position = [1, 1],
            control_behavior = {
                "read_logistics": True
            }
        )
        self.assertEqual(
            roboport.to_dict(),
            {
                "name": "roboport",
                "position": {"x": 3.0, "y": 3.0},
                "control_behavior": {
                    "read_logistics": True
                }
            }
        )

        roboport = Roboport(
            "roboport", position = [1, 1],
            control_behavior = {
                "read_logistics": True,
                "read_robot_stats": True,
                "available_logistic_output_signal": "signal-A",
                "total_logistic_output_signal": "signal-B",
                "available_construction_output_signal": "signal-C",
                "total_construction_output_signal": "signal-D"
            }
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
                        "type": "virtual"
                    },
                    "total_logistic_output_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    },
                    "available_construction_output_signal": {
                        "name": "signal-C",
                        "type": "virtual"
                    },
                    "total_construction_output_signal": {
                        "name": "signal-D",
                        "type": "virtual"
                    }
                }
            }
        )

        roboport = Roboport(
            "roboport", position = [1, 1],
            control_behavior = {
                "read_logistics": True,
                "read_robot_stats": True,
                "available_logistic_output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                },
                "total_logistic_output_signal": {
                    "name": "signal-B",
                    "type": "virtual"
                },
                "available_construction_output_signal": {
                    "name": "signal-C",
                    "type": "virtual"
                },
                "total_construction_output_signal": {
                    "name": "signal-D",
                    "type": "virtual"
                }
            }
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
                        "type": "virtual"
                    },
                    "total_logistic_output_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    },
                    "available_construction_output_signal": {
                        "name": "signal-C",
                        "type": "virtual"
                    },
                    "total_construction_output_signal": {
                        "name": "signal-D",
                        "type": "virtual"
                    }
                }
            }
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Roboport("roboport", unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Roboport("this is not a roboport")

    def test_flags(self):
        pass # TODO

    def test_set_read_logistics(self):
        roboport = Roboport()
        roboport.set_read_logistics(True)
        self.assertEqual(
            roboport.control_behavior,
            {
                "read_logistics": True
            }
        )
        roboport.set_read_logistics(None)
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(SchemaError):
            roboport.set_read_logistics("incorrect")

    def test_set_read_robot_stats(self):
        roboport = Roboport()
        roboport.set_read_robot_stats(True)
        self.assertEqual(
            roboport.control_behavior,
            {
                "read_robot_stats": True
            }
        )
        roboport.set_read_robot_stats(None)
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(SchemaError):
            roboport.set_read_robot_stats("incorrect")

    def test_set_available_logistics_signal(self):
        roboport = Roboport()
        roboport.set_available_logistics_signal("signal-A")
        self.assertEqual(
            roboport.control_behavior,
            {
                "available_logistic_output_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )
        roboport.set_available_logistics_signal(None)
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(InvalidSignalError):
            roboport.set_available_logistics_signal("incorrect")

    def test_set_total_logistics_signal(self):
        roboport = Roboport()
        roboport.set_total_logistics_signal("signal-B")
        self.assertEqual(
            roboport.control_behavior,
            {
                "total_logistic_output_signal": {
                    "name": "signal-B",
                    "type": "virtual"
                }
            }
        )
        roboport.set_total_logistics_signal(None)
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(InvalidSignalError):
            roboport.set_total_logistics_signal("incorrect")

    def test_set_available_construction_signal(self):
        roboport = Roboport()
        roboport.set_available_construction_signal("signal-C")
        self.assertEqual(
            roboport.control_behavior,
            {
                "available_construction_output_signal": {
                    "name": "signal-C",
                    "type": "virtual"
                }
            }
        )
        roboport.set_available_construction_signal(None)
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(InvalidSignalError):
            roboport.set_available_construction_signal("incorrect")

    def test_set_total_construction_signal(self):
        roboport = Roboport()
        roboport.set_total_construction_signal("signal-D")
        self.assertEqual(
            roboport.control_behavior,
            {
                "total_construction_output_signal": {
                    "name": "signal-D",
                    "type": "virtual"
                }
            }
        )
        roboport.set_total_construction_signal(None)
        self.assertEqual(roboport.control_behavior, {})
        with self.assertRaises(InvalidSignalError):
            roboport.set_total_construction_signal("incorrect")
