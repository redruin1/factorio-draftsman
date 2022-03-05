# constants.py

from enum import IntEnum


class Direction(IntEnum):
    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7

class ReadMode(IntEnum):
    PULSE = 0
    HOLD = 1

class MiningDrillReadMode(IntEnum):
    UNDER_DRILL = 0
    TOTAL_PATCH = 1

class ModeOfOperation(IntEnum):
    ENABLE_DISABLE = 0
    SET_FILTERS = 1
    NONE = 3