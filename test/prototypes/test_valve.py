# test_underground_pipe.py

from draftsman.constants import Direction
from draftsman.entity import Valve, Container, valves
from draftsman.error import InvalidEntityError
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
            pipe = Valve.from_dict(
                {"name": "top-up-valve", "unused_keyword": 10}
            )

        # Errors
        with pytest.warns(UnknownEntityWarning):
            pipe = Valve("this is not an valve")

    def test_power_and_circuit_flags(self):
        for name in valves:
            underground_belt = Valve(name)
            assert underground_belt.power_connectable == False
            assert underground_belt.dual_power_connectable == False
            assert underground_belt.circuit_connectable == False
            assert underground_belt.dual_circuit_connectable == False

    def test_mergable_with(self):
        pipe1 = Valve("top-up-valve")
        pipe2 = Valve("top-up-valve", tags={"some": "stuff"})

        assert pipe1.mergable_with(pipe1)

        assert pipe1.mergable_with(pipe2)
        assert pipe2.mergable_with(pipe1)

        pipe2.tile_position = (1, 1)
        assert not pipe1.mergable_with(pipe2)

    def test_merge(self):
        pipe1 = Valve("top-up-valve")
        pipe2 = Valve("top-up-valve", tags={"some": "stuff"})

        pipe1.merge(pipe2)
        del pipe2

        assert pipe1.tags == {"some": "stuff"}

    def test_eq(self):
        pipe1 = Valve("top-up-valve")
        pipe2 = Valve("top-up-valve")

        assert pipe1 == pipe2

        pipe1.tags = {"some": "stuff"}

        assert pipe1 != pipe2

        container = Container()

        assert pipe1 != container
        assert pipe2 != container

        # hashable
        assert isinstance(pipe1, Hashable)
