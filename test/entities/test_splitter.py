# test_splitter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import Splitter, splitters
from draftsman.error import InvalidEntityError, InvalidSideError, InvalidItemError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class SplitterTesting(unittest.TestCase):
    def test_constructor_init(self):
        # Valid
        splitter = Splitter(
            "splitter",
            direction=Direction.EAST,
            tile_position=[1, 1],
            input_priority="left",
            output_priority="right",
            filter="small-lamp",
        )
        assert splitter.to_dict() == {
            "name": "splitter",
            "position": {"x": 1.5, "y": 2.0},
            "direction": 2,
            "input_priority": "left",
            "output_priority": "right",
            "filter": "small-lamp",
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            Splitter(position=[0, 0], direction=Direction.WEST, invalid_keyword=5)

        # Errors
        # Raises InvalidEntityID when not in containers
        with pytest.raises(InvalidEntityError):
            Splitter("this is not a splitter")

        # Raises errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            Splitter("splitter", id=25)

        with pytest.raises(TypeError):
            Splitter("splitter", position=TypeError)

        with pytest.raises(ValueError):
            Splitter("splitter", direction="incorrect")

        with pytest.raises(TypeError):
            Splitter("splitter", input_priority=TypeError)

        with pytest.raises(InvalidSideError):
            Splitter("splitter", input_priority="wrong")

        with pytest.raises(TypeError):
            Splitter("splitter", output_priority=TypeError)

        with pytest.raises(InvalidSideError):
            Splitter("splitter", output_priority="wrong")

        with pytest.raises(TypeError):
            Splitter("splitter", filter=TypeError)

        with pytest.raises(InvalidItemError):
            Splitter("splitter", filter="wrong")

    def test_power_and_circuit_flags(self):
        for name in splitters:
            splitter = Splitter(name)
            assert splitter.power_connectable == False
            assert splitter.dual_power_connectable == False
            assert splitter.circuit_connectable == False
            assert splitter.dual_circuit_connectable == False

    def test_mergable_with(self):
        splitter1 = Splitter("splitter")
        splitter2 = Splitter(
            "splitter",
            input_priority="left",
            output_priority="right",
            filter="small-lamp",
            tags={"some": "stuff"},
        )

        assert splitter1.mergable_with(splitter1)

        assert splitter1.mergable_with(splitter2)
        assert splitter2.mergable_with(splitter1)

        splitter2.tile_position = (1, 1)
        assert not splitter1.mergable_with(splitter2)

    def test_merge(self):
        splitter1 = Splitter("splitter")
        splitter2 = Splitter(
            "splitter",
            input_priority="left",
            output_priority="right",
            filter="small-lamp",
            tags={"some": "stuff"},
        )

        splitter1.merge(splitter2)
        del splitter2

        assert splitter1.input_priority == "left"
        assert splitter1.output_priority == "right"
        assert splitter1.filter == "small-lamp"
        assert splitter1.tags == {"some": "stuff"}
