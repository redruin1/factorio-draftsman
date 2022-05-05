# test_reactor.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Reactor, reactors
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class ReactorTesting(unittest.TestCase):
    def test_constructor_init(self):
        reactor = Reactor()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Reactor(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Reactor("not a reactor")
