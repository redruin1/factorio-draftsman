# constants.py

"""
Enumerations of frequently used constants.
"""

from draftsman.classes.vector import Vector

from enum import IntEnum, Enum
import math


class Direction(IntEnum):
    """
    Factorio direction enum. Encompasses all 8 cardinal directions and diagonals
    in the range [0, 7] where north is 0 and increments clockwise.

    * ``NORTH`` (Default)
    * ``NORTHEAST``
    * ``EAST``
    * ``SOUTHEAST``
    * ``SOUTH``
    * ``SOUTHWEST``
    * ``WEST``
    * ``NORTHWEST``
    """

    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7

    def opposite(self):
        # type: () -> Direction
        """
        Returns the direction opposite this one.

        :returns: A new :py:class:`Direction`.
        """
        return Direction((self.value + 4) % 8)
    
    def next(self, eight_way=False):
        # type: (bool) -> None
        """
        Returns the direction adjacent direction.
        """
        return Direction((self.value + 1 + (not eight_way)) % 8)
    
    def previous(self, eight_way=False):
        # type: (bool) -> None
        """
        TODO
        """
        return Direction((self.value - 1 - (not eight_way)) % 8)

    def to_orientation(self):
        # type: () -> float
        """
        TODO
        """
        mapping = {
            # fmt: off
            Direction.NORTH:     Orientation.NORTH,
            Direction.NORTHEAST: Orientation.NORTHEAST,
            Direction.EAST:      Orientation.EAST,
            Direction.SOUTHEAST: Orientation.SOUTHEAST,
            Direction.SOUTH:     Orientation.SOUTH,
            Direction.SOUTHWEST: Orientation.SOUTHWEST,
            Direction.WEST:      Orientation.WEST,
            Direction.NORTHWEST: Orientation.NORTHWEST,
            # fmt: on
        }
        return mapping[self]

    def to_vector(self, magnitude=1):
        # type: (float) -> Vector
        """
        TODO
        """
        srt2 = 2 ** (-1/2)
        mapping = {
            # fmt: off
            Direction.NORTH:     Vector(0, -1),
            Direction.NORTHEAST: Vector(srt2, -srt2),
            Direction.EAST:      Vector(1, 0),
            Direction.SOUTHEAST: Vector(srt2, srt2),
            Direction.SOUTH:     Vector(0, 1),
            Direction.SOUTHWEST: Vector(-srt2, srt2),
            Direction.WEST:      Vector(-1, 0),
            Direction.NORTHWEST: Vector(-srt2, -srt2),
            # fmt: on
        }
        return mapping[self] * magnitude


class Orientation(float):
    """
    Factorio orientation enum. Represents the direction an object is facing with
    a floating point number in the range [0.0, 1.0) where north is 0.0 and 
    increases clockwise.

    * ``NORTH`` (Default)
    * ``NORTHEAST``
    * ``EAST``
    * ``SOUTHEAST``
    * ``SOUTH``
    * ``SOUTHWEST``
    * ``WEST``
    * ``NORTHWEST``
    """
    NORTH = 0.0
    NORTHEAST = 0.125
    EAST = 0.25
    SOUTHEAST = 0.375
    SOUTH = 0.5
    SOUTHWEST = 0.625
    WEST = 0.75
    NORTHWEST = 0.875

    def __init__(self, value):
        self.value = value % 1.0

    def opposite(self):
        # type: () -> Orientation
        """
        TODO
        """
        return self + 0.5

    def to_direction(self, eight_way=False):
        # type: (bool) -> Direction
        """
        TODO
        """
        if eight_way:
            return Direction(round(self.value * 8))
        else:
            return Direction(round(self.value * 4) * 2)
    
    def to_vector(self, magnitude=1):
        # type: (float) -> Vector
        """
        TODO
        """
        angle = self.value * math.pi * 2
        return Vector(math.sin(angle), -math.cos(angle)) * magnitude
    
    def in_range(self, min_val, max_val):
        # type: (Orientation, Orientation) -> bool
        """
        TODO
        """
        if min_val > max_val:
            min_val -= 1
        return min_val <= self.value <= max_val

    def __add__(self, other):
        # type: (Orientation) -> Orientation
        """
        Gets the addition of two orientations, modulo 1 to remain within the 
        valid range for a :py:class:`Orientation`.
        """
        other = Orientation(other)
        return Orientation((self.value + other.value) % 1.0)

    def __sub__(self, other):
        # type: (Orientation) -> Orientation
        """
        Gets the subtraction of two orientations, modulo 1 to remain within the 
        valid range for a :py:class:`Orientation`.
        """
        other = Orientation(other)
        return Orientation((self.value - other.value) % 1.0)


class ReadMode(IntEnum):
    """
    Determines what manner belts and inserters should send their content signal.

    * ``PULSE``: Pulse the signal for one tick when first detected. (Default)
    * ``HOLD``: Hold the signal for as long as the item is present.
    """

    PULSE = 0
    HOLD = 1


class MiningDrillReadMode(IntEnum):
    """
    Used to specify whether the mining drill will read the contents beneath it
    or the entire resource patch.

    Determines the manner in which a mining drill reads the resources beneath it.

    * ``UNDER_DRILL``: Only return the resources directly minable by this drill.
        (Default)
    * ``TOTAL_PATCH``: Return the entire contents of the ore patches the drill
        is over.
    """

    UNDER_DRILL = 0
    TOTAL_PATCH = 1


class InserterModeOfOperation(IntEnum):
    """
    Inserter circuit control constants. Determines how the Entity should behave
    when connected to a circuit network.

    * ``ENABLE_DISABLE``: Turns the inserter on or off depending on the circuit
        condition. (Default)
    * ``SET_FILTERS``: Sets the inserter's filter signals based on read signals.
    * ``READ_HAND_CONTENTS``: Reads the contents of the inserter's hand and
        sends it to the connected wire(s).
    * ``NONE``: Does nothing.
    * ``SET_STACK_SIZE``: Sets the stack size override to the value of an input
        signal.
    """

    ENABLE_DISABLE = 0
    SET_FILTERS = 1
    READ_HAND_CONTENTS = 2
    NONE = 3
    SET_STACK_SIZE = 4


class LogisticModeOfOperation(IntEnum):
    """
    Logistics container circuit control constants. Determines how the Entity
    should behave when connected to a circuit network.

    * ``SEND_CONTENTS``: Reads the inventory of the container and sends it to
      the connected circuit network. (Default)
    * ``SET_REQUESTS``: Sets the item requests based on the input signals to the
      container.
    """

    SEND_CONTENTS = 0
    SET_REQUESTS = 1


class FilterMode(IntEnum):
    """
    Filter mode constant.

    * ``WHITELIST``: Include only the listed items. (Default)
    * ``BLACKLIST``: Exclude only the listed items.
    """

    WHITELIST = 0
    BLACKLIST = 1


class TileSelectionMode(IntEnum):
    """
    Tile selection mode for :py:class:`.UpgradePlanner`.

    * ``NORMAL``: Constructed tiles are only removed if there are no entities in
        the selected area (Default)
    * ``ALWAYS``: Constructed tiles are always scheduled for deconstruction,
        regardless of selection contents.
    * ``NEVER``: Constructed tiles are never scheduled for deconstruction,
        regardless of selection contents.
    * ``ONLY``: Only tiles are selected for deconstruction; entities are
        completely ignored when using this mode.
    """

    NORMAL = 0
    ALWAYS = 1
    NEVER = 2
    ONLY = 3


class Ticks(IntEnum):
    """
    Constant values that correspond to the number of Factorio ticks for that 
    measure of time at 1.0 game-speed.

    * ``SECOND``: 60
    * ``MINUTE``: 60 * ``SECOND``
    * ``HOUR``  : 60 * ``MINUTE``
    * ``DAY``   : 24 * ``HOUR``
    """

    SECOND = 60
    MINUTE = 60 * SECOND
    HOUR   = 60 * MINUTE
    DAY    = 24 * HOUR


class WaitConditionType(str, Enum):
    """
    All valid string identifiers for the type of a train's 
    :py:class:`WaitCondition` object.

    * ``TIME_PASSED``: Triggered when a certain number of ticks has passed.
    * ``INACTIVITY``: Triggered when the state of the train currently at the 
        station is unaltered for a number of ticks.
    * ``FULL_CARGO``: Triggered when there is no more room in any of the stopped
        train's wagons.
    * ``EMPTY_CARGO``: Triggered when there is no more cargo in any of the 
        stopped train's wagons.
    * ``ITEM_COUNT``: Triggered when the count of some contained item passes 
        some specified condition.
    * ``FLUID_COUNT``: Triggered when the count of some contained fluid passes 
        some specified condition.
    * ``CIRCUIT_CONDITION``: Triggered when a circuit signal passed to the 
        train stop passes some specified condition.
    * ``PASSENGER_PRESENT``: Triggered if a player is inside any of the stopped
        train's wagons.
    * ``PASSENGER_NOT_PRESENT``: Triggered if a player is not inside any of the 
        stopped train's wagons.
    """

    TIME_PASSED = "time"
    INACTIVITY = "inactivity"
    FULL_CARGO = "full"
    EMPTY_CARGO = "empty"
    ITEM_COUNT = "item_count"
    FLUID_COUNT = "fluid_count"
    CIRCUIT_CONDITION = "circuit"
    PASSENGER_PRESENT = "passenger_present"
    PASSENGER_NOT_PRESENT = "passenger_not_present"


class WaitConditionCompareType(str, Enum):
    """
    All valid string identitfiers for the type of comparison between multiple
    :py:class:`WaitCondition` objects.

    * ``AND``: Boolean AND this condition with the subsequent one.
    * ``OR``: Boolean OR this conditions with the subsequent one.
    """

    AND = "and"
    OR = "or"