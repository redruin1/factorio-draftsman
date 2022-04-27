# test_pipe.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Pipe, pipes
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class PipeTesting(TestCase):
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Pipe("pipe", unused_keyword=10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Pipe("Ceci n'est pas une pipe.")
