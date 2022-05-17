# test_lab.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Lab, labs
from draftsman.error import InvalidEntityError, InvalidItemError
from draftsman.warning import (
    DraftsmanWarning,
    ModuleCapacityWarning,
    ItemLimitationWarning,
)

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LabTesting(unittest.TestCase):
    def test_contstructor_init(self):
        lab = Lab()

        with self.assertWarns(DraftsmanWarning):
            Lab(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Lab("this is not a lab")

    def test_inputs(self):
        lab = Lab("lab")

        self.assertEqual(
            lab.inputs,
            [
                "automation-science-pack",
                "logistic-science-pack",
                "military-science-pack",
                "chemical-science-pack",
                "production-science-pack",
                "utility-science-pack",
                "space-science-pack",
            ],
        )

    def test_set_item_request(self):
        lab = Lab("lab")

        lab.set_item_request("productivity-module-3", 2)
        self.assertEqual(lab.items, {"productivity-module-3": 2})
        self.assertEqual(lab.module_slots_occupied, 2)

        # Warnings
        with self.assertWarns(ModuleCapacityWarning):
            lab.set_item_request("speed-module-2", 2)
        self.assertEqual(lab.items, {"productivity-module-3": 2, "speed-module-2": 2})
        self.assertEqual(lab.module_slots_occupied, 4)

        lab.set_item_request("speed-module-2", None)
        self.assertEqual(lab.items, {"productivity-module-3": 2})

        lab.set_item_request("automation-science-pack", 10)
        self.assertEqual(
            lab.items, {"productivity-module-3": 2, "automation-science-pack": 10}
        )
        self.assertEqual(lab.module_slots_occupied, 2)

        with self.assertWarns(ItemLimitationWarning):
            lab.set_item_request("iron-plate", 100)
        self.assertEqual(
            lab.items,
            {
                "productivity-module-3": 2,
                "automation-science-pack": 10,
                "iron-plate": 100,
            },
        )

        # Errors
        lab.set_item_requests(None)
        self.assertEqual(lab.module_slots_occupied, 0)

        with self.assertRaises(TypeError):
            lab.set_item_request(TypeError, 100)
        with self.assertRaises(InvalidItemError):
            lab.set_item_request("incorrect", 100)
        with self.assertRaises(TypeError):
            lab.set_item_request("logistic-science-pack", TypeError)
        with self.assertRaises(ValueError):
            lab.set_item_request("logistic-science-pack", -1)

        self.assertEqual(lab.items, {})
        self.assertEqual(lab.module_slots_occupied, 0)
