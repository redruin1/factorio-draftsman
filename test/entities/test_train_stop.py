# test_train_stop.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import TrainStop, train_stops
from draftsman.error import InvalidEntityError, InvalidSignalError, DataFormatError
from draftsman.warning import DraftsmanWarning, RailAlignmentWarning, DirectionWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class TrainStopTesting(TestCase):
    def test_constructor_init(self):
        train_stop = TrainStop(
            "train-stop",
            tile_position=[0, 0],
            direction=Direction.EAST,
            control_behavior={},
        )
        self.assertEqual(
            train_stop.to_dict(),
            {
                "name": "train-stop",
                "position": {"x": 1.0, "y": 1.0},
                "direction": Direction.EAST,
            },
        )

        train_stop = TrainStop(
            "train-stop",
            tile_position=[0, 0],
            direction=Direction.EAST,
            station="Station name",
            manual_trains_limit=3,
            color=[1.0, 1.0, 1.0, 1.0],
            control_behavior={
                "read_from_train": True,
                "read_stopped_train": True,
                "train_stopped_signal": "signal-A",
                "set_trains_limit": True,
                "trains_limit_signal": "signal-B",
                "read_trains_count": True,
                "trains_count_signal": "signal-C",
            },
        )
        self.maxDiff = None
        self.assertEqual(
            train_stop.to_dict(),
            {
                "name": "train-stop",
                "position": {"x": 1.0, "y": 1.0},
                "direction": Direction.EAST,
                "station": "Station name",
                "manual_trains_limit": 3,
                "color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0},
                "control_behavior": {
                    "read_from_train": True,
                    "read_stopped_train": True,
                    "train_stopped_signal": {"name": "signal-A", "type": "virtual"},
                    "set_trains_limit": True,
                    "trains_limit_signal": {"name": "signal-B", "type": "virtual"},
                    "read_trains_count": True,
                    "trains_count_signal": {"name": "signal-C", "type": "virtual"},
                },
            },
        )

        train_stop = TrainStop(
            "train-stop",
            tile_position=[0, 0],
            direction=Direction.EAST,
            station="Station name",
            manual_trains_limit=3,
            color={"r": 1.0, "g": 1.0, "b": 1.0},
            control_behavior={
                "train_stopped_signal": {"name": "signal-A", "type": "virtual"},
                "trains_limit_signal": {"name": "signal-B", "type": "virtual"},
                "trains_count_signal": {"name": "signal-C", "type": "virtual"},
            },
        )
        self.maxDiff = None
        self.assertEqual(
            train_stop.to_dict(),
            {
                "name": "train-stop",
                "position": {"x": 1.0, "y": 1.0},
                "direction": Direction.EAST,
                "station": "Station name",
                "manual_trains_limit": 3,
                "color": {"r": 1.0, "g": 1.0, "b": 1.0},
                "control_behavior": {
                    "train_stopped_signal": {"name": "signal-A", "type": "virtual"},
                    "trains_limit_signal": {"name": "signal-B", "type": "virtual"},
                    "trains_count_signal": {"name": "signal-C", "type": "virtual"},
                },
            },
        )

        # Warnings:
        with self.assertWarns(DraftsmanWarning):
            TrainStop("train-stop", invalid_keyword="whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with self.assertWarns(RailAlignmentWarning):
            TrainStop("train-stop", tile_position=[1, 1])
        # Incorrect direction
        with self.assertWarns(DirectionWarning):
            TrainStop("train-stop", direction=Direction.NORTHWEST)

        # Errors
        with self.assertRaises(InvalidEntityError):
            TrainStop("this is not a curved rail")
        with self.assertRaises(TypeError):
            TrainStop(station=100)
        with self.assertRaises(DataFormatError):
            TrainStop(color="wrong")

    def test_set_manual_trains_limit(self):
        train_stop = TrainStop()
        train_stop.manual_trains_limit = None
        self.assertEqual(train_stop.manual_trains_limit, None)
        with self.assertRaises(TypeError):
            train_stop.manual_trains_limit = "incorrect"

    def test_set_read_from_train(self):
        train_stop = TrainStop()
        train_stop.read_from_train = True
        self.assertEqual(train_stop.read_from_train, True)
        self.assertEqual(train_stop.control_behavior, {"read_from_train": True})

        train_stop.read_from_train = None
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(TypeError):
            train_stop.read_from_train = "wrong"

    def test_set_read_stopped_train(self):
        train_stop = TrainStop()
        train_stop.read_stopped_train = False
        self.assertEqual(train_stop.read_stopped_train, False)
        self.assertEqual(train_stop.control_behavior, {"read_stopped_train": False})

        train_stop.read_stopped_train = None
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(TypeError):
            train_stop.read_stopped_train = "wrong"

    def test_set_train_stopped_signal(self):
        train_stop = TrainStop()
        train_stop.train_stopped_signal = "signal-A"
        self.assertEqual(
            train_stop.train_stopped_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            train_stop.control_behavior,
            {"train_stopped_signal": {"name": "signal-A", "type": "virtual"}},
        )

        train_stop.train_stopped_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            train_stop.control_behavior,
            {"train_stopped_signal": {"name": "signal-A", "type": "virtual"}},
        )

        train_stop.train_stopped_signal = None
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(TypeError):
            train_stop.train_stopped_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            train_stop.train_stopped_signal = "wrong signal"

    def test_set_trains_limit(self):
        train_stop = TrainStop()
        train_stop.signal_limits_trains = True
        self.assertEqual(train_stop.signal_limits_trains, True)
        self.assertEqual(train_stop.control_behavior, {"set_trains_limit": True})

        train_stop.signal_limits_trains = None
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(TypeError):
            train_stop.signal_limits_trains = "wrong"

    def test_set_trains_limit_signal(self):
        train_stop = TrainStop()
        train_stop.trains_limit_signal = "signal-A"
        self.assertEqual(
            train_stop.trains_limit_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            train_stop.control_behavior,
            {"trains_limit_signal": {"name": "signal-A", "type": "virtual"}},
        )

        train_stop.trains_limit_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            train_stop.control_behavior,
            {"trains_limit_signal": {"name": "signal-A", "type": "virtual"}},
        )

        train_stop.trains_limit_signal = None
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(TypeError):
            train_stop.trains_limit_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            train_stop.trains_limit_signal = "wrong signal"

    def test_set_read_trains_count(self):
        train_stop = TrainStop()
        train_stop.read_trains_count = True
        self.assertEqual(train_stop.read_trains_count, True)
        self.assertEqual(train_stop.control_behavior, {"read_trains_count": True})

        train_stop.read_trains_count = None
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(TypeError):
            train_stop.read_trains_count = "wrong"

    def test_set_trains_count_signal(self):
        train_stop = TrainStop()
        train_stop.trains_count_signal = "signal-A"
        self.assertEqual(
            train_stop.trains_count_signal, {"name": "signal-A", "type": "virtual"}
        )
        self.assertEqual(
            train_stop.control_behavior,
            {"trains_count_signal": {"name": "signal-A", "type": "virtual"}},
        )

        train_stop.trains_count_signal = {"name": "signal-A", "type": "virtual"}
        self.assertEqual(
            train_stop.control_behavior,
            {"trains_count_signal": {"name": "signal-A", "type": "virtual"}},
        )

        train_stop.trains_count_signal = None
        self.assertEqual(train_stop.control_behavior, {})

        with self.assertRaises(TypeError):
            train_stop.trains_count_signal = TypeError
        with self.assertRaises(InvalidSignalError):
            train_stop.trains_count_signal = "wrong signal"
