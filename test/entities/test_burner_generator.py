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
        generator = BurnerGenerator()

        with self.assertWarns(DraftsmanWarning):
            BurnerGenerator(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            BurnerGenerator("this is not a burner generator")
