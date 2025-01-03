# test_loader.py

from draftsman.entity import Loader, loaders, Container
from draftsman.signatures import ItemFilter
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestLoader:
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Loader("loader", unused_keyword=10).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            Loader("this is not a loader").validate().reissue_all()

        # Errors

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

        assert loader1.filters == [ItemFilter(**{"name": "coal", "index": 1})]
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
