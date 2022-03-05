# test_mining_drill.py

from draftsman.constants import MiningDrillReadMode
from draftsman.entity import MiningDrill, mining_drills
from draftsman.errors import InvalidEntityID, InvalidSignalID, InvalidModuleID

from schema import SchemaError

from unittest import TestCase

class MiningDrillTesting(TestCase):
    def test_default_constructor(self):
        mining_drill = MiningDrill()
        self.assertEqual(
            mining_drill.to_dict(),
            {
                "name": "burner-mining-drill",
                "position": {"x": 1.0, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        reactor = MiningDrill(
            "electric-mining-drill",
            items = {
                "productivity-module": 1,
                "productivity-module-2": 1
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            MiningDrill(unused_keyword = "whatever")
        with self.assertWarns(UserWarning):
            MiningDrill(
                "electric-mining-drill",
                items = {
                    "productivity-module": 5
                }
            )

        # Errors
        with self.assertRaises(InvalidEntityID):
            MiningDrill("not a mining drill")

    def test_set_item_request(self):
        mining_drill = MiningDrill("electric-mining-drill")
        mining_drill.set_item_request("speed-module-3", 3)
        self.assertEqual(
            mining_drill.to_dict(),
            {
                "name": "electric-mining-drill",
                "position": {"x": 1.5, "y": 1.5},
                "items": {
                    "speed-module-3": 3
                }
            }
        )
        with self.assertWarns(UserWarning):
            mining_drill.set_item_request("productivity-module-3", 3)
        self.assertEqual(
            mining_drill.to_dict(),
            {
                "name": "electric-mining-drill",
                "position": {"x": 1.5, "y": 1.5},
                "items": {
                    "speed-module-3": 3,
                    "productivity-module-3": 3
                }
            }
        )
        mining_drill.set_item_request("speed-module-3", None)
        self.assertEqual(
            mining_drill.items,
            {
                "productivity-module-3": 3
            }
        )
        mining_drill.set_item_requests(None)
        self.assertEqual(mining_drill.items, {})
        with self.assertRaises(InvalidSignalID):
            mining_drill.set_item_request("incorrect", 2)
        # with self.assertRaises(InvalidModuleID):
        #     mining_drill.set_item_request("iron-ore", 2)

    def test_set_read_resources(self):
        mining_drill = MiningDrill()
        mining_drill.set_read_resources(True)
        self.assertEqual(
            mining_drill.control_behavior,
            {
                "circuit_read_resources": True
            }
        )
        mining_drill.set_read_resources(None)
        self.assertEqual(mining_drill.control_behavior, {})
        with self.assertRaises(SchemaError):
            mining_drill.set_read_resources("incorrect")

    def test_set_read_mode(self):
        mining_drill = MiningDrill()
        mining_drill.set_read_mode(MiningDrillReadMode.UNDER_DRILL)
        self.assertEqual(
            mining_drill.control_behavior,
            {
                "circuit_resource_read_mode": MiningDrillReadMode.UNDER_DRILL
            }
        )
        mining_drill.set_read_mode(None)
        self.assertEqual(mining_drill.control_behavior, {})
        # with self.assertRaises(SchemaError):
        #     mining_drill.set_read_mode("incorrect")