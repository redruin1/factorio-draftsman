# test_rail_signal.py

from draftsman.constants import ValidationMode
from draftsman.entity import RailSignal, rail_signals, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalID
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    UnknownSignalWarning,
)

from collections.abc import Hashable
import pytest


class TestRailSignal:
    def test_constructor_init(self):
        rail_signal = RailSignal("rail-signal", control_behavior={})
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal = RailSignal(
            "rail-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
            },
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
            },
        }

        rail_signal = RailSignal(
            "rail-signal",
            control_behavior={
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
            },
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
            },
        }

        # Warnings:
        with pytest.warns(UnknownKeywordWarning):
            RailSignal("rail-signal", invalid_keyword="whatever")
        with pytest.warns(UnknownEntityWarning):
            RailSignal("this is not a rail signal")

        # Errors:
        with pytest.raises(DataFormatError):
            RailSignal(control_behavior="incorrect")

    def test_flags(self):
        assert RailSignal("rail-signal").rotatable == True
        assert RailSignal("rail-signal").square == True

    def test_enable_disable(self):
        rail_signal = RailSignal("rail-signal")
        rail_signal.enable_disable = True
        assert rail_signal.enable_disable == True

        rail_signal.enable_disable = None
        assert rail_signal.enable_disable == None

        with pytest.raises(DataFormatError):
            rail_signal.enable_disable = "incorrect"

        rail_signal.validate_assignment = "none"
        assert rail_signal.validate_assignment == ValidationMode.NONE

        rail_signal.enable_disable = "incorrect"
        assert rail_signal.enable_disable == "incorrect"
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_close_signal": "incorrect"},
        }

    def test_read_signal(self):
        rail_signal = RailSignal("rail-signal")
        rail_signal.read_signal = True
        assert rail_signal.read_signal == True

        rail_signal.read_signal = None
        assert rail_signal.read_signal == None

        with pytest.raises(DataFormatError):
            rail_signal.read_signal = "incorrect"

        rail_signal.validate_assignment = "none"
        assert rail_signal.validate_assignment == ValidationMode.NONE

        rail_signal.read_signal = "incorrect"
        assert rail_signal.read_signal == "incorrect"
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_read_signal": "incorrect"},
        }

    def test_red_output_signal(self):
        rail_signal = RailSignal("rail-signal")
        assert rail_signal.red_output_signal == SignalID(
            name="signal-red", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal.red_output_signal = "signal-A"
        assert rail_signal.red_output_signal == SignalID(
            name="signal-A", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "signal-A", "type": "virtual"}
            },
        }

        rail_signal.red_output_signal = {"name": "signal-B", "type": "virtual"}
        assert rail_signal.red_output_signal == SignalID(
            name="signal-B", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }

        with pytest.warns(UnknownSignalWarning):
            rail_signal.red_output_signal = {"name": "unknown", "type": "virtual"}
        assert rail_signal.red_output_signal == SignalID(name="unknown", type="virtual")
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "unknown", "type": "virtual"}
            },
        }

        with pytest.raises(DataFormatError):
            rail_signal.red_output_signal = "incorrect"

        rail_signal.validate_assignment = "none"
        assert rail_signal.validate_assignment == ValidationMode.NONE

        rail_signal.red_output_signal = "incorrect"
        assert rail_signal.red_output_signal == "incorrect"
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"red_output_signal": "incorrect"},
        }

    def test_yellow_output_signal(self):
        rail_signal = RailSignal("rail-signal")
        assert rail_signal.yellow_output_signal == SignalID(
            name="signal-yellow", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal.yellow_output_signal = "signal-A"
        assert rail_signal.yellow_output_signal == SignalID(
            name="signal-A", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "orange_output_signal": {"name": "signal-A", "type": "virtual"}
            },
        }

        rail_signal.yellow_output_signal = {"name": "signal-B", "type": "virtual"}
        assert rail_signal.yellow_output_signal == SignalID(
            name="signal-B", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "orange_output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }

        with pytest.warns(UnknownSignalWarning):
            rail_signal.yellow_output_signal = {"name": "unknown", "type": "virtual"}
        assert rail_signal.yellow_output_signal == SignalID(
            name="unknown", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "orange_output_signal": {"name": "unknown", "type": "virtual"}
            },
        }

        with pytest.raises(DataFormatError):
            rail_signal.yellow_output_signal = "incorrect"

        rail_signal.validate_assignment = "none"
        assert rail_signal.validate_assignment == ValidationMode.NONE

        rail_signal.yellow_output_signal = "incorrect"
        assert rail_signal.yellow_output_signal == "incorrect"
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"orange_output_signal": "incorrect"},
        }

    def test_green_output_signal(self):
        rail_signal = RailSignal("rail-signal")
        assert rail_signal.green_output_signal == SignalID(
            name="signal-green", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal.green_output_signal = "signal-A"
        assert rail_signal.green_output_signal == SignalID(
            name="signal-A", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "green_output_signal": {"name": "signal-A", "type": "virtual"}
            },
        }

        rail_signal.green_output_signal = {"name": "signal-B", "type": "virtual"}
        assert rail_signal.green_output_signal == SignalID(
            name="signal-B", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "green_output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }

        with pytest.warns(UnknownSignalWarning):
            rail_signal.green_output_signal = {"name": "unknown", "type": "virtual"}
        assert rail_signal.green_output_signal == SignalID(
            name="unknown", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "green_output_signal": {"name": "unknown", "type": "virtual"}
            },
        }

        with pytest.raises(DataFormatError):
            rail_signal.green_output_signal = "incorrect"

        rail_signal.validate_assignment = "none"
        assert rail_signal.validate_assignment == ValidationMode.NONE

        rail_signal.green_output_signal = "incorrect"
        assert rail_signal.green_output_signal == "incorrect"
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"green_output_signal": "incorrect"},
        }

    def test_mergable_with(self):
        signal1 = RailSignal("rail-signal")
        signal2 = RailSignal(
            "rail-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
            },
            tags={"some": "stuff"},
        )

        assert signal1.mergable_with(signal1)

        assert signal1.mergable_with(signal2)
        assert signal2.mergable_with(signal1)

        signal2.tile_position = (1, 1)
        assert not signal1.mergable_with(signal2)

    def test_merge(self):
        signal1 = RailSignal("rail-signal")
        signal2 = RailSignal(
            "rail-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
            },
            tags={"some": "stuff"},
        )

        signal1.merge(signal2)
        del signal2

        assert signal1.control_behavior == RailSignal.Format.ControlBehavior(
            **{
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
            }
        )
        assert signal1.tags == {"some": "stuff"}

        assert signal1.to_dict()["control_behavior"] == {
            "red_output_signal": {"name": "signal-A", "type": "virtual"},
            "orange_output_signal": {"name": "signal-B", "type": "virtual"},
            "green_output_signal": {"name": "signal-C", "type": "virtual"},
        }

    def test_eq(self):
        signal1 = RailSignal("rail-signal")
        signal2 = RailSignal("rail-signal")

        assert signal1 == signal2

        signal1.tags = {"some": "stuff"}

        assert signal1 != signal2

        container = Container()

        assert signal1 != container
        assert signal2 != container

        # hashable
        assert isinstance(signal1, Hashable)
