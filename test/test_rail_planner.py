# test_rail_planner.py

from draftsman.constants import Direction
from draftsman.classes.rail_planner import RailPlanner
from draftsman.classes.group import Group
from draftsman.entity import (
    StraightRail,
    CurvedRail,
    RailSignal,
    RailChainSignal,
    TrainStop,
)
from draftsman.error import DraftsmanError
from draftsman.utils import Vector

import pytest


class TestRailPlanner:
    def test_constructor(self):
        rail_planner = RailPlanner()

        # Make sure parent Group properties still work
        rail_planner = RailPlanner(
            id="something", head_position=[10, 10], head_direction=Direction.SOUTH
        )
        assert rail_planner.id == "something"
        assert rail_planner.head_position == Vector(10, 10)
        assert rail_planner.head_direction == Direction.SOUTH

        # Handle incorrect name
        with pytest.raises(DraftsmanError):
            RailPlanner(name="wrong")

    def test_move_forward(self):
        rail_planner = RailPlanner()

        # Straight
        rail_planner.move_forward(2)
        assert rail_planner.head_position == Vector(0, -4)
        assert rail_planner.head_direction == Direction.NORTH
        assert len(rail_planner.entities) == 2
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTH
            ),
            StraightRail(
                "straight-rail", tile_position=(0, -2), direction=Direction.NORTH
            ),
        ]

        # Diagonal (start on left)
        rail_planner.head_position = (0, 0)
        rail_planner.head_direction = Direction.NORTHEAST
        rail_planner.move_forward(2)
        assert rail_planner.head_position == Vector(2, -2)
        assert rail_planner.head_direction == Direction.NORTHEAST
        assert len(rail_planner.entities) == 4
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTH
            ),
            StraightRail(
                "straight-rail", tile_position=(0, -2), direction=Direction.NORTH
            ),
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTHWEST
            ),
            StraightRail(
                "straight-rail", tile_position=(0, -2), direction=Direction.SOUTHEAST
            ),
        ]

        # Diagonal (start on right)
        rail_planner.head_position = (0, 0)
        rail_planner.diagonal_side = 1
        rail_planner.move_forward(2)
        assert rail_planner.head_position == Vector(2, -2)
        assert rail_planner.head_direction == Direction.NORTHEAST
        assert len(rail_planner.entities) == 6
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTH
            ),
            StraightRail(
                "straight-rail", tile_position=(0, -2), direction=Direction.NORTH
            ),
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTHWEST
            ),
            StraightRail(
                "straight-rail", tile_position=(0, -2), direction=Direction.SOUTHEAST
            ),
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.SOUTHEAST
            ),
            StraightRail(
                "straight-rail", tile_position=(2, 0), direction=Direction.NORTHWEST
            ),
        ]

    def test_turn_left(self):
        rail_planner = RailPlanner()

        # Single turn
        rail_planner.turn_left()
        assert rail_planner.head_position == Vector(-4, -6)
        assert rail_planner.head_direction == Direction.NORTHWEST
        assert len(rail_planner.entities) == 1
        assert rail_planner.entities._root == [
            CurvedRail("curved-rail", position=(0, -2), direction=Direction.NORTH)
        ]

        # Straight rail inbetween
        rail_planner.turn_left()
        assert rail_planner.head_position == Vector(-12, -10)
        assert rail_planner.head_direction == Direction.WEST
        assert len(rail_planner.entities) == 3
        assert rail_planner.entities._root == [
            CurvedRail("curved-rail", position=(0, -2), direction=Direction.NORTH),
            StraightRail(
                "straight-rail", tile_position=(-4, -6), direction=Direction.NORTHEAST
            ),
            CurvedRail("curved-rail", position=(-6, -8), direction=Direction.SOUTHEAST),
        ]

        # No straight on S bend
        rail_planner.turn_left()
        rail_planner.turn_right()
        assert rail_planner.head_position == Vector(-26, -4)
        assert rail_planner.head_direction == Direction.WEST
        assert len(rail_planner.entities) == 5
        assert rail_planner.entities._root == [
            CurvedRail("curved-rail", position=(0, -2), direction=Direction.NORTH),
            StraightRail(
                "straight-rail", tile_position=(-4, -6), direction=Direction.NORTHEAST
            ),
            CurvedRail("curved-rail", position=(-6, -8), direction=Direction.SOUTHEAST),
            CurvedRail("curved-rail", position=(-14, -8), direction=Direction.WEST),
            CurvedRail("curved-rail", position=(-20, -4), direction=Direction.EAST),
        ]

    def test_turn_right(self):
        rail_planner = RailPlanner()

        # Single turn
        rail_planner.turn_right()
        assert rail_planner.head_position == Vector(4, -6)
        assert rail_planner.head_direction == Direction.NORTHEAST
        assert len(rail_planner.entities) == 1
        assert rail_planner.entities._root == [
            CurvedRail("curved-rail", position=(2, -2), direction=Direction.NORTHEAST)
        ]

        # Straight rail inbetween
        rail_planner.turn_right()
        assert rail_planner.head_position == Vector(12, -10)
        assert rail_planner.head_direction == Direction.EAST
        assert len(rail_planner.entities) == 3
        assert rail_planner.entities._root == [
            CurvedRail("curved-rail", position=(2, -2), direction=Direction.NORTHEAST),
            StraightRail(
                "straight-rail", tile_position=(4, -6), direction=Direction.NORTHWEST
            ),
            CurvedRail("curved-rail", position=(8, -8), direction=Direction.WEST),
        ]

        # No straight on S bend
        rail_planner.turn_right()
        rail_planner.turn_left()
        assert rail_planner.head_position == Vector(26, -4)
        assert rail_planner.head_direction == Direction.EAST
        assert len(rail_planner.entities) == 5
        assert rail_planner.entities._root == [
            CurvedRail("curved-rail", position=(2, -2), direction=Direction.NORTHEAST),
            StraightRail(
                "straight-rail", tile_position=(4, -6), direction=Direction.NORTHWEST
            ),
            CurvedRail("curved-rail", position=(8, -8), direction=Direction.WEST),
            CurvedRail("curved-rail", position=(16, -8), direction=Direction.SOUTHEAST),
            CurvedRail("curved-rail", position=(22, -4), direction=Direction.NORTHWEST),
        ]

    def test_add_signal(self):
        rail_planner = RailPlanner()

        # adding rail to nothing should do nothing
        rail_planner.add_signal("rail-signal")
        assert len(rail_planner.entities) == 0

        # right front
        rail_planner.move_forward()
        rail_planner.add_signal("rail-signal")
        assert len(rail_planner.entities) == 2
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTH
            ),
            RailSignal("rail-signal", tile_position=(2, 0), direction=Direction.SOUTH),
        ]

        # right back
        rail_planner.entities = []
        rail_planner.head_position = (0, 0)
        rail_planner.move_forward()
        rail_planner.add_signal("rail-signal", front=False)
        assert len(rail_planner.entities) == 2
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTH
            ),
            RailSignal("rail-signal", tile_position=(2, 1), direction=Direction.SOUTH),
        ]

        # left front
        rail_planner.entities = []
        rail_planner.head_position = (0, 0)
        rail_planner.move_forward()
        rail_planner.add_signal("rail-signal", right=False)
        assert len(rail_planner.entities) == 2
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTH
            ),
            RailSignal("rail-signal", tile_position=(-1, 0), direction=Direction.NORTH),
        ]

        # diagonal right
        rail_planner.entities = []
        rail_planner.head_position = (0, 0)
        rail_planner.head_direction = Direction.NORTHEAST
        rail_planner.move_forward()
        rail_planner.add_signal("rail-signal")
        assert len(rail_planner.entities) == 2
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTHWEST
            ),
            RailSignal(
                "rail-signal", tile_position=(1, 1), direction=Direction.SOUTHWEST
            ),
        ]

        # diagonal left
        rail_planner.entities = []
        rail_planner.head_position = (0, 0)
        rail_planner.head_direction = Direction.NORTHEAST
        rail_planner.move_forward()
        rail_planner.add_signal("rail-signal", right=False)
        assert len(rail_planner.entities) == 2
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTHWEST
            ),
            RailSignal(
                "rail-signal", tile_position=(-1, -1), direction=Direction.NORTHEAST
            ),
        ]

        # Curved
        rail_planner.entities = []
        rail_planner.head_position = (0, 0)
        rail_planner.head_direction = Direction.NORTH
        rail_planner.turn_right()
        rail_planner.add_signal("rail-signal")
        assert len(rail_planner.entities) == 2
        assert rail_planner.entities._root == [
            CurvedRail("curved-rail", position=(2, -2), direction=Direction.NORTHEAST),
            RailSignal(
                "rail-signal", tile_position=(4, -4), direction=Direction.SOUTHWEST
            ),
        ]

    def test_add_station(self):
        rail_planner = RailPlanner()

        # adding station to nothing should do nothing
        rail_planner.add_station("train-stop", "station name")
        assert len(rail_planner.entities) == 0

        # Test right side
        rail_planner.move_forward()
        rail_planner.add_station("train-stop", "station 1")
        assert len(rail_planner.entities) == 2
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTH
            ),
            TrainStop(
                "train-stop",
                station="station 1",
                tile_position=(2, 0),
                direction=Direction.NORTH,
            ),
        ]

        print(type(rail_planner.entities[0].direction))

        # Test left side
        rail_planner.add_station("train-stop", "station 2", right=False)
        assert len(rail_planner.entities) == 3
        assert rail_planner.entities._root == [
            StraightRail(
                "straight-rail", tile_position=(0, 0), direction=Direction.NORTH
            ),
            TrainStop(
                "train-stop",
                station="station 1",
                tile_position=(2, 0),
                direction=Direction.NORTH,
            ),
            TrainStop(
                "train-stop",
                station="station 2",
                tile_position=(-2, 0),
                direction=Direction.SOUTH,
            ),
        ]

        # Error on curved rails
        rail_planner.head_position = (10, 0)
        rail_planner.turn_right()
        with pytest.raises(DraftsmanError):
            rail_planner.add_station("train-stop", "error station")

        # Error on diagonal rails
        rail_planner.move_forward()
        with pytest.raises(DraftsmanError):
            rail_planner.add_station("train-stop", "error station")
