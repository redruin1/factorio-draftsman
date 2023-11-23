# test_train_stop.py

from draftsman.constants import Direction, ValidationMode
from draftsman.entity import TrainStop, train_stops, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalID
from draftsman.warning import (
    GridAlignmentWarning,
    DirectionWarning,
    UnknownKeywordWarning,
    UnknownSignalWarning,
)

from collections.abc import Hashable
import pytest


class TestTrainStop:
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
                # "trains_count_signal": {"name": "signal-C", "type": "virtual"}, # Default
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
                # "trains_count_signal": {"name": "signal-C", "type": "virtual"}, # Default
            },
        }

        # Warnings:
        with pytest.warns(UnknownKeywordWarning):
            TrainStop("train-stop", invalid_keyword="whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with pytest.warns(GridAlignmentWarning):
            TrainStop("train-stop", tile_position=(1, 1))
        # Incorrect direction
        with pytest.warns(DirectionWarning):
            TrainStop("train-stop", direction=Direction.NORTHWEST)

        # Errors
        with pytest.raises(DataFormatError):
            TrainStop(station=100)

        with pytest.raises(DataFormatError):
            TrainStop(color="wrong")
        with pytest.raises(DataFormatError):
            TrainStop(control_behavior="incorrect")

    def test_set_manual_trains_limit(self):
        train_stop = TrainStop()
        train_stop.manual_trains_limit = None
        assert train_stop.manual_trains_limit == None

        with pytest.raises(DataFormatError):
            train_stop.manual_trains_limit = 2**64
        with pytest.raises(DataFormatError):
            train_stop.manual_trains_limit = "incorrect"

    def test_set_send_to_train(self):
        train_stop = TrainStop()
        assert train_stop.send_to_train == True
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
        }

        train_stop.send_to_train = False
        assert train_stop.send_to_train == False
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"send_to_train": False},
        }

        train_stop.send_to_train = None
        assert train_stop.send_to_train == None
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
        }

        train_stop.validate_assignment = "none"
        assert train_stop.validate_assignment == ValidationMode.NONE

        train_stop.send_to_train = "incorrect"
        assert train_stop.send_to_train == "incorrect"
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"send_to_train": "incorrect"},
        }

    def test_set_read_from_train(self):
        train_stop = TrainStop()
        train_stop.read_from_train = True
        assert train_stop.read_from_train == True

        train_stop.read_from_train = None
        assert train_stop.read_from_train == None

        with pytest.raises(DataFormatError):
            train_stop.read_from_train = "wrong"

        train_stop.validate_assignment = "none"
        assert train_stop.validate_assignment == ValidationMode.NONE

        train_stop.read_from_train = "incorrect"
        assert train_stop.read_from_train == "incorrect"
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"read_from_train": "incorrect"},
        }

    def test_set_read_stopped_train(self):
        train_stop = TrainStop()
        train_stop.read_stopped_train = False
        assert train_stop.read_stopped_train == False

        train_stop.read_stopped_train = None
        assert train_stop.read_stopped_train == None

        with pytest.raises(DataFormatError):
            train_stop.read_stopped_train = "wrong"

        train_stop.validate_assignment = "none"
        assert train_stop.validate_assignment == ValidationMode.NONE

        train_stop.read_stopped_train = "incorrect"
        assert train_stop.read_stopped_train == "incorrect"
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"read_stopped_train": "incorrect"},
        }

    def test_set_train_stopped_signal(self):
        train_stop = TrainStop()
        train_stop.train_stopped_signal = "signal-A"
        assert train_stop.train_stopped_signal == SignalID(
            name="signal-A", type="virtual"
        )

        train_stop.train_stopped_signal = {"name": "signal-A", "type": "virtual"}
        assert train_stop.train_stopped_signal == SignalID(
            name="signal-A", type="virtual"
        )

        train_stop.train_stopped_signal = None
        assert train_stop.train_stopped_signal == None

        # Warnings
        with pytest.warns(UnknownSignalWarning):
            train_stop.train_stopped_signal = {
                "name": "wrong-signal",
                "type": "virtual",
            }

        # Errors
        with pytest.raises(DataFormatError):
            train_stop.train_stopped_signal = "wrong signal"
        with pytest.raises(DataFormatError):
            train_stop.train_stopped_signal = TypeError

        train_stop.validate_assignment = "none"
        assert train_stop.validate_assignment == ValidationMode.NONE

        train_stop.train_stopped_signal = "incorrect"
        assert train_stop.train_stopped_signal == "incorrect"
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"train_stopped_signal": "incorrect"},
        }

    def test_set_trains_limit(self):
        train_stop = TrainStop()
        train_stop.signal_limits_trains = True
        assert train_stop.signal_limits_trains == True

        train_stop.signal_limits_trains = None
        assert train_stop.signal_limits_trains == None

        with pytest.raises(DataFormatError):
            train_stop.signal_limits_trains = "wrong"

        train_stop.validate_assignment = "none"
        assert train_stop.validate_assignment == ValidationMode.NONE

        train_stop.signal_limits_trains = "incorrect"
        assert train_stop.signal_limits_trains == "incorrect"
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"set_trains_limit": "incorrect"},
        }

    def test_set_trains_limit_signal(self):
        train_stop = TrainStop()
        train_stop.trains_limit_signal = "signal-A"
        assert train_stop.trains_limit_signal == SignalID(
            name="signal-A", type="virtual"
        )

        train_stop.trains_limit_signal = {"name": "signal-A", "type": "virtual"}
        assert train_stop.trains_limit_signal == SignalID(
            name="signal-A", type="virtual"
        )

        train_stop.trains_limit_signal = None
        assert train_stop.trains_limit_signal == None

        # Warnings
        with pytest.warns(UnknownSignalWarning):
            train_stop.trains_limit_signal = {"name": "wrong-signal", "type": "virtual"}

        # Errors
        with pytest.raises(DataFormatError):
            train_stop.trains_limit_signal = "wrong signal"
        with pytest.raises(DataFormatError):
            train_stop.trains_limit_signal = TypeError

        train_stop.validate_assignment = "none"
        assert train_stop.validate_assignment == ValidationMode.NONE

        train_stop.trains_limit_signal = "incorrect"
        assert train_stop.trains_limit_signal == "incorrect"
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"trains_limit_signal": "incorrect"},
        }

    def test_set_read_trains_count(self):
        train_stop = TrainStop()
        train_stop.read_trains_count = True
        assert train_stop.read_trains_count == True

        train_stop.read_trains_count = None
        assert train_stop.read_trains_count == None

        with pytest.raises(DataFormatError):
            train_stop.read_trains_count = "wrong"

        train_stop.validate_assignment = "none"
        assert train_stop.validate_assignment == ValidationMode.NONE

        train_stop.read_trains_count = "incorrect"
        assert train_stop.read_trains_count == "incorrect"
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"read_trains_count": "incorrect"},
        }

    def test_set_trains_count_signal(self):
        train_stop = TrainStop()
        train_stop.trains_count_signal = "signal-A"
        assert train_stop.trains_count_signal == SignalID(
            name="signal-A", type="virtual"
        )

        train_stop.trains_count_signal = {"name": "signal-A", "type": "virtual"}
        assert train_stop.trains_count_signal == SignalID(
            name="signal-A", type="virtual"
        )

        train_stop.trains_count_signal = None
        assert train_stop.trains_count_signal == None

        # Warnings
        with pytest.warns(UnknownSignalWarning):
            train_stop.trains_count_signal = {"name": "wrong-signal", "type": "virtual"}

        # Errors
        with pytest.raises(DataFormatError):
            train_stop.trains_count_signal = "wrong signal"
        with pytest.raises(DataFormatError):
            train_stop.trains_count_signal = TypeError

        train_stop.validate_assignment = "none"
        assert train_stop.validate_assignment == ValidationMode.NONE

        train_stop.trains_count_signal = "incorrect"
        assert train_stop.trains_count_signal == "incorrect"
        assert train_stop.to_dict() == {
            "name": "train-stop",
            "position": {"x": 1, "y": 1},
            "control_behavior": {"trains_count_signal": "incorrect"},
        }

    def test_power_and_circuit_flags(self):
        for name in train_stops:
            train_stop = TrainStop(name)
            assert train_stop.power_connectable == False
            assert train_stop.dual_power_connectable == False
            assert train_stop.circuit_connectable == True
            assert train_stop.dual_circuit_connectable == False

    def test_double_grid_aligned(self):
        for name in train_stops:
            train_stop = TrainStop(name)
            assert train_stop.double_grid_aligned == True

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

    def test_eq(self):
        stop1 = TrainStop("train-stop")
        stop2 = TrainStop("train-stop")

        assert stop1 == stop2

        stop1.tags = {"some": "stuff"}

        assert stop1 != stop2

        container = Container()

        assert stop1 != container
        assert stop2 != container

        # hashable
        assert isinstance(stop1, Hashable)
