# constants.py

from enum import IntEnum


class Direction(IntEnum):
    """
    Factorio direction enum. Encompasses all 8 cardinal directions and diagonals
    where north is 0.
    """
    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7

    # def __repr__(self):
    #     return "<{}.{}: {}>".format(type(self).__name__, self.name, self.value)

    # def __str__(self):
    #     return str(self.value)
        

class ReadMode(IntEnum):
    """
    Used on belts and inserters to indicate whether to pulse or hold their 
    contents.
    """
    PULSE = 0
    HOLD = 1

    # def __repr__(self):
    #     return "<{}.{}: {}>".format(type(self).__name__, self.name, self.value)

    # def __str__(self):
    #     return str(self.value)

class MiningDrillReadMode(IntEnum):
    """
    Used to specify whether the mining drill will read the contents beneath it
    or the entire resource patch.
    """
    UNDER_DRILL = 0
    TOTAL_PATCH = 1

    # def __repr__(self):
    #     return "<{}.{}: {}>".format(type(self).__name__, self.name, self.value)

    # def __str__(self):
    #     return str(self.value)

class ModeOfOperation(IntEnum):
    """
    TODO
    """
    ENABLE_DISABLE = 0
    SET_FILTERS = 1
    NONE = 3

    # def __repr__(self):
    #     return "<{}.{}: {}>".format(type(self).__name__, self.name, self.value)

    # def __str__(self):
    #     return str(self.value)