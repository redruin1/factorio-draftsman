# test_utils.py
# -*- encoding: utf-8 -*-

from collections import OrderedDict
from draftsman import utils
from draftsman.error import InvalidSignalError
from draftsman.data import recipes, signals

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest

import warnings


class UtilsTesting(unittest.TestCase):
    def test_string_to_JSON(self):
        # Blueprints
        resulting_dict = utils.string_to_JSON(
            "0eNqN0N0KwjAMBeB3yXU33E/d7KuISKdRCltW2mxsjL67ncIEvdDLHnK+lCzQtANaZ4hBLWAuPXlQxwW8uZNu14xni6BgNI6HmAgg3a3BayLZQRBg6IoTqCycBCCxYYMv5vmYzzR0Dbo4sLVv2nPCTpO3veOkwZYjbXsfuz2te6Mnd1UqBcygkqyuUxmC+CLzjfyt7X9qxabhZB16/8cf6w813sAwdtF431bAiM4/W3mdldUhr8qDLCtZhPAAeZl+cQ=="
        )
        self.assertEqual(
            resulting_dict,
            {
                "blueprint": {
                    "item": "blueprint",
                    "version": 281479274954753,
                    "icons": [
                        {"signal": {"type": "virtual", "name": "signal-0"}, "index": 1}
                    ],
                    "entities": [
                        {
                            "entity_number": 1,
                            "name": "fast-transport-belt",
                            "position": {"x": 507.5, "y": -188.5},
                        },
                        {
                            "entity_number": 2,
                            "name": "transport-belt",
                            "position": {"x": 506.5, "y": -188.5},
                        },
                        {
                            "entity_number": 3,
                            "name": "express-transport-belt",
                            "position": {"x": 508.5, "y": -188.5},
                        },
                    ],
                }
            },
        )

    def test_JSON_to_string(self):
        # Blueprints
        test_dict = OrderedDict(
            [
                ("arbitrary_data_1", 1),
                ("arbitrary_data_2", 2.0),
                ("arbitrary_data_3", ["stringy", "strigger", "others"]),
                ("finally", {"key": "value"}),
            ]
        )
        self.assertEqual(
            utils.JSON_to_string(test_dict),
            "0eNplyEEKgCAURdG9vLFE2sytRMiPzCQx+Fog0t6ThjW6h1tBPPvMxMUslMlIaCm+U0Grrv/tAXpEyuyjKxCvnLPceOTNcsIksPpIIRToit224KJwWtz3AzZ8Kjs=",
        )

    def test_encode_version(self):
        self.assertEqual(utils.encode_version(1, 1, 50, 1), 281479274954753)

    def test_decode_version(self):
        self.assertEqual(utils.decode_version(281479274954753), (1, 1, 50, 1))

    def test_version_string_to_tuple(self):
        self.assertEqual(utils.version_string_to_tuple("1.15.2.3"), (1, 15, 2, 3))

    def test_version_tuple_to_string(self):
        self.assertEqual(utils.version_tuple_to_string((1, 15, 2, 3)), "1.15.2.3")

    def test_get_signal_type(self):
        self.assertEqual(signals.get_signal_type("signal-anything"), "virtual")
        self.assertEqual(signals.get_signal_type("water"), "fluid")
        self.assertEqual(signals.get_signal_type("wooden-chest"), "item")
        with self.assertRaises(InvalidSignalError):
            signals.get_signal_type("incorrect")

    def test_signal_dict(self):
        self.assertEqual(
            signals.signal_dict("signal-anything"),
            {"name": "signal-anything", "type": "virtual"},
        )
        self.assertEqual(
            signals.signal_dict("water"), {"name": "water", "type": "fluid"}
        )
        self.assertEqual(
            signals.signal_dict("wooden-chest"),
            {"name": "wooden-chest", "type": "item"},
        )
        with self.assertRaises(InvalidSignalError):
            signals.signal_dict("incorrect")

    # def test_dist(self):
    #     self.assertAlmostEqual(
    #         utils.dist([0, 0], [100, 0]),
    #         100
    #     )
    #     self.assertAlmostEqual(
    #         utils.dist([0, 0], [4, 3]),
    #         5
    #     )

    def test_point_in_aabb(self):
        aabb = [[0, 0], [1, 1]]
        # Inside
        self.assertEqual(utils.point_in_aabb((0.5, 0.5), aabb), True)
        # On edge
        self.assertEqual(utils.point_in_aabb((1.0, 0.5), aabb), True)
        # Outside
        self.assertEqual(utils.point_in_aabb((2.0, 0.5), aabb), False)

    def test_aabb_overlaps_aabb(self):
        aabb1 = [[0, 0], [10, 10]]
        aabb2 = [[1, 1], [2, 2]]
        aabb3 = [[2, 1], [18, 8]]
        aabb4 = [[3, 3], [4, 4]]
        # 1 vs 2
        self.assertEqual(utils.aabb_overlaps_aabb(aabb1, aabb2), True)
        # Converse
        self.assertEqual(utils.aabb_overlaps_aabb(aabb2, aabb1), True)
        # 1 vs 3
        self.assertEqual(utils.aabb_overlaps_aabb(aabb1, aabb3), True)
        # Converse
        self.assertEqual(utils.aabb_overlaps_aabb(aabb3, aabb1), True)
        # 2 vs 3 (Edge)
        self.assertEqual(utils.aabb_overlaps_aabb(aabb2, aabb3), False)
        # Converse
        self.assertEqual(utils.aabb_overlaps_aabb(aabb3, aabb2), False)
        # 2 vs 4
        self.assertEqual(utils.aabb_overlaps_aabb(aabb2, aabb4), False)
        # Converse
        self.assertEqual(utils.aabb_overlaps_aabb(aabb4, aabb2), False)

    def test_point_in_circle(self):
        # Inside
        self.assertEqual(utils.point_in_circle((0, 0), 1), True)
        # Edge
        self.assertEqual(utils.point_in_circle((1, 0), 1), True)
        # Outside
        self.assertEqual(utils.point_in_circle((2, 0), 1), False)
        # Inside (Offset)
        self.assertEqual(utils.point_in_circle((1, 1), 1, (1, 1)), True)
        # Edge (Offset)
        self.assertEqual(utils.point_in_circle((1, 2), 1, (1, 1)), True)
        # Outside (Offset)
        self.assertEqual(utils.point_in_circle((0, 0), 1, (1, 1)), False)

    def test_aabb_overlaps_circle(self):
        # AABB inside circle
        self.assertEqual(
            utils.aabb_overlaps_circle([[-1, -1], [1, 1]], 2, (0, 0)), True
        )
        # Circle inside AABB
        self.assertEqual(
            utils.aabb_overlaps_circle([[-4, -4], [4, 4]], 1, (0, 0)), True
        )
        self.assertEqual(
            utils.aabb_overlaps_circle([[-5, -1], [-4, 1]], 1, (0, 0)), False
        )
        self.assertEqual(
            utils.aabb_overlaps_circle([[-1, 10], [1, 11]], 1, (0, 0)), False
        )
        self.assertEqual(
            utils.aabb_overlaps_circle([[-1.0, -0.5], [-0.5, 0.5]], 1, (0, 0)), True
        )
        # Edge
        self.assertEqual(
            utils.aabb_overlaps_circle([[-1.5, -1.5], [-0.5, -0.5]], 1, (0, 0)), True
        )

    def test_extend_aabb(self):
        base_aabb = [[0, 0], [0, 0]]
        base_aabb = utils.extend_aabb(base_aabb, [[0, 0], [1, 1]])
        self.assertEqual(base_aabb, [[0, 0], [1, 1]])
        # swap orders
        base_aabb = utils.extend_aabb([[9, 9], [10, 10]], base_aabb)
        self.assertEqual(base_aabb, [[0, 0], [10, 10]])

    def test_aabb_to_dimensions(self):
        self.assertEqual(utils.aabb_to_dimensions([[-5, -5], [10, 0]]), (15, 5))

    def test_get_recipe_ingredients(self):
        # Normal, list-type
        self.assertEqual(recipes.get_recipe_ingredients("wooden-chest"), {"wood"})
        # Normal, dict-type
        self.assertEqual(
            recipes.get_recipe_ingredients("plastic-bar"), {"petroleum-gas", "coal"}
        )
        # Expensive, list-type
        self.assertEqual(
            recipes.get_recipe_ingredients("iron-gear-wheel"), {"iron-plate"}
        )
        # Custom examples
        recipes.raw["test-1"] = {"ingredients": [["iron-plate", 2]]}
        self.assertEqual(recipes.get_recipe_ingredients("test-1"), {"iron-plate"})
        recipes.raw["test-2"] = {"normal": {"ingredients": [{"name": "iron-plate"}]}}
        self.assertEqual(recipes.get_recipe_ingredients("test-2"), {"iron-plate"})

    def test_reissue_warnings(self):
        @utils.reissue_warnings
        def test_function():
            warnings.warn("testing")
            return "examples"

        with self.assertWarns(UserWarning):
            result = test_function()

        self.assertEqual(result, "examples")
