# test_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Pipe, pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class PipeTesting(unittest.TestCase):
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with pytest.warns(DraftsmanWarning):
            Pipe("pipe", unused_keyword=10)

        # Errors
        with pytest.raises(InvalidEntityError):
            Pipe("Ceci n'est pas une pipe.")

    def test_mergable_with(self):
        pipe1 = Pipe("pipe")
        pipe2 = Pipe("pipe", tags={"some": "stuff"})

        assert pipe1.mergable_with(pipe1)

        assert pipe1.mergable_with(pipe2)
        assert pipe2.mergable_with(pipe1)

        pipe2.tile_position = (1, 1)
        assert not pipe1.mergable_with(pipe2)

    def test_merge(self):
        pipe1 = Pipe("pipe")
        pipe2 = Pipe("pipe", tags={"some": "stuff"})

        pipe1.merge(pipe2)
        del pipe2

        assert pipe1.tags == {"some": "stuff"}
