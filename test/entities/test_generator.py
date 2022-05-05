# test_generator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Generator, generators
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class GeneratorTesting(unittest.TestCase):
    def test_constructor_init(self):
        generator = Generator()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Generator(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Generator("not a boiler")
