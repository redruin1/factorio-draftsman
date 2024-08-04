# test_generator.py

from draftsman.entity import Generator, generators, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestGenerator:
    def test_constructor_init(self):
        generator = Generator("steam-engine")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Generator("steam-engine", unused_keyword="whatever").validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            Generator("not a generator").validate().reissue_all()

        # Errors

    def test_mergable_with(self):
        gen1 = Generator("steam-engine")
        gen2 = Generator("steam-engine", tags={"some": "stuff"})

        assert gen1.mergable_with(gen1)

        assert gen1.mergable_with(gen2)
        assert gen2.mergable_with(gen1)

        gen2.tile_position = (10, 10)
        assert not gen1.mergable_with(gen2)

    def test_merge(self):
        gen1 = Generator("steam-engine")
        gen2 = Generator("steam-engine", tags={"some": "stuff"})

        gen1.merge(gen2)
        del gen2

        assert gen1.tags == {"some": "stuff"}

    def test_eq(self):
        generator1 = Generator("steam-engine")
        generator2 = Generator("steam-engine")

        assert generator1 == generator2

        generator1.tags = {"some": "stuff"}

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
