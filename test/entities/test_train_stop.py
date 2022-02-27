# test_train_stop.py

from draftsman.entity import TrainStop, train_stops, Direction
from draftsman.errors import InvalidEntityID, InvalidSignalID

from schema import SchemaError

from unittest import TestCase

class TrainStopTesting(TestCase):
    def test_default_constructor(self):
        train_stop = TrainStop()
        self.assertEqual(
            train_stop.to_dict(),
            {
                "name": "train-stop",
                "position": {"x": 1.0, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        train_stop = TrainStop(
            "train-stop", 
            position = [0, 0],
            direction = Direction.EAST,
            control_behavior = {}
        )
        self.assertEqual(
            train_stop.to_dict(),
            {
                "name": "train-stop",
                "position": {"x": 1.0, "y": 1.0},
                "direction": 2,
            }
        )

        train_stop = TrainStop(
            "train-stop", 
            position = [0, 0],
            direction = Direction.EAST,
            station = "Station name",
            manual_trains_limit = 3,
            color = [1.0, 1.0, 1.0, 1.0],
            control_behavior = {
                "read_from_train": True,
                "read_stopped_train": True,
                "train_stopped_signal": "signal-A",
                "set_trains_limit": True,
                "trains_limit_signal": "signal-B",
                "read_trains_count": True,
                "trains_count_signal": "signal-C"
            }
        )
        self.assertEqual(
            train_stop.to_dict(),
            {
                "name": "train-stop",
                "position": {"x": 1.0, "y": 1.0},
                "direction": 2,
                "station": "Station name",
                "manual_trains_limit": 3,
                "color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0},
                "control_behavior": {
                    "read_from_train": True,
                    "read_stopped_train": True,
                    "train_stopped_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "set_trains_limit": True,
                    "trains_limit_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    },
                    "read_trains_count": True,
                    "trains_count_signal": {
                        "name": "signal-C",
                        "type": "virtual"
                    },
                }
            }
        )

        train_stop = TrainStop(
            "train-stop", 
            position = [0, 0],
            direction = Direction.EAST,
            station = "Station name",
            manual_trains_limit = 3,
            color = {"r": 1.0, "g": 1.0, "b": 1.0},
            control_behavior = {
                "train_stopped_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                },
                "trains_limit_signal": {
                    "name": "signal-B",
                    "type": "virtual"
                },
                "trains_count_signal": {
                    "name": "signal-C",
                    "type": "virtual"
                },
            }
        )
        self.assertEqual(
            train_stop.to_dict(),
            {
                "name": "train-stop",
                "position": {"x": 1.0, "y": 1.0},
                "direction": 2,
                "station": "Station name",
                "manual_trains_limit": 3,
                "color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0},
                "control_behavior": {
                    "train_stopped_signal": {
                        "name": "signal-A",
                        "type": "virtual"
                    },
                    "trains_limit_signal": {
                        "name": "signal-B",
                        "type": "virtual"
                    },
                    "trains_count_signal": {
                        "name": "signal-C",
                        "type": "virtual"
                    },
                }
            }
        )

        # Warnings:
        with self.assertWarns(UserWarning):
            TrainStop("train-stop", invalid_keyword = "whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with self.assertWarns(UserWarning):
            TrainStop("train-stop", position = [1, 1])
        # Incorrect direction
        with self.assertWarns(UserWarning):
            TrainStop("train-stop", direction = Direction.NORTHWEST)

        # Errors
        with self.assertRaises(InvalidEntityID):
            TrainStop("this is not a curved rail")
        with self.assertRaises(SchemaError):
            TrainStop(station = 100)
        with self.assertRaises(SchemaError):
            TrainStop(color = "wrong")

    def test_dimensions(self):
        train_stop = TrainStop()
        self.assertEqual(train_stop.width, 2)
        self.assertEqual(train_stop.height, 2)

    def test_set_read_from_train(self):
        train_stop = TrainStop()
        train_stop.set_read_from_train(True)
        self.assertEqual(
            train_stop.control_behavior,
            {
                "read_from_train": True
            }
        )

        train_stop.set_read_from_train(None)
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(SchemaError):
            train_stop.set_read_from_train("wrong")

    def test_set_read_stopped_train(self):
        train_stop = TrainStop()
        train_stop.set_read_stopped_train(False)
        self.assertEqual(
            train_stop.control_behavior,
            {
                "read_stopped_train": False
            }
        )

        train_stop.set_read_stopped_train(None)
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(SchemaError):
            train_stop.set_read_stopped_train("wrong")

    def test_set_train_stopped_signal(self):
        train_stop = TrainStop()
        train_stop.set_train_stopped_signal("signal-A")
        self.assertEqual(
            train_stop.control_behavior,
            {
                "train_stopped_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )

        train_stop.set_train_stopped_signal(None)
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(InvalidSignalID):
            train_stop.set_train_stopped_signal("wrong signal")

    def test_set_trains_limit(self):
        train_stop = TrainStop()
        train_stop.set_trains_limit(True)
        self.assertEqual(
            train_stop.control_behavior,
            {
                "set_trains_limit": True
            }
        )

        train_stop.set_trains_limit(None)
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(SchemaError):
            train_stop.set_trains_limit("wrong")

    def test_set_trains_limit_signal(self):
        train_stop = TrainStop()
        train_stop.set_trains_limit_signal("signal-A")
        self.assertEqual(
            train_stop.control_behavior,
            {
                "trains_limit_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )

        train_stop.set_trains_limit_signal(None)
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(InvalidSignalID):
            train_stop.set_trains_limit_signal("wrong signal")

    def test_set_read_trains_count(self):
        train_stop = TrainStop()
        train_stop.set_read_trains_count(True)
        self.assertEqual(
            train_stop.control_behavior,
            {
                "read_trains_count": True
            }
        )

        train_stop.set_read_trains_count(None)
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(SchemaError):
            train_stop.set_read_trains_count("wrong")

    def test_set_trains_count_signal(self):
        train_stop = TrainStop()
        train_stop.set_trains_count_signal("signal-A")
        self.assertEqual(
            train_stop.control_behavior,
            {
                "trains_count_signal": {
                    "name": "signal-A",
                    "type": "virtual"
                }
            }
        )

        train_stop.set_trains_count_signal(None)
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(InvalidSignalID):
            train_stop.set_trains_count_signal("wrong signal")