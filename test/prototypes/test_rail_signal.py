# test_rail_signal.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import RailSignal, rail_signals, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class RailSignalTesting(unittest.TestCase):
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
        with pytest.warns(DraftsmanWarning):
            RailSignal("rail-signal", invalid_keyword="whatever")

        # Warn if the rail signal is not placed next to rail
        # TODO (Complex)

        # Errors:
        with pytest.raises(InvalidEntityError):
            RailSignal("this is not a rail signal")
        with pytest.raises(DataFormatError):
            RailSignal(control_behavior={"blue_output_signal": "signal-A"})

    def test_read_signal(self):
        rail_signal = RailSignal()
        rail_signal.read_signal = True
        assert rail_signal.read_signal == True
        assert rail_signal.control_behavior == {"circuit_read_signal": True}
        rail_signal.read_signal = None
        assert rail_signal.control_behavior == {}
        with pytest.raises(TypeError):
            rail_signal.read_signal = "incorrect"

    def test_enable_disable(self):
        rail_signal = RailSignal()
        rail_signal.enable_disable = True
        assert rail_signal.enable_disable == True
        assert rail_signal.control_behavior == {"circuit_close_signal": True}
        rail_signal.enable_disable = None
        assert rail_signal.control_behavior == {}
        with pytest.raises(TypeError):
            rail_signal.enable_disable = "incorrect"

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

        assert signal1.control_behavior == {
            "red_output_signal": {"name": "signal-A", "type": "virtual"},
            "orange_output_signal": {"name": "signal-B", "type": "virtual"},
            "green_output_signal": {"name": "signal-C", "type": "virtual"},
        }
        assert signal1.tags == {"some": "stuff"}

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
