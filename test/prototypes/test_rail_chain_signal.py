# test_rail_chain_signal.py

from draftsman.entity import RailChainSignal, rail_chain_signals, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalID
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestRailChainSignal:
    def test_constructor_init(self):
        rail_signal = RailChainSignal("rail-chain-signal", control_behavior={})
        assert rail_signal.to_dict() == {
            "name": "rail-chain-signal",
            "position": {"x": 0.5, "y": 0.5},
        }

        rail_signal = RailChainSignal(
            "rail-chain-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
                "blue_output_signal": "signal-D",
            },
        )
        assert rail_signal.to_dict() == {
            "name": "rail-chain-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
                "blue_output_signal": {"name": "signal-D", "type": "virtual"},
            },
        }

        rail_signal = RailChainSignal(
            "rail-chain-signal",
            control_behavior={
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
                "blue_output_signal": {"name": "signal-D", "type": "virtual"},
            },
        )
        assert rail_signal.to_dict() == {
            "name": "rail-chain-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "red_output_signal": {"name": "signal-A", "type": "virtual"},
                "orange_output_signal": {"name": "signal-B", "type": "virtual"},
                "green_output_signal": {"name": "signal-C", "type": "virtual"},
                "blue_output_signal": {"name": "signal-D", "type": "virtual"},
            },
        }

        # Warnings:
        with pytest.warns(UnknownKeywordWarning):
            RailChainSignal("rail-chain-signal", invalid_keyword="whatever").validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            RailChainSignal("this is not a rail chain signal").validate().reissue_all()

        # Errors:
        with pytest.raises(DataFormatError):
            RailChainSignal(control_behavior="incorrect").validate().reissue_all()

    def test_set_blue_output_signal(self):
        rail_signal = RailChainSignal()
        rail_signal.blue_output_signal = "signal-A"
        assert rail_signal.blue_output_signal == SignalID(
            name="signal-A", type="virtual"
        )

        rail_signal.blue_output_signal = {"name": "signal-A", "type": "virtual"}
        assert rail_signal.blue_output_signal == SignalID(
            name="signal-A", type="virtual"
        )

        rail_signal.blue_output_signal = None
        assert rail_signal.blue_output_signal == None

        with pytest.raises(DataFormatError):
            rail_signal.blue_output_signal = TypeError
        with pytest.raises(DataFormatError):
            rail_signal.blue_output_signal = "incorrect"

        rail_signal.validate_assignment = "none"

        rail_signal.blue_output_signal = "incorrect"
        assert rail_signal.blue_output_signal == "incorrect"
        assert rail_signal.to_dict() == {
            "name": "rail-chain-signal",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"blue_output_signal": "incorrect"},
        }

    def test_mergable_with(self):
        signal1 = RailChainSignal("rail-chain-signal")
        signal2 = RailChainSignal(
            "rail-chain-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
                "blue_output_signal": "signal-D",
            },
            tags={"some": "stuff"},
        )

        assert signal1.mergable_with(signal1)

        assert signal1.mergable_with(signal2)
        assert signal2.mergable_with(signal1)

        signal2.tile_position = (1, 1)
        assert not signal1.mergable_with(signal2)

    def test_merge(self):
        signal1 = RailChainSignal("rail-chain-signal")
        signal2 = RailChainSignal(
            "rail-chain-signal",
            control_behavior={
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
                "blue_output_signal": "signal-D",
            },
            tags={"some": "stuff"},
        )

        signal1.merge(signal2)
        del signal2

        assert signal1.control_behavior == RailChainSignal.Format.ControlBehavior(
            **{
                "red_output_signal": "signal-A",
                "orange_output_signal": "signal-B",
                "green_output_signal": "signal-C",
                "blue_output_signal": "signal-D",
            }
        )
        assert signal1.tags == {"some": "stuff"}

        assert signal1.to_dict()["control_behavior"] == {
            "red_output_signal": {"name": "signal-A", "type": "virtual"},
            "orange_output_signal": {"name": "signal-B", "type": "virtual"},
            "green_output_signal": {"name": "signal-C", "type": "virtual"},
            "blue_output_signal": {"name": "signal-D", "type": "virtual"},
        }

    def test_eq(self):
        signal1 = RailChainSignal("rail-chain-signal")
        signal2 = RailChainSignal("rail-chain-signal")

        assert signal1 == signal2

        signal1.tags = {"some": "stuff"}

        assert signal1 != signal2

        container = Container()

        assert signal1 != container
        assert signal2 != container

        # hashable
        assert isinstance(signal1, Hashable)
