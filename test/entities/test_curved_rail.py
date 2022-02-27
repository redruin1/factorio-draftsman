# test_curved_rail.py

from draftsman.entity import CurvedRail, curved_rails, Direction
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class CurvedRailTesting(TestCase):
    def test_default_constructor(self):
        straight_rail = CurvedRail()
        self.assertEqual(
            straight_rail.to_dict(),
            {
                "name": "curved-rail",
                "position": {"x": 2.0, "y": 4.0}
            }
        )

    def test_constructor_init(self):
        curved_rail = CurvedRail(
            "curved-rail", 
            position = [0, 0],
            direction = Direction.NORTHWEST
        )
        self.assertEqual(
            curved_rail.to_dict(),
            {
                "name": "curved-rail",
                "position": {"x": 4.0, "y": 2.0},
                "direction": 7
            }
        )

        # Warnings:
        with self.assertWarns(UserWarning):
            CurvedRail("curved-rail", invalid_keyword = "whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with self.assertWarns(UserWarning):
            CurvedRail("curved-rail", position = [1, 1])

        # Errors
        with self.assertRaises(InvalidEntityID):
            CurvedRail("this is not a curved rail")

    def test_dimensions(self):
        curved_rail = CurvedRail()
        self.assertEqual(curved_rail.width, 4)
        self.assertEqual(curved_rail.height, 8)