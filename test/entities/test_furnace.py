# test_furnace.py

from draftsman.entity import Furnace, furnaces
from draftsman.error import InvalidEntityError, InvalidItemError
from draftsman.warning import DraftsmanWarning, ItemLimitationWarning

from schema import SchemaError
from unittest import TestCase

class FurnaceTesting(TestCase):
    def test_constructor_init(self):
        furance = Furnace()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Furnace(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            Furnace("not a heat pipe")

    def test_set_item_request(self):
        furnace = Furnace("electric-furnace")
        # Valid
        furnace.set_item_request("productivity-module-3", 2)
        self.assertEqual(
            furnace.items,
            {
                "productivity-module-3": 2
            }
        )

        # Warnings
        furnace.set_item_requests(None)
        with self.assertWarns(ItemLimitationWarning):
            furnace.set_item_request("wood", 100)

        # Errors
        with self.assertRaises(InvalidItemError):
            furnace.set_item_request("incorrect", "nonsense")
        with self.assertRaises(SchemaError):
            furnace.set_item_request("speed-module-2", "nonsense")