# test_mining_drill.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import MiningDrillReadMode
from draftsman.entity import MiningDrill, mining_drills
from draftsman.error import InvalidEntityError, InvalidItemError, DataFormatError
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


class MiningDrillTesting(unittest.TestCase):
    def test_constructor_init(self):
        drill = MiningDrill(
            "electric-mining-drill",
            items={"productivity-module": 1, "productivity-module-2": 1},
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            MiningDrill(unused_keyword="whatever")
        with self.assertWarns(ModuleCapacityWarning):
            MiningDrill("electric-mining-drill", items={"productivity-module": 5})

        # Errors
        with self.assertRaises(InvalidEntityError):
            MiningDrill("not a mining drill")
        with self.assertRaises(DataFormatError):
            MiningDrill(control_behavior={"unused_key": "something"})

    def test_set_item_request(self):
        mining_drill = MiningDrill("electric-mining-drill")
        mining_drill.set_item_request("speed-module-3", 3)
        self.assertEqual(
            mining_drill.to_dict(),
            {
                "name": "electric-mining-drill",
                "position": {"x": 1.5, "y": 1.5},
                "items": {"speed-module-3": 3},
            },
        )
        with self.assertWarns(ModuleCapacityWarning):
            mining_drill.set_item_request("productivity-module-3", 3)
        self.assertEqual(
            mining_drill.to_dict(),
            {
                "name": "electric-mining-drill",
                "position": {"x": 1.5, "y": 1.5},
                "items": {"speed-module-3": 3, "productivity-module-3": 3},
            },
        )
        mining_drill.set_item_request("speed-module-3", None)
        self.assertEqual(mining_drill.items, {"productivity-module-3": 3})
        mining_drill.set_item_requests(None)
        self.assertEqual(mining_drill.items, {})
        with self.assertWarns(ItemLimitationWarning):
            mining_drill.set_item_request("iron-ore", 2)

        # Errors
        with self.assertRaises(InvalidItemError):
            mining_drill.set_item_request("incorrect", 2)

    def test_set_read_resources(self):
        mining_drill = MiningDrill()
        mining_drill.read_resources = True
        self.assertEqual(mining_drill.read_resources, True)
        self.assertEqual(
            mining_drill.control_behavior, {"circuit_read_resources": True}
        )
        mining_drill.read_resources = None
        self.assertEqual(mining_drill.control_behavior, {})
        with self.assertRaises(TypeError):
            mining_drill.read_resources = "incorrect"

    def test_set_read_mode(self):
        mining_drill = MiningDrill()
        mining_drill.read_mode = MiningDrillReadMode.UNDER_DRILL
        self.assertEqual(mining_drill.read_mode, MiningDrillReadMode.UNDER_DRILL)
        self.assertEqual(
            mining_drill.control_behavior,
            {"circuit_resource_read_mode": MiningDrillReadMode.UNDER_DRILL},
        )
        mining_drill.read_mode = None
        self.assertEqual(mining_drill.control_behavior, {})

        with self.assertRaises(ValueError):
            mining_drill.read_mode = "incorrect"

    def test_mergable_with(self):
        drill1 = MiningDrill("electric-mining-drill")
        drill2 = MiningDrill(
            "electric-mining-drill",
            items={"productivity-module": 1, "productivity-module-2": 1},
            tags={"some": "stuff"},
        )

        self.assertTrue(drill1.mergable_with(drill1))

        self.assertTrue(drill1.mergable_with(drill2))
        self.assertTrue(drill2.mergable_with(drill1))

        drill2.tile_position = (1, 1)
        self.assertFalse(drill1.mergable_with(drill2))

    def test_merge(self):
        drill1 = MiningDrill("electric-mining-drill")
        drill2 = MiningDrill(
            "electric-mining-drill",
            items={"productivity-module": 1, "productivity-module-2": 1},
            tags={"some": "stuff"},
        )

        drill1.merge(drill2)
        del drill2

        self.assertEqual(
            drill1.items, {"productivity-module": 1, "productivity-module-2": 1}
        )
        self.assertEqual(drill1.tags, {"some": "stuff"})
