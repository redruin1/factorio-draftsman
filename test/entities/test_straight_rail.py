# test_straight_rail.py

from draftsman.constants import Direction
from draftsman.entity import StraightRail, straight_rails
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class StraightRailTesting(TestCase): # Hoo boy
    def test_default_constructor(self):
        straight_rail = StraightRail()
        self.assertEqual(
            straight_rail.to_dict(),
            {
                "name": "straight-rail",
                "position": {"x": 1.0, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        straight_rail = StraightRail(
            "straight-rail", 
            position = [0, 0],
            direction = Direction.NORTHWEST
        )
        self.assertEqual(
            straight_rail.to_dict(),
            {
                "name": "straight-rail",
                "position": {"x": 1.0, "y": 1.0},
                "direction": 7
            }
        )

        straight_rail = StraightRail(
            "straight-rail", 
            position = {"x": 101, "y": 101},
            direction = Direction.SOUTH
        )
        self.assertEqual(
            straight_rail.to_dict(),
            {
                "name": "straight-rail",
                "position": {"x": 101.0, "y": 101.0},
                "direction": 4
            }
        )

        # Warnings:
        with self.assertWarns(UserWarning):
            StraightRail("straight-rail", invalid_keyword = "whatever")
        # if entity is not on a grid pos / 2, then warn the user of the incoming
        # shift
        with self.assertWarns(UserWarning):
            StraightRail("straight-rail", position = [1, 1])

        # Errors
        with self.assertRaises(InvalidEntityID):
            StraightRail("this is not a straight rail")