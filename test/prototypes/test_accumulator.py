# test_accumulator.py

from draftsman.classes.vector import Vector
from draftsman.entity import Accumulator, accumulators, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalID
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestAccumulator:
    def test_constructor_init(self):
        accumulator = Accumulator(control_behavior={"output_signal": "signal-B"})
        assert accumulator.to_dict() == {
            "name": accumulators[0],
            "position": accumulator.position.to_dict(),
            "control_behavior": {
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }
        accumulator = Accumulator(
            control_behavior={"output_signal": {"name": "signal-B", "type": "virtual"}}
        )
        assert accumulator.to_dict() == {
            "name": accumulators[0],
            "position": accumulator.position.to_dict(),
            "control_behavior": {
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Accumulator(unused_keyword="whatever")
        with pytest.warns(UnknownKeywordWarning):
            Accumulator(control_behavior={"unused_keyword": "whatever"})
        with pytest.warns(UnknownEntityWarning):
            Accumulator("not an accumulator")

        # Errors
        with pytest.raises(DataFormatError):
            Accumulator(control_behavior="incorrect")
        with pytest.raises(DataFormatError):
            Accumulator(control_behavior={"output_signal": "incorrect"})

    def test_output_signal(self):
        accumulator = Accumulator()
        # String case
        accumulator.output_signal = "signal-D"
        assert accumulator.output_signal == SignalID(**{"name": "signal-D", "type": "virtual"})
        
        # Dict case
        accumulator2 = Accumulator()
        accumulator2.output_signal = accumulator.output_signal
        assert accumulator2.output_signal == accumulator.output_signal

        # None case
        accumulator.output_signal = None
        assert accumulator.output_signal == None

        with pytest.raises(DataFormatError):
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
        assert accumulatorA.output_signal == SignalID(**{"name": "signal-A", "type": "virtual"})

    def test_eq(self):
        accumulatorA = Accumulator("accumulator", tile_position=(0, 0))
        accumulatorB = Accumulator("accumulator", tile_position=(0, 0))

        assert accumulatorA == accumulatorB

        accumulatorA.output_signal = "signal-B" # Make sure it's not default!

        assert accumulatorA != accumulatorB

        container = Container("wooden-chest")

        assert accumulatorA != container
        assert accumulatorB != container

        # hashable
        assert isinstance(accumulatorA, Hashable)
