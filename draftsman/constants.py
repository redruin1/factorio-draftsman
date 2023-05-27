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
    in the range [0, 7] where north is 0 and increments clockwise. Provides a
    number of convenience constants and functions over working with a raw int
    value.

    * ``NORTH`` (0) (Default)
    * ``NORTHEAST`` (1)
    * ``EAST`` (2)
    * ``SOUTHEAST`` (3)
    * ``SOUTH`` (4)
    * ``SOUTHWEST`` (5)
    * ``WEST`` (6)
    * ``NORTHWEST`` (7)
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
        # type: (bool) -> Direction
        """
        Returns the direction one unit clockwise from the current direction.
        ``eight_way`` determines whether or not to treat the next-most direction
        from a four-way or eight-way perspective; for example:

        .. example:: python

            >>> Direction.NORTH.next(eight_way=False)
            <Direction.EAST: 2>
            >>> Direction.NORTH.next(eight_way=True)
            <Direction.NORTHEAST: 1>

        :param eight_way: Whether to increment the current direction by 1 or 2
            units.

        :returns: A new :py:class:`Direction` object.
        """
        return Direction((self.value + 1 + (not eight_way)) % 8)

    def previous(self, eight_way=False):
        # type: (bool) -> Direction
        """
        Returns the direction one unit counter-clockwise from the current
        direction. ``eight_way`` determines whether or not to treat the
        previous-most direction from a four-way or eight-way perspective; for
        example:

        .. example:: python

            >>> Direction.NORTH.previous(eight_way=False)
            <Direction.WEST: 6>
            >>> Direction.NORTH.previous(eight_way=True)
            <Direction.NORTHWEST: 7>

        :param eight_way: Whether to increment the current direction by 1 or 2
            units.

        :returns: A new :py:class:`Direction` object.
        """
        return Direction((self.value - 1 - (not eight_way)) % 8)

    def to_orientation(self):
        # type: () -> Orientation
        """
        Converts this direction to an :py:class:`Orientation` of corresponding
        value.

        .. example:: python

            >>> Direction.EAST.to_orientation()
            <Orientation.EAST: 0.25>

        :returns: An equivalent :py:class:`Orientation` object.
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
        Converts a :py:class:`Direction` into an equivalent 2-dimensional vector,
        for various linear operations. Works with both four-way and eight-way
        directions. Returned vectors are unit-length, unless ``magnitude`` is
        altered.

        .. example:: python

            >>> Direction.NORTH.to_vector(magnitude=2)
            <Vector>(0, -2)
            >>> Direction.SOUTHWEST.to_vector()
            <Vector>(-0.7071067811865476, 0.7071067811865476)

        :param magnitude: The magnitude (total length) of the vector to create.

        :returns: A new :py:class:`Vector` object pointing in the correct
            direction.
        """
        srt2 = 2 ** (-1 / 2)
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


class OrientationMeta(type):
    _mapping = {
        "NORTH": 0.0,
        "NORTHEAST": 0.125,
        "EAST": 0.25,
        "SOUTHEAST": 0.375,
        "SOUTH": 0.5,
        "SOUTHWEST": 0.625,
        "WEST": 0.75,
        "NORTHWEST": 0.875,
    }

    def __getattr__(cls, name):
        if name in cls._mapping:
            return Orientation(cls._mapping[name])
        else:
            super().__getattr__(name)

    # NORTH = Orientation(0.0)


class Orientation(float):
    """
    Factorio orientation enum. Represents the direction an object is facing with
    a floating point number in the range [0.0, 1.0) where north is 0.0 and
    increases clockwise. Provides a number of convenience constants and
    functions over working with a raw float value.

    .. NOTE::

        Currently only supports addition and subtraction; if you want to perform
        more complex operations it's best to convert it to a float and then convert
        it back to an Orientation when complete.

    * ``NORTH`` (0.0) (Default)
    * ``NORTHEAST`` (0.125)
    * ``EAST`` (0.25)
    * ``SOUTHEAST`` (0.375)
    * ``SOUTH`` (0.5)
    * ``SOUTHWEST`` (0.625)
    * ``WEST`` (0.75)
    * ``NORTHWEST`` (0.875)
    """

    # Note: These are overwritten with Orientation() instances after definition
    NORTH = 0.0
    NORTHEAST = 0.125
    EAST = 0.25
    SOUTHEAST = 0.375
    SOUTH = 0.5
    SOUTHWEST = 0.625
    WEST = 0.75
    NORTHWEST = 0.875

    def __init__(self, value):
        self._value_ = value
        _reverse_mapping = {
            0.0: "NORTH",
            0.125: "NORTHEAST",
            0.25: "EAST",
            0.375: "SOUTHEAST",
            0.5: "SOUTH",
            0.625: "SOUTHWEST",
            0.75: "WEST",
            0.875: "NORTHWEST",
        }
        if value in _reverse_mapping:
            self._name_ = _reverse_mapping[value]
        else:
            self._name_ = None

    def opposite(self):
        # type: () -> Orientation
        """
        Returns the direction opposite this one. For cardinal four-way and eight-
        way directions calling this function should always return the "true"
        opposite; but when calling on an arbitrary orientation the opposite may
        succumb to floating point error:

        .. example:: python

            >>> Orientation.NORTH.opposite()
            <Orientation.SOUTH: 0.5>
            >>> Orientation.NORTHWEST.opposite()
            <Orientation.SOUTHEAST: 0.375>
            >>> Orientation(0.9).opposite()
            <Orientation: 0.3999999999999999>

        :returns: A new :py:class:`Orientation` object.
        """
        return self + 0.5

    def to_direction(self, eight_way=False):
        # type: (bool) -> Direction
        """
        Converts the orientation to a :py:class:`Direction` instance. If the
        orientation is imprecise, the orientation will be rounded to either the
        closest four-way or eight-way direction.

        :param eight_way: Whether to round to the closest four-way direction or
            eight-way direction.

        :returns: A new :py:class:`Direction` object.
        """
        if eight_way:
            return Direction(round(self._value_ * 8))
        else:
            return Direction(round(self._value_ * 4) * 2)

    def to_vector(self, magnitude=1):
        # type: (float) -> Vector
        """
        Converts a :py:class:`Orientation` into an equivalent 2-dimensional
        vector, for various linear operations. Returned vectors are unit-length,
        unless ``magnitude`` is altered.

        .. example:: python

            >>> Orientation.NORTH.to_vector(magnitude=2)
            <Vector>(0, -2)
            >>> Orientation.SOUTHWEST.to_vector()
            <Vector>(-0.7071067811865476, 0.7071067811865476)

        :param magnitude: The magnitude (total length) of the vector to create.

        :returns: A new :py:class:`Vector` object pointing in the correct
            direction.
        """
        angle = self._value_ * math.pi * 2
        return Vector(math.sin(angle), -math.cos(angle)) * magnitude

    def __add__(self, other):
        other = Orientation(other)
        return Orientation((self._value_ + other._value_) % 1.0)

    def __sub__(self, other):
        other = Orientation(other)
        return Orientation((self._value_ - other._value_) % 1.0)

    def __repr__(self) -> str:
        # Matches the format of Enum unless the value isn't one of the special
        # cardinal directions
        if self._name_ is not None:
            special_name = "." + self._name_
        else:
            special_name = ""
        return "<%s%s: %r>" % (self.__class__.__name__, special_name, self._value_)


# Note: this is a bit scuffed
# Ideally Orientation would be the same as an Enum, but with no restriction on
# having it's value match the 8 special directions we define
# For now I'm just gonna do this and wait to do some actual research on
# metaclasses
Orientation.NORTH = Orientation(0.0)
Orientation.NORTHEAST = Orientation(0.125)
Orientation.EAST = Orientation(0.25)
Orientation.SOUTHEAST = Orientation(0.375)
Orientation.SOUTH = Orientation(0.5)
Orientation.SOUTHWEST = Orientation(0.625)
Orientation.WEST = Orientation(0.75)
Orientation.NORTHWEST = Orientation(0.875)


class ReadMode(IntEnum):
    """
    Determines what manner belts and inserters should send their content signal.

    * ``PULSE``: (0) Pulse the signal for one tick when first detected.
        (Default)
    * ``HOLD``: (1) Hold the signal for as long as the item is present.
    """

    PULSE = 0
    HOLD = 1


class MiningDrillReadMode(IntEnum):
    """
    Used to specify whether the mining drill will read the contents beneath it
    or the entire resource patch.

    Determines the manner in which a mining drill reads the resources beneath it.

    * ``UNDER_DRILL``: (0) Only return the resources directly minable by this
        drill. (Default)
    * ``TOTAL_PATCH``: (1) Return the entire contents of the ore patches the
        drill is over.
    """

    UNDER_DRILL = 0
    TOTAL_PATCH = 1


class InserterModeOfOperation(IntEnum):
    """
    Inserter circuit control constants. Determines how the Entity should behave
    when connected to a circuit network.

    * ``ENABLE_DISABLE``: (0) Turns the inserter on or off depending on the
        circuit condition. (Default)
    * ``SET_FILTERS``: (1) Sets the inserter's filter signals based on read
        signals.
    * ``READ_HAND_CONTENTS``: (2) Reads the contents of the inserter's hand and
        sends it to the connected wire(s).
    * ``NONE``: (3) Does nothing.
    * ``SET_STACK_SIZE``: (4) Sets the stack size override to the value of an
        input signal.
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

    * ``SEND_CONTENTS``: (0) Reads the inventory of the container and sends it
        to the connected circuit network. (Default)
    * ``SET_REQUESTS``: (1) Sets the item requests based on the input signals to
        the container.
    """

    SEND_CONTENTS = 0
    SET_REQUESTS = 1


class FilterMode(IntEnum):
    """
    Filter mode constant.

    * ``WHITELIST``: (0) Include only the listed items. (Default)
    * ``BLACKLIST``: (1) Exclude only the listed items.
    """

    WHITELIST = 0
    BLACKLIST = 1


class TileSelectionMode(IntEnum):
    """
    Tile selection mode for :py:class:`.UpgradePlanner`.

    * ``NORMAL``: (0) Constructed tiles are only removed if there are no
        entities in the selected area (Default)
    * ``ALWAYS``: (1) Constructed tiles are always scheduled for deconstruction,
        regardless of selection contents.
    * ``NEVER``: (2) Constructed tiles are never scheduled for deconstruction,
        regardless of selection contents.
    * ``ONLY``: (3) Only tiles are selected for deconstruction; entities are
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
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR


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
