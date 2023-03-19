# railplanner.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.group import Group
from draftsman.constants import Direction
from draftsman.error import DraftsmanError

from draftsman.data import items

import math
from typing import Union


class RailPlanner(Group):
    """
    Rail planner. Allows the user to specify rails in a pen-drawing or turtle-
    based manner. Currently unimplemented.
    """

    def __init__(
        self, name, start_position=[0, 0], head_direction=Direction.NORTH, **kwargs
    ):
        # type: (str, Union[list, dict, tuple], int, **dict) -> None
        super(RailPlanner, self).__init__(**kwargs)
        if name in items.raw and items.raw[name]["type"] == "rail-planner":
            self.name = name
        else:
            raise DraftsmanError("'{}' is not a valid rail-planner")
        self.straight_rail = items.raw[name]["straight_rail"]
        self.curved_rail = items.raw[name]["curved_rail"]

        self.head_position = start_position
        self.head_direction = head_direction

    # =========================================================================

    @property
    def head_position(self):
        # type: () -> dict
        """
        TODO
        """
        return self._head_position

    @head_position.setter
    def head_position(self, value):
        # type: (Union[dict, list, tuple]) -> None
        if self.parent:
            raise DraftsmanError(
                "Cannot change position of Group while it's inside a Collection"
            )

        if "x" in value and "y" in value:
            self._head_position = {
                "x": math.floor(value["x"]),
                "y": math.floor(value["y"]),
            }
        elif isinstance(value, (list, tuple)):
            self._head_position = {"x": math.floor(value[0]), "y": math.floor(value[1])}
        else:
            raise TypeError("Incorrectly formatted position ({})".format(value))

    # =========================================================================

    @property
    def head_direction(self):
        # type: () -> Direction
        """
        TODO
        """
        return self._head_direction

    @head_direction.setter
    def head_direction(self, value):
        # type: (Direction) -> None
        self._head_direction = Direction(value)
        self._direction = Direction((value + 2) % 8)

    # =========================================================================

    @property
    def direction(self):
        # type: () -> Direction
        """
        TODO
        """
        return self._direction

    @direction.setter
    def direction(self, value):
        # type: (Direction) -> None
        self._direction = Direction(value)

    # =========================================================================

    def move_forward(self, amount=1):
        # type: (int) -> None
        """
        TODO
        """
        raise NotImplementedError
        offset_matrix = [
            {
                "x": 0,
                "y": -2,
            },  # 0 (North)
            {"x": 2, "y": 0, "d": 5},  # 1 (Northeast)
            {"x": 2, "y": 0},  # 2 (East)
            {"x": 2, "y": 0, "d": 7},  # 3 (Southeast)
            {"x": 0, "y": 2},  # 4 (South)
            {"x": 0, "y": 2, "d": 1},  # 5 (Southwest)
            {"x": -2, "y": 0},  # 6 (West)
            {"x": 0, "y": 2, "d": 3},  # 7 (Northwest)
        ]
        travel_dir = {
            1: {"x": 1, "y": -1},
            3: {"x": 1, "y": 1},
            5: {"x": -1, "y": 1},
            7: {"x": -1, "y": -1},
        }
        if self.head_direction in {0, 2, 4, 6}:  # Straight rails, easy
            offset = offset_matrix[self.head_direction]
            for _ in range(amount):
                self.entities.append(
                    self.straight_rail,
                    tile_position=self.head_position,
                    direction=self.direction,
                )
                self.head_position["x"] += offset["x"]
                self.head_position["y"] += offset["y"]
        else:  # Diagonal rails, annoying
            self.direction = (self.head_direction + 2) % 8
            for _ in range(amount):
                print(self.head_position)
                print(self.direction, int(self.direction))
                offset = offset_matrix[self.direction]
                self.entities.append(
                    self.straight_rail,
                    tile_position=self.head_position,
                    direction=self.direction,
                )
                print(offset)
                move_dir = travel_dir[self.head_direction]
                self.head_position["x"] += offset["x"] * move_dir["x"]
                self.head_position["y"] += offset["y"] * move_dir["y"]
                self.direction = offset["d"]

    def turn_left(self, amount=1):
        # type: (int) -> None
        """
        TODO
        """
        raise NotImplementedError

    def turn_right(self, amount=1):
        # type: (int) -> None
        """
        TODO
        """
        raise NotImplementedError
