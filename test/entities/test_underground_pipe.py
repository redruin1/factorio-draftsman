# test_underground_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import UndergroundPipe, underground_pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class UndergroundPipeTesting(unittest.TestCase):
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            UndergroundPipe("pipe-to-ground", unused_keyword=10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            UndergroundPipe("this is not an underground pipe")
