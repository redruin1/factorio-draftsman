# test_rail_signal.py

from draftsman.constants import ValidationMode
from draftsman.entity import RailSignal, rail_signals, Container
from draftsman.error import DataFormatError, IncompleteSignalError
from draftsman.signatures import AttrsSignalID
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    UnknownSignalWarning,
)

from collections.abc import Hashable
import pytest


class TestRailSignal:
    def test_constructor_init(self):
        rail_signal = RailSignal("rail-signal")
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal = RailSignal(
            "rail-signal",
            red_output_signal="signal-A",
            yellow_output_signal="signal-B",
            green_output_signal="signal-C",
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "yellow_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
            },
        }

        rail_signal = RailSignal(
            "rail-signal",
            red_output_signal={"name": "signal-A", "type": "virtual"},
            yellow_output_signal={"name": "signal-B", "type": "virtual"},
            green_output_signal={"name": "signal-C", "type": "virtual"},
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "yellow_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
            },
        }

        # Warnings:
        with pytest.warns(UnknownKeywordWarning):
            RailSignal.from_dict(
                {"name": "rail-signal", "invalid_keyword": "whatever"}
            ).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            RailSignal("this is not a rail signal").validate().reissue_all()

        # Errors:
        with pytest.raises(DataFormatError):
            RailSignal(tags="incorrect").validate().reissue_all()

    def test_1_0_serialization(self):
        signal = RailSignal("rail-signal", yellow_output_signal="signal-T")
        assert signal.to_dict(version=(2, 0)) == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "yellow_output_signal": {"name": "signal-T", "type": "virtual"},
            },
        }
        assert signal.to_dict(version=(1, 0)) == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "orange_output_signal": {"name": "signal-T", "type": "virtual"},
            },
        }

    def test_flags(self):
        for name in rail_signals:
            signal = RailSignal(name)
            assert signal.rotatable == True
            assert signal.square == True
            assert signal.power_connectable == False
            assert signal.dual_power_connectable == False
            assert signal.circuit_connectable == True
            assert signal.dual_circuit_connectable == False

    def test_enable_disable(self):
        rail_signal = RailSignal("rail-signal")
        rail_signal.enable_disable == False

        rail_signal.enable_disable = True
        assert rail_signal.enable_disable == True

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
        assert rail_signal.read_signal == True

        rail_signal.read_signal = False
        assert rail_signal.read_signal == False

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
        assert rail_signal.red_output_signal == AttrsSignalID(
            name="signal-red", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal.red_output_signal = "signal-A"
        assert rail_signal.red_output_signal == AttrsSignalID(
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
        assert rail_signal.red_output_signal == AttrsSignalID(
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
            assert rail_signal.red_output_signal == AttrsSignalID(
                name="unknown", type="virtual"
            )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "unknown", "type": "virtual"}
            },
        }

        with pytest.raises(IncompleteSignalError):
            rail_signal.red_output_signal = "incorrect"

    def test_yellow_output_signal(self):
        rail_signal = RailSignal("rail-signal")
        assert rail_signal.yellow_output_signal == AttrsSignalID(
            name="signal-yellow", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal.yellow_output_signal = "signal-A"
        assert rail_signal.yellow_output_signal == AttrsSignalID(
            name="signal-A", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "yellow_output_signal": {"name": "signal-A", "type": "virtual"}
            },
        }

        rail_signal.yellow_output_signal = {"name": "signal-B", "type": "virtual"}
        assert rail_signal.yellow_output_signal == AttrsSignalID(
            name="signal-B", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "yellow_output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }

        with pytest.warns(UnknownSignalWarning):
            rail_signal.yellow_output_signal = {"name": "unknown", "type": "virtual"}
            assert rail_signal.yellow_output_signal == AttrsSignalID(
                name="unknown", type="virtual"
            )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "yellow_output_signal": {"name": "unknown", "type": "virtual"}
            },
        }

        with pytest.raises(IncompleteSignalError):
            rail_signal.yellow_output_signal = "incorrect"

    def test_green_output_signal(self):
        rail_signal = RailSignal("rail-signal")
        assert rail_signal.green_output_signal == AttrsSignalID(
            name="signal-green", type="virtual"
        )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal.green_output_signal = "signal-A"
        assert rail_signal.green_output_signal == AttrsSignalID(
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
        assert rail_signal.green_output_signal == AttrsSignalID(
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
            assert rail_signal.green_output_signal == AttrsSignalID(
                name="unknown", type="virtual"
            )
        assert rail_signal.to_dict() == {
            "name": "rail-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "green_output_signal": {"name": "unknown", "type": "virtual"}
            },
        }

        with pytest.raises(IncompleteSignalError):
            rail_signal.green_output_signal = "incorrect"

    def test_mergable_with(self):
        signal1 = RailSignal("rail-signal")
        signal2 = RailSignal(
            "rail-signal",
            red_output_signal="signal-A",
            yellow_output_signal="signal-B",
            green_output_signal="signal-C",
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
            red_output_signal="signal-A",
            yellow_output_signal="signal-B",
            green_output_signal="signal-C",
            tags={"some": "stuff"},
        )

        signal1.merge(signal2)
        del signal2

        assert signal1.red_output_signal == AttrsSignalID(
            name="signal-A", type="virtual"
        )
        assert signal1.yellow_output_signal == AttrsSignalID(
            name="signal-B", type="virtual"
        )
        assert signal1.green_output_signal == AttrsSignalID(
            name="signal-C", type="virtual"
        )
        assert signal1.tags == {"some": "stuff"}

        assert signal1.to_dict()["control_behavior"] == {
            "red_output_signal": {"name": "signal-A", "type": "virtual"},
            "yellow_output_signal": {"name": "signal-B", "type": "virtual"},
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
