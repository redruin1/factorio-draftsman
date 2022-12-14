# test_underground_belt.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import UndergroundBelt, underground_belts
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class UndergroundBeltTesting(unittest.TestCase):
    def test_constructor_init(self):
        # Valid
        underground_belt = UndergroundBelt(
            "underground-belt",
            direction=Direction.EAST,
            tile_position=[1, 1],
            io_type="output",
        )
        assert underground_belt.to_dict() == {
            "name": "underground-belt",
            "position": {"x": 1.5, "y": 1.5},
            "direction": 2,
            "type": "output",
        }

        underground_belt = UndergroundBelt("underground-belt", type="output")
        assert underground_belt.to_dict() == {
            "name": "underground-belt",
            "position": {"x": 0.5, "y": 0.5},
            "type": "output",
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            UndergroundBelt(
                position=[0, 0], direction=Direction.WEST, invalid_keyword=5
            )

        # Errors
        # Raises InvalidEntityID when not in containers
        with pytest.raises(InvalidEntityError):
            UndergroundBelt("this is not an underground belt")

        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            UndergroundBelt("underground-belt", id=25)

        with pytest.raises(TypeError):
            UndergroundBelt("underground-belt", position=TypeError)

        with pytest.raises(ValueError):
            UndergroundBelt("underground-belt", direction="incorrect")

        with pytest.raises(ValueError):
            UndergroundBelt("underground-belt", type="incorrect")

        with pytest.raises(ValueError):
            UndergroundBelt("underground-belt", io_type="incorrect")

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
