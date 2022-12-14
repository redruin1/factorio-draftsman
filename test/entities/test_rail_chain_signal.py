# test_rail_chain_signal.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import RailChainSignal, rail_chain_signals
from draftsman.error import InvalidEntityError, InvalidSignalError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class RailChainSignalTesting(unittest.TestCase):
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
        with pytest.warns(DraftsmanWarning):
            RailChainSignal("rail-chain-signal", invalid_keyword="whatever")

        # Warn if the rail signal is not placed next to rail
        # TODO (Complex)

        # Errors:
        with pytest.raises(InvalidEntityError):
            RailChainSignal("this is not a rail chain signal")
        with pytest.raises(DataFormatError):
            RailChainSignal(control_behavior={"unused_key": "something"})

    def test_set_blue_output_signal(self):
        rail_signal = RailChainSignal()
        rail_signal.blue_output_signal = "signal-A"
        assert rail_signal.blue_output_signal == {"name": "signal-A", "type": "virtual"}
        assert rail_signal.control_behavior == {
            "blue_output_signal": {"name": "signal-A", "type": "virtual"}
        }
        rail_signal.blue_output_signal = {"name": "signal-A", "type": "virtual"}
        assert rail_signal.control_behavior == {
            "blue_output_signal": {"name": "signal-A", "type": "virtual"}
        }
        rail_signal.blue_output_signal = None
        assert rail_signal.control_behavior == {}
        with pytest.raises(TypeError):
            rail_signal.blue_output_signal = TypeError
        with pytest.raises(InvalidSignalError):
            rail_signal.blue_output_signal = "incorrect"

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

        assert signal1.control_behavior == {
            "red_output_signal": {"name": "signal-A", "type": "virtual"},
            "orange_output_signal": {"name": "signal-B", "type": "virtual"},
            "green_output_signal": {"name": "signal-C", "type": "virtual"},
            "blue_output_signal": {"name": "signal-D", "type": "virtual"},
        }
        assert signal1.tags == {"some": "stuff"}
