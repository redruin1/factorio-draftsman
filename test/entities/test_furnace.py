# test_furnace.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Furnace, furnaces
from draftsman.error import InvalidEntityError, InvalidItemError
from draftsman.warning import DraftsmanWarning, ItemLimitationWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class FurnaceTesting(TestCase):
    def test_constructor_init(self):
        furance = Furnace()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Furnace(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Furnace("not a heat pipe")

    def test_set_item_request(self):
        furnace = Furnace("electric-furnace")
        # Valid
        furnace.set_item_request("productivity-module-3", 2)
        self.assertEqual(furnace.items, {"productivity-module-3": 2})

        # Warnings
        furnace.set_item_requests(None)
        with self.assertWarns(ItemLimitationWarning):
            furnace.set_item_request("wood", 100)

        # Errors
        with self.assertRaises(InvalidItemError):
            furnace.set_item_request("incorrect", "nonsense")
        with self.assertRaises(TypeError):
            furnace.set_item_request("speed-module-2", "nonsense")
