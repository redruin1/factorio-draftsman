# test_utils.py

from collections import OrderedDict
from draftsman import utils
from draftsman.classes.vector import Vector
from draftsman.constants import Direction, Orientation, Ticks, ValidationMode
from draftsman.error import InvalidSignalError
from draftsman.data import recipes, signals

import pytest
import warnings


class TestAABB:
    def test_constructor(self):
        aabb = utils.AABB(0, 0, 1, 1)
        # self.assertEqual(aabb.top_left, Vector(0, 0))
        assert aabb.top_left == Vector(0, 0)
        # self.assertEqual(aabb.bot_right, Vector(1, 1))
        assert aabb.bot_right == Vector(1, 1)
        # self.assertEqual(aabb.position, Vector(0, 0))
        assert aabb.position == Vector(0, 0)

        aabb = utils.AABB(0, 0, 2, 2, (1, 1))
        # self.assertEqual(aabb.top_left, Vector(0, 0))
        assert aabb.top_left == Vector(0, 0)
        # self.assertEqual(aabb.bot_right, Vector(2, 2))
        assert aabb.bot_right == Vector(2, 2)
        # self.assertEqual(aabb.position, Vector(1, 1))
        assert aabb.position == Vector(1, 1)

    def test_from_other(self):
        aabb = utils.AABB.from_other([0, 1, 2, 3])
        # self.assertEqual(aabb.top_left, Vector(0, 1))
        assert aabb.top_left == Vector(0, 1)
        # self.assertEqual(aabb.bot_right, Vector(2, 3))
        assert aabb.bot_right == Vector(2, 3)
        # self.assertEqual(aabb.position, Vector(0, 0))
        assert aabb.position == Vector(0, 0)

        aabb = utils.AABB.from_other((0, 1, 2, 3))
        # self.assertEqual(aabb.top_left, Vector(0, 1))
        assert aabb.top_left == Vector(0, 1)
        # self.assertEqual(aabb.bot_right, Vector(2, 3))
        assert aabb.bot_right == Vector(2, 3)
        # self.assertEqual(aabb.position, Vector(0, 0))
        assert aabb.position == Vector(0, 0)

        with pytest.raises(TypeError):
            utils.AABB.from_other(123.4)

        with pytest.raises(TypeError):
            utils.AABB.from_other([1, 1])

    def test_overlaps(self):
        aabb1 = utils.AABB(0, 0, 1, 1)
        aabb2 = utils.AABB(0.5, 0.5, 1.5, 1.5)
        aabb3 = utils.AABB(1, 0, 2, 1)
        aabb4 = utils.AABB(0, 0, 1, 1, (5, 5))

        # Normal case
        assert aabb1.overlaps(aabb2)
        # Test reciprocal
        assert aabb2.overlaps(aabb1)
        # Edge overlap does not count
        assert not aabb1.overlaps(aabb3)
        # Account for position
        assert not aabb1.overlaps(aabb4)

        # Rectangle cases
        rect1 = utils.Rectangle((1, 1), 1, 1, 0)
        rect2 = utils.Rectangle((1, 1), 1, 1, 45)
        rect3 = utils.Rectangle((1.4, 1.4), 1, 1, 45)

        assert aabb1.overlaps(rect1)
        assert aabb1.overlaps(rect2)

        assert not aabb1.overlaps(rect3)
        assert not rect3.overlaps(aabb1)  # reciprocal

        # Error case
        with pytest.raises(TypeError):
            aabb1.overlaps(Vector(0.5, 0.5))

    def test_get_bounding_box(self):
        aabb = utils.AABB(0, 1, 2, 3)
        bounding_box = aabb.get_bounding_box()
        assert bounding_box == utils.AABB(0, 1, 2, 3)
        assert aabb is not bounding_box

    def test_rotate(self):
        aabb = utils.AABB(0, 0, 1, 1)
        rotated_aabb = aabb.rotate(4)
        assert round(abs(rotated_aabb.top_left[0] - -1), 7) == 0
        assert round(abs(rotated_aabb.top_left[1] - 0), 7) == 0
        assert round(abs(rotated_aabb.bot_right[0] - 0), 7) == 0
        assert round(abs(rotated_aabb.bot_right[1] - 1), 7) == 0

        with pytest.raises(ValueError):
            aabb.rotate(1)

    def test_add(self):
        aabb = utils.AABB(0, 0, 1, 1)
        new_aabb = aabb + (10, 10)
        assert new_aabb.position == Vector(10, 10)
        assert new_aabb.get_bounding_box() == utils.AABB(
            10,
            10,
            11,
            11,
        )

    def test_eq(self):
        assert utils.AABB(0, 0, 1, 1) == utils.AABB(0, 0, 1, 1)
        assert utils.AABB(0, 0, 1, 1) != utils.AABB(1, 1, 2, 2)


class TestRectangle:
    def test_constructor(self):
        # TODO
        pass

    def test_overlaps(self):
        # TODO
        pass

    def test_get_bounding_box(self):
        rect = utils.Rectangle((4, 4), 1, 1, 45)
        bounding_box = rect.get_bounding_box()
        assert round(abs(bounding_box.top_left[0] - 3.292), 2) == 0
        assert round(abs(bounding_box.top_left[1] - 3.292), 2) == 0
        assert round(abs(bounding_box.bot_right[0] - 4.707), 2) == 0
        assert round(abs(bounding_box.bot_right[1] - 4.707), 2) == 0
        assert bounding_box.position == Vector(0, 0)

    def test_rotate(self):
        pass

    def test_eq(self):
        pass


class TestConstants:
    def test_orientation_to_direction(self):
        assert Orientation.NORTH.to_direction() == Direction.NORTH
        assert Orientation.NORTHEAST.to_direction() == Direction.NORTH
        assert (
            Orientation.NORTHEAST.to_direction(sixteen_way=True) == Direction.NORTHEAST
        )

    def test_orientation_add(self):
        assert Orientation(0.75) + Orientation(0.5) == Orientation(0.25)
        assert Orientation(0.75) + 0.5 == Orientation(0.25)
        assert 0.75 + Orientation(0.5) == Orientation(0.25)
        with pytest.raises(TypeError):
            Orientation.NORTH + "string"
        with pytest.raises(TypeError):
            "string" + Orientation.NORTH

    def test_orientation_sub(self):
        assert Orientation(0.25) - Orientation(0.5) == Orientation(0.75)
        assert Orientation(0.25) - 0.5 == Orientation(0.75)
        assert 0.25 - Orientation(0.5) == Orientation(0.75)
        with pytest.raises(TypeError):
            Orientation.NORTH - "string"
        with pytest.raises(TypeError):
            "string" - Orientation.NORTH

    def test_eq(self):
        assert not Orientation.NORTH == "wrong"

    def test_lt(self):
        assert Orientation.NORTH < Orientation.SOUTH
        with pytest.raises(TypeError):
            Orientation.NORTH < "wrong"

    def test_ticks_from_timedelta(self):
        from datetime import timedelta

        td = timedelta(1, 123, 2 * 8)
        assert Ticks.from_timedelta(td) == 5191380

    def test_validation_mode_eq(self):
        assert ValidationMode.MINIMUM != TypeError

    def test_validation_mode_gt(self):
        with pytest.raises(TypeError):
            ValidationMode.NONE > TypeError


class TestUtils:
    def test_string_to_JSON(self):
        # Blueprints
        resulting_dict = utils.string_to_JSON(
            "0eNqN0N0KwjAMBeB3yXU33E/d7KuISKdRCltW2mxsjL67ncIEvdDLHnK+lCzQtANaZ4hBLWAuPXlQxwW8uZNu14xni6BgNI6HmAgg3a3BayLZQRBg6IoTqCycBCCxYYMv5vmYzzR0Dbo4sLVv2nPCTpO3veOkwZYjbXsfuz2te6Mnd1UqBcygkqyuUxmC+CLzjfyt7X9qxabhZB16/8cf6w813sAwdtF431bAiM4/W3mdldUhr8qDLCtZhPAAeZl+cQ=="
        )
        assert resulting_dict == {
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
        }

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
        assert (
            utils.JSON_to_string(test_dict)
            == "0eNplyEEKgCAURdG9vLFE2sytRMiPzCQx+Fog0t6ThjW6h1tBPPvMxMUslMlIaCm+U0Grrv/tAXpEyuyjKxCvnLPceOTNcsIksPpIIRToit224KJwWtz3AzZ8Kjs="
        )

    def test_encode_version(self):
        assert utils.encode_version(1, 1, 50, 1) == 281479274954753

    def test_decode_version(self):
        assert utils.decode_version(281479274954753) == (1, 1, 50, 1)

    def test_version_string_to_tuple(self):
        assert utils.version_string_to_tuple("1.15.2.3") == (1, 15, 2, 3)

    def test_version_tuple_to_string(self):
        assert utils.version_tuple_to_string((1, 15, 2, 3)) == "1.15.2.3"

    def test_get_signal_types(self):
        assert signals.get_signal_types("signal-anything") == ["virtual"]
        assert signals.get_signal_types("water") == ["fluid"]
        assert signals.get_signal_types("wooden-chest") == ["item", "recipe", "entity"]
        with pytest.raises(InvalidSignalError):
            signals.get_signal_types("incorrect")

    # def test_signal_dict(self):
    #     assert signals.signal_dict("signal-anything") == {
    #         "name": "signal-anything",
    #         "type": "virtual",
    #     }
    #     assert signals.signal_dict("water") == {"name": "water", "type": "fluid"}
    #     assert signals.signal_dict("wooden-chest") == {
    #         "name": "wooden-chest",
    #         "type": "item",
    #     }
    #     with pytest.raises(InvalidSignalError):
    #         signals.signal_dict("incorrect")

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
        aabb = utils.AABB(0, 0, 1, 1)
        # Inside
        assert utils.point_in_aabb([0.5, 0.5], aabb) == True
        # On edge
        assert utils.point_in_aabb([1.0, 0.5], aabb) == True
        # Outside
        assert utils.point_in_aabb([2.0, 0.5], aabb) == False

    def test_aabb_overlaps_aabb(self):
        aabb1 = utils.AABB(0, 0, 10, 10)
        aabb2 = utils.AABB(1, 1, 2, 2)
        aabb3 = utils.AABB(2, 1, 18, 8)
        aabb4 = utils.AABB(3, 3, 4, 4)
        # 1 vs 2
        assert utils.aabb_overlaps_aabb(aabb1, aabb2) == True
        # Converse
        assert utils.aabb_overlaps_aabb(aabb2, aabb1) == True
        # 1 vs 3
        assert utils.aabb_overlaps_aabb(aabb1, aabb3) == True
        # Converse
        assert utils.aabb_overlaps_aabb(aabb3, aabb1) == True
        # 2 vs 3 (Edge)
        assert utils.aabb_overlaps_aabb(aabb2, aabb3) == False
        # Converse
        assert utils.aabb_overlaps_aabb(aabb3, aabb2) == False
        # 2 vs 4
        assert utils.aabb_overlaps_aabb(aabb2, aabb4) == False
        # Converse
        assert utils.aabb_overlaps_aabb(aabb4, aabb2) == False

    def test_point_in_circle(self):
        # Inside
        assert utils.point_in_circle([0, 0], 1) == True
        # Edge
        assert utils.point_in_circle([1, 0], 1) == True
        # Outside
        assert utils.point_in_circle([2, 0], 1) == False
        # Inside (Offset)
        assert utils.point_in_circle([1, 1], 1, (1, 1)) == True
        # Edge (Offset)
        assert utils.point_in_circle([1, 2], 1, (1, 1)) == True
        # Outside (Offset)
        assert utils.point_in_circle([0, 0], 1, (1, 1)) == False

    def test_aabb_overlaps_circle(self):
        # AABB inside circle
        assert utils.aabb_overlaps_circle(utils.AABB(-1, -1, 1, 1), 2, (0, 0)) == True
        # Circle inside AABB
        assert utils.aabb_overlaps_circle(utils.AABB(-4, -4, 4, 4), 1, (0, 0)) == True
        assert utils.aabb_overlaps_circle(utils.AABB(-5, -1, -4, 1), 1, (0, 0)) == False
        assert utils.aabb_overlaps_circle(utils.AABB(-1, 10, 1, 11), 1, (0, 0)) == False
        assert (
            utils.aabb_overlaps_circle(utils.AABB(-1.0, -0.5, -0.5, 0.5), 1, (0, 0))
            == True
        )
        # Edge
        assert (
            utils.aabb_overlaps_circle(utils.AABB(-1.5, -1.5, -0.5, -0.5), 1, (0, 0))
            == True
        )

    def test_rect_overlaps_rect(self):
        pass

    def test_extend_aabb(self):
        base_aabb = utils.AABB(0, 0, 0, 0)
        base_aabb = utils.extend_aabb(base_aabb, utils.AABB(0, 0, 1, 1))
        assert base_aabb == utils.AABB(0, 0, 1, 1)

        # Swap orders
        base_aabb = utils.extend_aabb(utils.AABB(9, 9, 10, 10), base_aabb)
        assert base_aabb == utils.AABB(0, 0, 10, 10)

        # First None case
        result_aabb = utils.extend_aabb(None, utils.AABB(0, 0, 1, 1))
        assert result_aabb == utils.AABB(0, 0, 1, 1)

        # Second None case
        result_aabb = utils.extend_aabb(utils.AABB(0, 0, 1, 1), None)
        assert result_aabb == utils.AABB(0, 0, 1, 1)

        # Both None case
        result_aabb = utils.extend_aabb(None, None)
        assert result_aabb == None

    def test_aabb_to_dimensions(self):
        assert utils.aabb_to_dimensions(utils.AABB(-5, -5, 10, 0)) == (15, 5)

    def test_get_first(self):
        test_list = ["a", "b", "c"]
        assert utils.get_first(test_list) == "a"
        test_list = []
        assert utils.get_first(test_list) == None

    def test_parse_energy(self):
        # Normal
        assert utils.parse_energy("100J") == 100
        assert utils.parse_energy("1000KJ") == 1_000_000
        assert utils.parse_energy("60MW") == 1_000_000

        # Unknown unit type specifier
        with pytest.raises(ValueError):
            utils.parse_energy("100MY")

        # Unknown unit scale specifier
        with pytest.raises(ValueError):
            utils.parse_energy("100QW")

    def test_reissue_warnings(self):
        @utils.reissue_warnings
        def test_function():
            warnings.warn("testing")
            return "examples"

        with pytest.warns(UserWarning):
            result = test_function()

        assert result == "examples"
