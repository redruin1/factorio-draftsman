# test_underground_pipe.py

from draftsman.constants import Direction
from draftsman.entity import Valve, Container, valves
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_valve():
    if len(valves) == 0:
        return None
    return Valve(
        "top-up-valve",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


@pytest.mark.skipif(len(valves) == 0, reason="No valves to test")
class TestValve:
    def test_constructor_init(self):
        # pipe = UndergroundPipe("pipe-to-ground")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            valve = Valve.from_dict({"name": "top-up-valve", "unused_keyword": 10})

        # Errors
        with pytest.warns(UnknownEntityWarning):
            valve = Valve("this is not an valve")

    def test_power_and_circuit_flags(self):
        for name in valves:
            valve = Valve(name)
            assert valve.power_connectable == False
            assert valve.dual_power_connectable == False
            assert valve.circuit_connectable == False
            assert valve.dual_circuit_connectable == False

    def test_threshold(self):
        valve = Valve("top-up-valve")
        assert valve.threshold == 0.5

        with pytest.warns(UnknownEntityWarning):
            valve = Valve("unknown-valve")
        assert valve.threshold is None

    def test_mergable_with(self):
        valve1 = Valve("top-up-valve")
        valve2 = Valve("top-up-valve", tags={"some": "stuff"})

        assert valve1.mergable_with(valve1)

        assert valve1.mergable_with(valve2)
        assert valve2.mergable_with(valve1)

        valve2.tile_position = (1, 1)
        assert not valve1.mergable_with(valve2)

    def test_merge(self):
        valve1 = Valve("top-up-valve")
        valve2 = Valve("top-up-valve", tags={"some": "stuff"})

        valve1.merge(valve2)
        del valve2

        assert valve1.tags == {"some": "stuff"}

    def test_eq(self):
        valve1 = Valve("top-up-valve")
        valve2 = Valve("top-up-valve")

        assert valve1 == valve2

        valve1.tags = {"some": "stuff"}

        assert valve1 != valve2

        container = Container()

        assert valve1 != container
        assert valve2 != container

        # hashable
        assert isinstance(valve1, Hashable)
