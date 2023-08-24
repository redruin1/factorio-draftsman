# test_wall.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Wall, walls, Container
from draftsman.error import InvalidEntityError, InvalidSignalError, DataFormatError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class WallTesting(unittest.TestCase):
    def test_constructor_init(self):
        wall = Wall()

        with pytest.warns(DraftsmanWarning):
            Wall(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            Wall("this is not a wall")
        with pytest.raises(DataFormatError):
            Wall(control_behavior={"unused_key": "something"})

    def test_set_enable_disable(self):
        wall = Wall()
        wall.enable_disable = True
        assert wall.enable_disable == True
        assert wall.control_behavior == {"circuit_open_gate": True}
        wall.enable_disable = None
        assert wall.control_behavior == {}
        with pytest.raises(TypeError):
            wall.enable_disable = "incorrect"

    def test_set_read_gate(self):
        wall = Wall()
        wall.read_gate = True
        assert wall.read_gate == True
        assert wall.control_behavior == {"circuit_read_sensor": True}
        wall.read_gate = None
        assert wall.control_behavior == {}
        with pytest.raises(TypeError):
            wall.read_gate = "incorrect"

    def test_set_output_signal(self):
        wall = Wall()
        wall.output_signal = "signal-A"
        assert wall.output_signal == {"name": "signal-A", "type": "virtual"}
        assert wall.control_behavior == {
            "output_signal": {"name": "signal-A", "type": "virtual"}
        }
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.control_behavior == {
            "output_signal": {"name": "signal-A", "type": "virtual"}
        }
        wall.output_signal = None
        assert wall.control_behavior == {}
        with pytest.raises(TypeError):
            wall.output_signal = TypeError
        with pytest.raises(InvalidSignalError):
            wall.output_signal = "incorrect"

    def test_mergable_with(self):
        wall1 = Wall("stone-wall")
        wall2 = Wall("stone-wall", tags={"some": "stuff"})

        assert wall1.mergable_with(wall1)

        assert wall1.mergable_with(wall2)
        assert wall2.mergable_with(wall1)

        wall2.tile_position = (1, 1)
        assert not wall1.mergable_with(wall2)

    def test_merge(self):
        wall1 = Wall("stone-wall")
        wall2 = Wall("stone-wall", tags={"some": "stuff"})

        wall1.merge(wall2)
        del wall2

        assert wall1.tags == {"some": "stuff"}

    def test_eq(self):
        wall1 = Wall("stone-wall")
        wall2 = Wall("stone-wall")

        assert wall1 == wall2

        wall1.tags = {"some": "stuff"}

        assert wall1 != wall2

        container = Container()

        assert wall1 != container
        assert wall2 != container

        # hashable
        assert isinstance(wall1, Hashable)
