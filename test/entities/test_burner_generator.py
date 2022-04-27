# test_burner_generator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import BurnerGenerator, burner_generators
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class BurnerGeneratorTesting(TestCase):
    def test_contstructor_init(self):
        generator = BurnerGenerator()

        with self.assertWarns(DraftsmanWarning):
            BurnerGenerator(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            BurnerGenerator("this is not a burner generator")
