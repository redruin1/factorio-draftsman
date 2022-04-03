# test_generator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Generator, generators
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class GeneratorTesting(TestCase):
    def test_constructor_init(self):
        generator = Generator()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Generator(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Generator("not a boiler")
