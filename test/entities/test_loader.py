# test_loader.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Loader, loaders
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class LoaderTesting(TestCase):
    def test_constructor_init(self):
        # loader = Loader()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Loader("loader", unused_keyword=10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            Loader("this is not a loader")
