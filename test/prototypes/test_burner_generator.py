# test_burner_generator.py

from draftsman.entity import BurnerGenerator, burner_generators, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestBurnerGenerator:
    def test_contstructor_init(self):
        generator = BurnerGenerator("burner-generator")

        with pytest.warns(UnknownKeywordWarning):
            BurnerGenerator(unused_keyword="whatever")

        with pytest.warns(UnknownEntityWarning):
            BurnerGenerator("this is not a burner generator")

    def test_mergable_with(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator", tags={"some": "stuff"})

        assert generator1.mergable_with(generator2)
        assert generator2.mergable_with(generator1)

        generator2.tile_position = [-10, -10]
        assert not generator1.mergable_with(generator2)

    def test_merge(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator", tags={"some": "stuff"})

        generator1.merge(generator2)
        del generator2

        assert generator1.tags == {"some": "stuff"}

    def test_eq(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator")

        assert generator1 == generator2

        generator1.tags = {"some": "stuff"}

        assert generator1 != generator2

        container = Container()

        assert generator1 != container
        assert generator2 != container

        # hashable
        assert isinstance(generator1, Hashable)
