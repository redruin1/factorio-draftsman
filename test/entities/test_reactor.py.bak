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
        reactor = Reactor("nuclear-reactor")

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Reactor("nuclear-reactor", unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Reactor("not a reactor")

    def test_mergable_with(self):
        reactor1 = Reactor("nuclear-reactor")
        reactor2 = Reactor("nuclear-reactor", tags={"some": "stuff"})

        self.assertTrue(reactor1.mergable_with(reactor1))

        self.assertTrue(reactor1.mergable_with(reactor2))
        self.assertTrue(reactor2.mergable_with(reactor1))

        reactor2.tile_position = (1, 1)
        self.assertFalse(reactor1.mergable_with(reactor2))

    def test_merge(self):
        reactor1 = Reactor("nuclear-reactor")
        reactor2 = Reactor("nuclear-reactor", tags={"some": "stuff"})

        reactor1.merge(reactor2)
        del reactor2

        self.assertEqual(reactor1.tags, {"some": "stuff"})
