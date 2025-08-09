# test_underground_belt.py

from draftsman.constants import Direction, LegacyDirection
from draftsman.entity import UndergroundBelt, underground_belts, Container
from draftsman.error import DataFormatError, InvalidEntityError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_underground_belt():
    return UndergroundBelt(
        "underground-belt",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        io_type="output",
        tags={"blah": "blah"},
    )


class TestUndergroundBelt:
    def test_constructor_init(self):
        # Valid
        underground_belt = UndergroundBelt("underground-belt")
        assert underground_belt.to_dict() == {
            "name": "underground-belt",
            "position": {"x": 0.5, "y": 0.5},
        }

        underground_belt = UndergroundBelt(
            "underground-belt",
            direction=Direction.EAST,
            tile_position=[1, 1],
            io_type="output",
        )
        assert underground_belt.to_dict(version=(1, 0)) == {
            "name": "underground-belt",
            "position": {"x": 1.5, "y": 1.5},
            "direction": LegacyDirection.EAST,
            "type": "output",
        }
        assert underground_belt.to_dict(version=(2, 0)) == {
            "name": "underground-belt",
            "position": {"x": 1.5, "y": 1.5},
            "direction": Direction.EAST,
            "type": "output",
        }

        underground_belt = UndergroundBelt.from_dict(
            {"name": "underground-belt", "type": "output"}
        )
        assert underground_belt.to_dict() == {
            "name": "underground-belt",
            "position": {"x": 0.5, "y": 0.5},
            "type": "output",
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            underground_belt = UndergroundBelt.from_dict(
                {
                    "name": "underground-belt",
                    "direction": Direction.WEST,
                    "invalid_keyword": 5,
                },
                version=(2, 0),
            )

        # Not in Underground Belts
        with pytest.warns(UnknownEntityWarning):
            underground_belt = UndergroundBelt("this is not an underground belt")

        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            underground_belt = UndergroundBelt("underground-belt", id=25)

        with pytest.raises(DataFormatError):
            underground_belt = UndergroundBelt("underground-belt", position=TypeError)

        with pytest.raises(DataFormatError):
            underground_belt = UndergroundBelt(
                "underground-belt", direction="incorrect"
            )

        with pytest.raises(DataFormatError):
            underground_belt = UndergroundBelt.from_dict(
                {"name": "underground-belt", "type": "incorrect"}
            )

        with pytest.raises(DataFormatError):
            underground_belt = UndergroundBelt("underground-belt", io_type="incorrect")

    def test_power_and_circuit_flags(self):
        for name in underground_belts:
            underground_belt = UndergroundBelt(name)
            assert underground_belt.power_connectable == False
            assert underground_belt.dual_power_connectable == False
            assert underground_belt.circuit_connectable == False
            assert underground_belt.dual_circuit_connectable == False

    def test_mergable_with(self):
        belt1 = UndergroundBelt("underground-belt")
        belt2 = UndergroundBelt(
            "underground-belt", io_type="output", tags={"some": "stuff"}
        )

        assert belt1.mergable_with(belt1)

        assert belt1.mergable_with(belt2)
        assert belt2.mergable_with(belt1)

        belt2.tile_position = (1, 1)
        assert not belt1.mergable_with(belt2)

    def test_merge(self):
        belt1 = UndergroundBelt("underground-belt")
        belt2 = UndergroundBelt(
            "underground-belt", io_type="output", tags={"some": "stuff"}
        )

        belt1.merge(belt2)
        del belt2

        assert belt1.io_type == "output"
        assert belt1.tags == {"some": "stuff"}

    def test_eq(self):
        belt1 = UndergroundBelt("underground-belt")
        belt2 = UndergroundBelt("underground-belt")

        assert belt1 == belt2

        belt1.tags = {"some": "stuff"}

        assert belt1 != belt2

        container = Container()

        assert belt1 != container
        assert belt2 != container

        # hashable
        assert isinstance(belt1, Hashable)
