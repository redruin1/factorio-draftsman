# test_burner_generator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import BurnerGenerator, burner_generators
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BurnerGeneratorTesting(unittest.TestCase):
    def test_contstructor_init(self):
        generator = BurnerGenerator("burner-generator")

        with self.assertWarns(DraftsmanWarning):
            BurnerGenerator(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            BurnerGenerator("this is not a burner generator")

    def test_mergable_with(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator", tags={"some": "stuff"})

        self.assertTrue(generator1.mergable_with(generator2))
        self.assertTrue(generator2.mergable_with(generator1))

        generator2.tile_position = [-10, -10]
        self.assertFalse(generator1.mergable_with(generator2))

    def test_merge(self):
        generator1 = BurnerGenerator("burner-generator")
        generator2 = BurnerGenerator("burner-generator", tags={"some": "stuff"})

        generator1.merge(generator2)
        del generator2

        self.assertEqual(generator1.tags, {"some": "stuff"})
