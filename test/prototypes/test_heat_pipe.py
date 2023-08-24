# test_heat_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import HeatPipe, heat_pipes, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class HeatPipeTesting(unittest.TestCase):
    def test_constructor_init(self):
        heat_pipe = HeatPipe()

        # Warnings
        with pytest.warns(DraftsmanWarning):
            HeatPipe(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            HeatPipe("not a heat pipe")

    def test_mergable_with(self):
        pipe1 = HeatPipe("heat-pipe")
        pipe2 = HeatPipe("heat-pipe", tags={"some": "stuff"})

        assert pipe1.mergable_with(pipe1)

        assert pipe1.mergable_with(pipe2)
        assert pipe2.mergable_with(pipe1)

        pipe2.tile_position = (1, 1)
        assert not pipe1.mergable_with(pipe2)

    def test_merge(self):
        pipe1 = HeatPipe("heat-pipe")
        pipe2 = HeatPipe("heat-pipe", tags={"some": "stuff"})

        pipe1.merge(pipe2)
        del pipe2

        assert pipe1.tags == {"some": "stuff"}

    def test_eq(self):
        pipe1 = HeatPipe("heat-pipe")
        pipe2 = HeatPipe("heat-pipe")

        assert pipe1 == pipe2

        pipe1.tags = {"some": "stuff"}

        assert pipe1 != pipe2

        container = Container()

        assert pipe1 != container
        assert pipe2 != container

        # hashable
        assert isinstance(pipe1, Hashable)
