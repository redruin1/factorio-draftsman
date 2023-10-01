# test_accumulator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.vector import Vector
from draftsman.entity import Accumulator, accumulators, Container
from draftsman.error import InvalidEntityError, InvalidSignalError, DataFormatError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class AccumulatorTesting(unittest.TestCase):
    def test_constructor_init(self):
        accumulator = Accumulator(control_behavior={"output_signal": "signal-A"})
        assert accumulator.to_dict() == {
            "name": accumulators[0],
            "position": accumulator.position.to_dict(),
            "control_behavior": {
                "output_signal": {"name": "signal-A", "type": "virtual"}
            },
        }
        accumulator = Accumulator(
            control_behavior={"output_signal": {"name": "signal-A", "type": "virtual"}}
        )
        assert accumulator.to_dict() == {
            "name": accumulators[0],
            "position": accumulator.position.to_dict(),
            "control_behavior": {
                "output_signal": {"name": "signal-A", "type": "virtual"}
            },
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            Accumulator(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            Accumulator("not an accumulator")
        # TODO: move to validate
        # with pytest.raises(DataFormatError):
        #     Accumulator(control_behavior={"output_signal": "incorrect"})

    def test_output_signal(self):
        accumulator = Accumulator()
        # String case
        accumulator.output_signal = "signal-D"
        assert accumulator.output_signal == {"name": "signal-D", "type": "virtual"}
        assert accumulator.control_behavior == {
            "output_signal": {"name": "signal-D", "type": "virtual"}
        }
        # Dict case
        accumulator2 = Accumulator()
        accumulator2.output_signal = accumulator.output_signal
        assert accumulator2.output_signal == accumulator.output_signal
        assert accumulator2.control_behavior == {
            "output_signal": {"name": "signal-D", "type": "virtual"}
        }

        # None case
        accumulator.output_signal = None
        assert accumulator.control_behavior == {}
        with pytest.raises(InvalidSignalError):
            accumulator.output_signal = "incorrect"
        with pytest.raises(DataFormatError):
            accumulator.output_signal = {"incorrectly": "formatted"}

    def test_mergable(self):
        accumulatorA = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB = Accumulator("accumulator", tile_position=(0, 0))

        # Compatible
        assert accumulatorA.mergable_with(accumulatorB) == True

        accumulatorA.output_signal = "signal-A"
        assert accumulatorA.mergable_with(accumulatorB) == True

        # Incompatible
        assert accumulatorA.mergable_with(Container()) == False

        accumulatorA.tile_position = (2, 0)
        assert accumulatorA.mergable_with(accumulatorB) == False

        accumulatorA.tile_position = (0, 0)
        accumulatorA.id = "something"
        assert accumulatorA.mergable_with(accumulatorB) == False

    def test_merge(self):
        accumulatorA = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB.output_signal = "signal-A"

        accumulatorA.merge(accumulatorB)
        assert accumulatorA.name == "accumulator"
        assert accumulatorA.tile_position == Vector(0, 0)
        assert accumulatorA.tile_position.to_dict() == {"x": 0, "y": 0}
        assert accumulatorA.output_signal == {"name": "signal-A", "type": "virtual"}

    def test_eq(self):
        accumulatorA = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB = Accumulator("accumulator", tile_position=(0, 0))

        assert accumulatorA == accumulatorB

        accumulatorA.output_signal = "signal-A"

        assert accumulatorA != accumulatorB

        container = Container("wooden-chest")

        assert accumulatorA != container
        assert accumulatorB != container

        # hashable
        assert isinstance(accumulatorA, Hashable)
