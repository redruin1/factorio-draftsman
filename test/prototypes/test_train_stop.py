# test_train_stop.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import TrainStop, train_stops
from draftsman.error import InvalidEntityError, InvalidSignalError, DataFormatError
from draftsman.warning import DraftsmanWarning, RailAlignmentWarning, DirectionWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class TrainStopTesting(unittest.TestCase):
    def test_constructor_init(self):
        train_stop = TrainStop(
            "train-stop",
            tile_position=[0, 0],
            direction=Direction.EAST,
            control_behavior={},
        )
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1.0, "y": 1.0},
            "direction": Direction.EAST,
        }

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
        assert train_stop.to_dict() == {
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
        }

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
        assert train_stop.to_dict() == {
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
        }

        # Warnings:
        with pytest.warns(DraftsmanWarning):
            TrainStop("train-stop", invalid_keyword="whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with pytest.warns(RailAlignmentWarning):
            TrainStop("train-stop", tile_position=[1, 1])
        # Incorrect direction
        with pytest.warns(DirectionWarning):
            TrainStop("train-stop", direction=Direction.NORTHWEST)

        # Errors
        with pytest.raises(InvalidEntityError):
            TrainStop("this is not a curved rail")
        with pytest.raises(TypeError):
            TrainStop(station=100)
        with pytest.raises(DataFormatError):
            TrainStop(color="wrong")
        with pytest.raises(DataFormatError):
            TrainStop(control_behavior={"unused_key": "something"})

    def test_set_manual_trains_limit(self):
        train_stop = TrainStop()
        train_stop.manual_trains_limit = None
        assert train_stop.manual_trains_limit == None
        with pytest.raises(TypeError):
            train_stop.manual_trains_limit = "incorrect"

    def test_set_read_from_train(self):
        train_stop = TrainStop()
        train_stop.read_from_train = True
        assert train_stop.read_from_train == True
        assert train_stop.control_behavior == {"read_from_train": True}

        train_stop.read_from_train = None
        assert train_stop.control_behavior == {}

        with pytest.raises(TypeError):
            train_stop.read_from_train = "wrong"

    def test_set_read_stopped_train(self):
        train_stop = TrainStop()
        train_stop.read_stopped_train = False
        assert train_stop.read_stopped_train == False
        assert train_stop.control_behavior == {"read_stopped_train": False}

        train_stop.read_stopped_train = None
        assert train_stop.control_behavior == {}

        with pytest.raises(TypeError):
            train_stop.read_stopped_train = "wrong"

    def test_set_train_stopped_signal(self):
        train_stop = TrainStop()
        train_stop.train_stopped_signal = "signal-A"
        assert train_stop.train_stopped_signal == {
            "name": "signal-A",
            "type": "virtual",
        }
        assert train_stop.control_behavior == {
            "train_stopped_signal": {"name": "signal-A", "type": "virtual"}
        }

        train_stop.train_stopped_signal = {"name": "signal-A", "type": "virtual"}
        assert train_stop.control_behavior == {
            "train_stopped_signal": {"name": "signal-A", "type": "virtual"}
        }

        train_stop.train_stopped_signal = None
        assert train_stop.control_behavior == {}

        with pytest.raises(TypeError):
            train_stop.train_stopped_signal = TypeError
        with pytest.raises(InvalidSignalError):
            train_stop.train_stopped_signal = "wrong signal"

    def test_set_trains_limit(self):
        train_stop = TrainStop()
        train_stop.signal_limits_trains = True
        assert train_stop.signal_limits_trains == True
        assert train_stop.control_behavior == {"set_trains_limit": True}

        train_stop.signal_limits_trains = None
        assert train_stop.control_behavior == {}

        with pytest.raises(TypeError):
            train_stop.signal_limits_trains = "wrong"

    def test_set_trains_limit_signal(self):
        train_stop = TrainStop()
        train_stop.trains_limit_signal = "signal-A"
        assert train_stop.trains_limit_signal == {"name": "signal-A", "type": "virtual"}
        assert train_stop.control_behavior == {
            "trains_limit_signal": {"name": "signal-A", "type": "virtual"}
        }

        train_stop.trains_limit_signal = {"name": "signal-A", "type": "virtual"}
        assert train_stop.control_behavior == {
            "trains_limit_signal": {"name": "signal-A", "type": "virtual"}
        }

        train_stop.trains_limit_signal = None
        assert train_stop.control_behavior == {}

        with pytest.raises(TypeError):
            train_stop.trains_limit_signal = TypeError
        with pytest.raises(InvalidSignalError):
            train_stop.trains_limit_signal = "wrong signal"

    def test_set_read_trains_count(self):
        train_stop = TrainStop()
        train_stop.read_trains_count = True
        assert train_stop.read_trains_count == True
        assert train_stop.control_behavior == {"read_trains_count": True}

        train_stop.read_trains_count = None
        assert train_stop.control_behavior == {}

        with pytest.raises(TypeError):
            train_stop.read_trains_count = "wrong"

    def test_set_trains_count_signal(self):
        train_stop = TrainStop()
        train_stop.trains_count_signal = "signal-A"
        assert train_stop.trains_count_signal == {"name": "signal-A", "type": "virtual"}
        assert train_stop.control_behavior == {
            "trains_count_signal": {"name": "signal-A", "type": "virtual"}
        }

        train_stop.trains_count_signal = {"name": "signal-A", "type": "virtual"}
        assert train_stop.control_behavior == {
            "trains_count_signal": {"name": "signal-A", "type": "virtual"}
        }

        train_stop.trains_count_signal = None
        assert train_stop.control_behavior == {}

        with pytest.raises(TypeError):
            train_stop.trains_count_signal = TypeError
        with pytest.raises(InvalidSignalError):
            train_stop.trains_count_signal = "wrong signal"

    def test_mergable_with(self):
        stop1 = TrainStop("train-stop")
        stop2 = TrainStop(
            "train-stop",
            station="Station name",
            manual_trains_limit=3,
            color=[0.5, 0.5, 0.5],
            control_behavior={
                "read_from_train": True,
                "read_stopped_train": True,
                "train_stopped_signal": "signal-A",
                "set_trains_limit": True,
                "trains_limit_signal": "signal-B",
                "read_trains_count": True,
                "trains_count_signal": "signal-C",
            },
            tags={"some": "stuff"},
        )

        assert stop1.mergable_with(stop1)

        assert stop1.mergable_with(stop2)
        assert stop2.mergable_with(stop1)

        stop2.tile_position = (2, 2)
        assert not stop1.mergable_with(stop2)

    def test_merge(self):
        stop1 = TrainStop("train-stop")
        stop2 = TrainStop(
            "train-stop",
            station="Station name",
            manual_trains_limit=3,
            color=[0.5, 0.5, 0.5],
            control_behavior={
                "read_from_train": True,
                "read_stopped_train": True,
                "train_stopped_signal": "signal-A",
                "set_trains_limit": True,
                "trains_limit_signal": "signal-B",
                "read_trains_count": True,
                "trains_count_signal": "signal-C",
            },
            tags={"some": "stuff"},
        )

        stop1.merge(stop2)
        del stop2

        assert stop1.station == "Station name"
        assert stop1.tags == {"some": "stuff"}
