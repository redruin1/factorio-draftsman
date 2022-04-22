# constants.py

"""
TODO
"""

from enum import IntEnum


class Direction(IntEnum):
    """
    Factorio direction enum. Encompasses all 8 cardinal directions and diagonals
    where north is 0 and increments clockwise.
    """

    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7


class ReadMode(IntEnum):
    """
    Used on belts and inserters to indicate whether to pulse or hold their
    content signal.
    """

    PULSE = 0
    HOLD = 1


class MiningDrillReadMode(IntEnum):
    """
    Used to specify whether the mining drill will read the contents beneath it
    or the entire resource patch.
    """

    UNDER_DRILL = 0
    TOTAL_PATCH = 1


class ModeOfOperation(IntEnum):
    """
    TODO
    """

    ENABLE_DISABLE = 0
    SET_FILTERS = 1
    NONE = 3
