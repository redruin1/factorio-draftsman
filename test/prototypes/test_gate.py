# test_gate.py

from draftsman.constants import Direction
from draftsman.entity import Gate, gates, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_gate():
    return Gate(
        "gate",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        tags={"blah": "blah"},
    )


class TestGate:
    def test_contstructor_init(self):
        gate = Gate("gate")

        with pytest.warns(UnknownEntityWarning):
            Gate("this is not a gate").validate().reissue_all()

    def test_mergable_with(self):
        gate1 = Gate("gate", tile_position=(1, 1))
        gate2 = Gate("gate", position=(1.5, 1.5), tags={"some": "stuff"})

        assert gate1.mergable_with(gate1)

        assert gate1.mergable_with(gate2)
        assert gate2.mergable_with(gate1)

        gate2.direction = Direction.EAST
        assert not gate1.mergable_with(gate2)

    def test_merge(self):
        gate1 = Gate("gate", tile_position=(1, 1))
        gate2 = Gate("gate", position=(1.5, 1.5), tags={"some": "stuff"})

        gate1.merge(gate2)
        del gate2

        assert gate1.tags == {"some": "stuff"}

    def test_eq(self):
        gate1 = Gate("gate")
        gate2 = Gate("gate")

        assert gate1 == gate2

        gate1.tags = {"some": "stuff"}

        assert gate1 != gate2

        container = Container()

        assert gate1 != container
        assert gate2 != container

        # hashable
        assert isinstance(gate1, Hashable)
