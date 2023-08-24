# test_loader.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Loader, loaders, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LoaderTesting(unittest.TestCase):
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with pytest.warns(DraftsmanWarning):
            Loader("loader", unused_keyword=10)

        # Errors
        with pytest.raises(InvalidEntityError):
            Loader("this is not a loader")

    def test_mergable_with(self):
        loader1 = Loader()
        loader2 = Loader(
            filters=[{"name": "coal", "index": 1}],
            io_type="input",
            tags={"some": "stuff"},
        )

        assert loader1.mergable_with(loader1)

        assert loader1.mergable_with(loader2)
        assert loader2.mergable_with(loader1)

        loader2.tile_position = (1, 1)
        assert not loader1.mergable_with(loader2)

    def test_merge(self):
        loader1 = Loader()
        loader2 = Loader(
            filters=[{"name": "coal", "index": 1}],
            io_type="input",
            tags={"some": "stuff"},
        )

        loader1.merge(loader2)
        del loader2

        assert loader1.filters == [{"name": "coal", "index": 1}]
        assert loader1.io_type == "input"
        assert loader1.tags == {"some": "stuff"}

    def test_eq(self):
        loader1 = Loader()
        loader2 = Loader()

        assert loader1 == loader2

        loader1.tags = {"some": "stuff"}

        assert loader1 != loader2

        container = Container()

        assert loader1 != container
        assert loader2 != container

        # hashable
        assert isinstance(loader1, Hashable)
