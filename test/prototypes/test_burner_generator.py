# test_burner_generator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import BurnerGenerator, burner_generators, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BurnerGeneratorTesting(unittest.TestCase):
    def test_contstructor_init(self):
        generator = BurnerGenerator("burner-generator")

        with pytest.warns(DraftsmanWarning):
            BurnerGenerator(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
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
