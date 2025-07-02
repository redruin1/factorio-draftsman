# constants.py

"""
Enumerations of frequently used constants.
"""

from draftsman.classes.vector import Vector
from draftsman.serialization import draftsman_converters

from datetime import timedelta
from enum import IntEnum, Enum
from functools import total_ordering
import math


class Direction(IntEnum):
    """
    Factorio direction enum. Encompasses all 16 cardinal directions, diagonals,
    and half-dagonals in the range [0, 15] where north is 0 and increments
    clockwise. Provides a number of convenience constants and functions over
    working with a raw int value.

    * ``NORTH     (0)`` (Default)
    * ``NORTHEAST (1)``
    * ``EAST      (2)``
    * ``SOUTHEAST (3)``
    * ``SOUTH     (4)``
    * ``SOUTHWEST (5)``
    * ``WEST      (6)``
    * ``NORTHWEST (7)``
    """

    NORTH = 0
    NORTHNORTHEAST = 1
    NORTHEAST = 2
    EASTNORTHEAST = 3
    EAST = 4
    EASTSOUTHEAST = 5
    SOUTHEAST = 6
    SOUTHSOUTHEAST = 7
    SOUTH = 8
    SOUTHSOUTHWEST = 9
    SOUTHWEST = 10
    WESTSOUTHWEST = 11
    WEST = 12
    WESTNORTHWEST = 13
    NORTHWEST = 14
    NORTHNORTHWEST = 15

    def opposite(self) -> "Direction":
        """
        Returns the direction opposite this one.

        .. doctest:: [constants]

            >>> Direction.NORTH.opposite()
            <Direction.SOUTH: 4>

        :returns: A new :py:class:`Direction`.
        """
        return Direction((self.value + 8) % 16)

    def next(self, eight_way: bool = False) -> "Direction":
        """
        Returns the direction one unit clockwise from the current direction.
        ``eight_way`` determines whether or not to treat the next-most direction
        from a four-way or eight-way perspective; for example:

        .. doctest:: [constants]

            >>> Direction.NORTH.next(eight_way=False)
            <Direction.EAST: 4>
            >>> Direction.NORTH.next(eight_way=True)
            <Direction.NORTHEAST: 2>

        :param eight_way: Whether to increment the current direction by 2 or 4
            units.

        :returns: A new :py:class:`Direction` object.
        """
        return Direction((self.value + (4 if not eight_way else 2)) % 16)

    def previous(self, eight_way: bool = False) -> "Direction":
        """
        Returns the direction one unit counter-clockwise from the current
        direction. ``eight_way`` determines whether or not to treat the
        previous-most direction from a four-way or eight-way perspective; for
        example:

        .. doctest:: [constants]

            >>> Direction.NORTH.previous(eight_way=False)
            <Direction.WEST: 6>
            >>> Direction.NORTH.previous(eight_way=True)
            <Direction.NORTHWEST: 7>

        :param eight_way: Whether to increment the current direction by 1 or 2
            units.

        :returns: A new :py:class:`Direction` object.
        """
        return Direction((self.value - (4 if not eight_way else 2)) % 16)

    def to_closest_valid_direction(self, valid_directions) -> "Direction":
        """
        Floor this direction to the closest valid direction. ``valid_directions``
        must be exactly one of the constants ``FOUR_WAY_DIRECTIONS``,
        ``EIGHT_WAY_DIRECTIONS``, or ``SIXTEEN_WAY_DIRECTIONS``.
        """
        if valid_directions is FOUR_WAY_DIRECTIONS:
            return Direction((round(self.value / 4) * 4) % 16)
        elif valid_directions is EIGHT_WAY_DIRECTIONS:
            return Direction((math.floor(self.value / 2) * 2) % 16)
        else:  # valid_directions is SIXTEEN_WAY_DIRECTIONS:
            return self

    def to_orientation(self) -> "Orientation":
        """
        Converts this direction to an :py:class:`Orientation` of corresponding
        value.

        .. doctest:: [constants]

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

    def to_vector(self, magnitude: float = 1.0) -> Vector:
        """
        Converts a :py:class:`Direction` into an equivalent 2-dimensional vector,
        for various linear operations. Works with both four-way and eight-way
        directions. Returned vectors are unit-length, unless ``magnitude`` is
        specified.

        .. doctest:: [constants]

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
            Direction.NORTHNORTHEAST: Vector(0, 0),
            Direction.NORTHEAST: Vector(srt2, -srt2),
            Direction.EASTNORTHEAST: Vector(0, 0),
            Direction.EAST:      Vector(1, 0),
            Direction.EASTSOUTHEAST: Vector(0, 0),
            Direction.SOUTHEAST: Vector(srt2, srt2),
            Direction.SOUTHSOUTHEAST: Vector(0, 0),
            Direction.SOUTH:     Vector(0, 1),
            Direction.SOUTHSOUTHWEST: Vector(0, 0),
            Direction.SOUTHWEST: Vector(-srt2, srt2),
            Direction.WESTSOUTHWEST: Vector(0, 0),
            Direction.WEST:      Vector(-1, 0),
            Direction.WESTNORTHWEST: Vector(0, 0),
            Direction.NORTHWEST: Vector(-srt2, -srt2),
            Direction.NORTHNORTHWEST: Vector(0, 0)
            # fmt: on
        }
        return mapping[self] * magnitude

    def to_legacy(self) -> "LegacyDirection":
        """
        Converts this :py:class:`.Direction` to a :py:class:`.LegacyDirection`.
        """
        mapping = {
            # fmt: off
            Direction.NORTH:     LegacyDirection.NORTH,
            Direction.NORTHEAST: LegacyDirection.NORTHEAST,
            Direction.EAST:      LegacyDirection.EAST,
            Direction.SOUTHEAST: LegacyDirection.SOUTHEAST,
            Direction.SOUTH:     LegacyDirection.SOUTH,
            Direction.SOUTHWEST: LegacyDirection.SOUTHWEST,
            Direction.WEST:      LegacyDirection.WEST,
            Direction.NORTHWEST: LegacyDirection.NORTHWEST,
            # fmt: on
        }
        return mapping[self]


FOUR_WAY_DIRECTIONS = {Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST}

EIGHT_WAY_DIRECTIONS = {
    Direction.NORTH,
    Direction.NORTHEAST,
    Direction.EAST,
    Direction.SOUTHEAST,
    Direction.SOUTH,
    Direction.SOUTHWEST,
    Direction.WEST,
    Direction.NORTHWEST,
}

SIXTEEN_WAY_DIRECTIONS = {direction for direction in Direction}


class LegacyDirection(IntEnum):
    """
    Factorio direction enum. Encompasses all 8 cardinal directions and diagonals
    in the range [0, 7] where north is 0 and increments clockwise. Provides a
    number of convenience constants and functions over working with a raw int
    value.

    * ``NORTH     (0)`` (Default)
    * ``NORTHEAST (1)``
    * ``EAST      (2)``
    * ``SOUTHEAST (3)``
    * ``SOUTH     (4)``
    * ``SOUTHWEST (5)``
    * ``WEST      (6)``
    * ``NORTHWEST (7)``
    """

    NORTH = 0
    NORTHEAST = 1
    EAST = 2
    SOUTHEAST = 3
    SOUTH = 4
    SOUTHWEST = 5
    WEST = 6
    NORTHWEST = 7

    def opposite(self) -> "LegacyDirection":
        """
        Returns the direction opposite this one.

        .. doctest:: [constants]

            >>> Direction.NORTH.opposite()
            <Direction.SOUTH: 4>

        :returns: A new :py:class:`Direction`.
        """
        return LegacyDirection((self.value + 4) % 8)

    def next(self, eight_way: bool = False) -> "LegacyDirection":
        """
        Returns the direction one unit clockwise from the current direction.
        ``eight_way`` determines whether or not to treat the next-most direction
        from a four-way or eight-way perspective; for example:

        .. doctest:: [constants]

            >>> Direction.NORTH.next(eight_way=False)
            <Direction.EAST: 2>
            >>> Direction.NORTH.next(eight_way=True)
            <Direction.NORTHEAST: 1>

        :param eight_way: Whether to increment the current direction by 1 or 2
            units.

        :returns: A new :py:class:`Direction` object.
        """
        return LegacyDirection((self.value + 1 + (not eight_way)) % 8)

    def previous(self, eight_way: bool = False) -> "LegacyDirection":
        """
        Returns the direction one unit counter-clockwise from the current
        direction. ``eight_way`` determines whether or not to treat the
        previous-most direction from a four-way or eight-way perspective; for
        example:

        .. doctest:: [constants]

            >>> Direction.NORTH.previous(eight_way=False)
            <Direction.WEST: 6>
            >>> Direction.NORTH.previous(eight_way=True)
            <Direction.NORTHWEST: 7>

        :param eight_way: Whether to increment the current direction by 1 or 2
            units.

        :returns: A new :py:class:`Direction` object.
        """
        return LegacyDirection((self.value - 1 - (not eight_way)) % 8)

    def to_orientation(self) -> "Orientation":
        """
        Converts this direction to an :py:class:`Orientation` of corresponding
        value.

        .. doctest:: [constants]

            >>> Direction.EAST.to_orientation()
            <Orientation.EAST: 0.25>

        :returns: An equivalent :py:class:`Orientation` object.
        """
        mapping = {
            # fmt: off
            LegacyDirection.NORTH:     Orientation.NORTH,
            LegacyDirection.NORTHEAST: Orientation.NORTHEAST,
            LegacyDirection.EAST:      Orientation.EAST,
            LegacyDirection.SOUTHEAST: Orientation.SOUTHEAST,
            LegacyDirection.SOUTH:     Orientation.SOUTH,
            LegacyDirection.SOUTHWEST: Orientation.SOUTHWEST,
            LegacyDirection.WEST:      Orientation.WEST,
            LegacyDirection.NORTHWEST: Orientation.NORTHWEST,
            # fmt: on
        }
        return mapping[self]

    def to_vector(self, magnitude: float = 1.0) -> Vector:
        """
        Converts a :py:class:`Direction` into an equivalent 2-dimensional vector,
        for various linear operations. Works with both four-way and eight-way
        directions. Returned vectors are unit-length, unless ``magnitude`` is
        specified.

        .. doctest:: [constants]

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
            LegacyDirection.NORTH:     Vector(0, -1),
            LegacyDirection.NORTHEAST: Vector(srt2, -srt2),
            LegacyDirection.EAST:      Vector(1, 0),
            LegacyDirection.SOUTHEAST: Vector(srt2, srt2),
            LegacyDirection.SOUTH:     Vector(0, 1),
            LegacyDirection.SOUTHWEST: Vector(-srt2, srt2),
            LegacyDirection.WEST:      Vector(-1, 0),
            LegacyDirection.NORTHWEST: Vector(-srt2, -srt2),
            # fmt: on
        }
        return mapping[self] * magnitude

    def to_modern(self) -> Direction:
        """
        Converts this :py:class:`.LegactDirection` to a :py:class:`.Direction`.
        """
        mapping = {
            # fmt: off
            LegacyDirection.NORTH:     Direction.NORTH,
            LegacyDirection.NORTHEAST: Direction.NORTHEAST,
            LegacyDirection.EAST:      Direction.EAST,
            LegacyDirection.SOUTHEAST: Direction.SOUTHEAST,
            LegacyDirection.SOUTH:     Direction.SOUTH,
            LegacyDirection.SOUTHWEST: Direction.SOUTHWEST,
            LegacyDirection.WEST:      Direction.WEST,
            LegacyDirection.NORTHWEST: Direction.NORTHWEST,
            # fmt: on
        }
        return mapping[self]


draftsman_converters.get_version((1, 0)).register_structure_hook(  # pragma: no branch
    Direction, lambda d, _: LegacyDirection(d).to_modern()
)
draftsman_converters.get_version((1, 0)).register_unstructure_hook(  # pragma: no branch
    Direction, lambda inst: inst.to_legacy()
)

# class OrientationMeta(type):
#     _mapping = {
#         "NORTH": 0.0,
#         "NORTHEAST": 0.125,
#         "EAST": 0.25,
#         "SOUTHEAST": 0.375,
#         "SOUTH": 0.5,
#         "SOUTHWEST": 0.625,
#         "WEST": 0.75,
#         "NORTHWEST": 0.875,
#     }

#     def __getattr__(cls, name):
#         if name in cls._mapping:
#             return Orientation(cls._mapping[name])
#         else:
#             super().__getattr__(name)

#     # NORTH = Orientation(0.0)


@total_ordering
class Orientation(float):
    """
    Factorio orientation enum. Represents the direction an object is facing with
    a floating point number in the range [0.0, 1.0) where north is 0.0 and
    increases clockwise. Provides a number of convenience constants and
    functions over working with a raw float value.

    .. NOTE::

        Currently only supports addition and subtraction. If you want to perform
        more complex operations, it's best to convert it to a float and then
        convert it back to an Orientation when complete.

    * ``NORTH     (0.000)`` (Default)
    * ``NORTHEAST (0.125)``
    * ``EAST      (0.250)``
    * ``SOUTHEAST (0.375)``
    * ``SOUTH     (0.500)``
    * ``SOUTHWEST (0.625)``
    * ``WEST      (0.750)``
    * ``NORTHWEST (0.875)``
    """

    # Note: These are overwritten with Orientation() instances after definition
    NORTH: "Orientation" = 0.0
    NORTHEAST: "Orientation" = 0.125
    EAST: "Orientation" = 0.25
    SOUTHEAST: "Orientation" = 0.375
    SOUTH: "Orientation" = 0.5
    SOUTHWEST: "Orientation" = 0.625
    WEST: "Orientation" = 0.75
    NORTHWEST: "Orientation" = 0.875

    def __init__(self, value: float):
        self._value_ = value % 1.0
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

    def opposite(self) -> "Orientation":
        """
        Returns the direction opposite this one. For cardinal four-way and eight-
        way directions calling this function should always return the "true"
        opposite; but when calling on an arbitrary orientation the opposite may
        succumb to floating point error:

        .. doctest:: [constants]

            >>> Orientation.NORTH.opposite()
            <Orientation.SOUTH: 0.5>
            >>> Orientation.NORTHWEST.opposite()
            <Orientation.SOUTHEAST: 0.375>
            >>> Orientation(0.9).opposite()
            <Orientation: 0.3999999999999999>

        :returns: A new :py:class:`Orientation` object.
        """
        return Orientation((self._value_ + 0.5) % 1.0)

    def to_direction(self, sixteen_way: bool = False) -> Direction:
        """
        Converts the orientation to a :py:class:`Direction` instance. If the
        orientation is imprecise, the orientation will be rounded to either the
        closest four-way or eight-way direction.

        .. doctest:: [constants]

            >>> example = Orientation(1.0 / 3.0)
            >>> example.to_direction(sixteen_way=False)
            <Direction.EAST: 2>
            >>> example.to_direction(sixteen_way=True)
            <Direction.SOUTHEAST: 3>

        :param sixteen_way: Whether to round to the closest four-way direction or
            sixteen-way direction.

        :returns: A new :py:class:`Direction` object.
        """
        if sixteen_way:
            return Direction(round(self._value_ * 16))
        else:
            return Direction(round(self._value_ * 4) * 4)

    def to_vector(self, magnitude=1) -> Vector:
        """
        Converts a :py:class:`Orientation` into an equivalent 2-dimensional
        vector, for various linear operations. Returned vectors are unit-length,
        unless ``magnitude`` is altered.

        .. doctest:: [constants]

            >>> Orientation.NORTH.to_vector(magnitude=2)
            <Vector>(0, -2)
            >>> Orientation.SOUTHWEST.to_vector()
            <Vector>(-0.7071067811865476, 0.7071067811865476)

        :param magnitude: The magnitude (total length) of the vector to create.

        :returns: A new :py:class:`Vector` object pointing in the corresponding
            direction.
        """
        angle = self._value_ * math.pi * 2
        return Vector(math.sin(angle), -math.cos(angle)) * magnitude

    # =========================================================================

    def __add__(self, other) -> "Orientation":
        if isinstance(other, Orientation):
            return Orientation(self._value_ + other._value_)
        elif isinstance(other, float):
            return Orientation(self._value_ + other)
        else:
            return NotImplemented

    def __radd__(self, other) -> "Orientation":
        if isinstance(other, float):
            return Orientation(other + self._value_)
        else:
            return NotImplemented

    def __sub__(self, other) -> "Orientation":
        if isinstance(other, Orientation):
            return Orientation(self._value_ - other._value_)
        elif isinstance(other, float):
            return Orientation(self._value_ - other)
        else:
            return NotImplemented

    def __rsub__(self, other) -> "Orientation":
        if isinstance(other, float):
            return Orientation(other - self._value_)
        else:
            return NotImplemented

    def __eq__(self, other) -> bool:
        if isinstance(other, Orientation):
            return self._value_ == other._value_
        elif isinstance(other, float):
            return self._value_ == other
        else:
            return NotImplemented

    def __lt__(self, other) -> bool:
        if isinstance(other, Orientation):
            return self._value_ < other._value_
        elif isinstance(other, float):
            return self._value_ < other
        else:
            return NotImplemented

    def __hash__(self) -> int:
        return id(self) >> 4  # Default

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


class BeltReadMode(IntEnum):
    """
    Determines what manner belts should send their contents signal.

    * ``PULSE (0)``
        Pulse the signal for one tick when first detected. (Default)
    * ``HOLD (1)``
        Hold the signal for as long as the item is present.
    * ``HOLD_ALL_BELTS (2)``
        Hold the signal for all items on all contiguous connected belt segments.
    """

    PULSE = 0
    HOLD = 1
    HOLD_ALL_BELTS = 2


class InserterReadMode(IntEnum):
    """
    Determines what manner inserters should send their contents signal.

    * ``PULSE (0)``
        Pulse the signal for one tick when first detected. (Default)
    * ``HOLD (1)``
        Hold the signal for as long as the item is present.
    """

    PULSE = 0
    HOLD = 1


class MiningDrillReadMode(IntEnum):
    """
    Used to specify whether the mining drill will read just the resources
    accessible to it or the entire resource patch.

    * ``UNDER_DRILL (0)``
        Only return the resources directly minable by this drill. (Default)
    * ``TOTAL_PATCH (1)``
        Return the entire contents of the ore patches the drill is over.
    """

    UNDER_DRILL = 0
    TOTAL_PATCH = 1


class SiloReadMode(IntEnum):
    """
    Determines how rocket silos should interact with the circuit network.

    * ``NONE (0)``
        Do nothing.
    * ``READ_CONTENTS (1)``
        Send the contents of the currently loaded rocket. (Default)
    * ``READ_ORBITAL_REQUESTS (2)``
        Send the set of items desired by any space platforms in orbit.
    """

    NONE = 0
    READ_CONTENTS = 1
    READ_ORBITAL_REQUESTS = 2


class InserterModeOfOperation(IntEnum):
    """
    Inserter circuit control constants. Determines how the Entity should behave
    when connected to a circuit network.

    * ``ENABLE_DISABLE (0)``
        Turns the inserter on or off depending on the circuit condition.
        (Default)
    * ``SET_FILTERS (1)``
        Sets the inserter's filter signals based on read signals.
    * ``READ_HAND_CONTENTS (2)``
        Reads the contents of the inserter's hand and sends it to the connected
        wire(s).
    * ``NONE (3)``
        Does nothing.
    * ``SET_STACK_SIZE (4)``
        Sets the stack size override to the value of an input signal.
    """

    ENABLE_DISABLE = 0
    SET_FILTERS = 1
    READ_HAND_CONTENTS = 2
    NONE = 3
    SET_STACK_SIZE = 4


class LampColorMode(IntEnum):
    """
    In what manner should circuit signals sent to a Lamp be interpreted when
    determining that Lamp's color.

    * ``COLOR_MAPPING (0)``
        The given signal type broadcasts that particular color, so giving
        ``signal-red`` will display the color red. If multiple color signals are
        provided, the first one according to sort order is displayed.
        (Default)
    * ``COMPONENTS (1)``
        Three signals are used, where the value of each one corresponds to the
        8-bit red, green, and blue values of the final color.
    * ``PACKED_RGB (2)``
        One signal is used, where each color component is pulled from a specific
        8 bits of the input signal.
        wire(s).
    """

    COLOR_MAPPING = 0
    COMPONENTS = 1
    PACKED_RGB = 2


class LogisticModeOfOperation(IntEnum):
    """
    Logistics container circuit control constants. Determines how the Entity
    should behave when connected to a circuit network.

    * ``SEND_CONTENTS (0)``
        Reads the inventory of the container and sends it to the connected
        circuit network. (Default)
    * ``SET_REQUESTS (1)``
        Sets the item requests based on the input signals to the container.
    * ``NONE (2)``
        Does nothing with a connected circuit network.
    """

    SEND_CONTENTS = 0
    SET_REQUESTS = 1
    NONE = 2


class FilterMode(IntEnum):
    """
    Filter mode constant.

    * ``WHITELIST (0)``
        Include only the listed items. (Default)
    * ``BLACKLIST (1)``
        Exclude only the listed items.
    """

    WHITELIST = 0
    BLACKLIST = 1


class TileSelectionMode(IntEnum):
    """
    Tile selection mode for :py:class:`.UpgradePlanner`.

    * ``NORMAL (0)``
        Constructed tiles are only removed if there are no entities in the
        selected area. (Default)
    * ``ALWAYS (1)``
        Constructed tiles are always scheduled for deconstruction, regardless of
        selection contents.
    * ``NEVER (2)``
        Constructed tiles are never scheduled for deconstruction, regardless of
        selection contents.
    * ``ONLY (3)``
        Only tiles are selected for deconstruction; entities are completely
        ignored when using this mode.
    """

    NORMAL = 0
    ALWAYS = 1
    NEVER = 2
    ONLY = 3


class Ticks(int, Enum):
    """
    Constant values that correspond to the number of Factorio ticks for that
    measure of time at normal game-speed.

    * ``SECOND``: 60
    * ``MINUTE``: 60 * ``SECOND``
    * ``HOUR``  : 60 * ``MINUTE``
    * ``DAY``   : 24 * ``HOUR``
    """

    SECOND = 60
    MINUTE = 60 * SECOND
    HOUR = 60 * MINUTE
    DAY = 24 * HOUR

    @classmethod
    def from_timedelta(cls, td: timedelta) -> int:
        """
        Converts a :py:class:`.timedelta` into the closest number of Factorio
        ticks that measures that duration.

        :example:

        .. doctest::

            >>> from datetime import datetime
            >>> t1 = datetime.strptime("10:15:04", "%H:%M:%S")
            >>> t2 = datetime.strptime("10:19:27", "%H:%M:%S")
            >>> td = t2 - t1
            >>> Ticks.from_timedelta(td)
            15780

        :param timedelta: The difference in time between two points.
        :returns: The equivalent number of ticks representing this difference,
            rounded to the nearest tick.
        """
        return (
            td.days * Ticks.DAY
            + td.seconds * Ticks.SECOND
            + round(td.microseconds * 60 / 1_000_000)
        )


class WaitConditionType(str, Enum):
    """
    All valid string identifiers for the type of a train's
    :py:class:`WaitCondition` object.

    * ``TIME_PASSED``
        Triggered when a certain number of ticks has passed.
    * ``INACTIVITY``
        Triggered when the state of the train currently at the station is
        unaltered for a number of ticks.
    * ``FULL_CARGO``
        Triggered when there is no more room for any new cargo in any of the
        stopped train's wagons.
    * ``EMPTY_CARGO``
        Triggered when there is no more cargo in any of the stopped train's
        wagons.
    * ``ITEM_COUNT``
        Triggered when the count of some loaded item passes some specified
        condition.
    * ``FLUID_COUNT``
        Triggered when the count of some loaded fluid passes some specified
        condition.
    * ``CIRCUIT_CONDITION``
        Triggered when a circuit signal passed to the train stop passes some
        specified condition.
    * ``PASSENGER_PRESENT``
        Triggered if a player is inside any of the stopped train's wagons.
    * ``PASSENGER_NOT_PRESENT``
        Triggered if a player is not inside any of the stopped train's wagons.
    """

    ALL_REQUESTS_STATISFIED = "all_requests_satisfied"
    ANY_PLANET_IMPORT_ZERO = "any_planet_import_zero"
    ANY_REQUEST_NOT_SATISFIED = "any_request_not_satisfied"
    ANY_REQUEST_ZERO = "any_request_zero"
    AT_STATION = "at_station"
    CIRCUIT_CONDITION = "circuit"
    DAMAGE_TAKEN = "damage_taken"
    DESTINATION_FULL_OR_NO_PATH = "destination_full_or_no_path"
    EMPTY_CARGO = "empty"
    FLUID_COUNT = "fluid_count"
    FUEL_COUNT_ALL = "fuel_item_count_all"
    FUEL_COUNT_ANY = "fuel_item_count_any"
    FULL_CARGO = "full"
    FULL_FUEL = "fuel_full"
    NOT_EMPTY = "not_empty"
    INACTIVITY = "inactivity"
    ITEM_COUNT = "item_count"
    NOT_AT_STATION = "not_at_station"
    PASSENGER_PRESENT = "passenger_present"
    PASSENGER_NOT_PRESENT = "passenger_not_present"
    REQUEST_SATISFIED = "request_satisfied"
    REQUEST_NOT_SATISFIED = "request_not_satisfied"
    SPECIFIC_DESTINATION_FULL = "specific_destination_full"
    SPECIFIC_DESTINATION_NOT_FULL = "specific_destination_not_full"
    TIME_PASSED = "time"


class WaitConditionCompareType(str, Enum):
    """
    All valid string identitfiers for the type of comparison between multiple
    :py:class:`WaitCondition` objects.

    * ``AND``
        Boolean AND this condition with the subsequent one.
    * ``OR``
        Boolean OR this conditions with the subsequent one.
    """

    AND = "and"
    OR = "or"


class WireColor(str, Enum):
    """
    The valid wire colors for circuit connection types in Factorio, either red
    or green.

    * ``RED``
        Red wire.
    * ``GREEN``
        Green wire.
    """

    RED = "red"
    GREEN = "green"


@total_ordering
class ValidationMode(Enum):
    """
    The manner in which to validate a given Draftsman object.

    * ``DISABLED``
        No validation will be performed at all. Shorthand conversions will still
        take place, meaning that all values will still attempt to be coerced to
        their internal form whenever possible.
    * ``MINIMUM``
        The minimum amount of validation needed in order to validate that the
        structure of the object conforms to what Factorio expects. Importing an
        object that has been validated with this mode is not guaranteed to
        succeed, as while the object might be structurally correct, the data
        inside of it might still be malformed.
    * ``STRICT``
        The default mode. Includes all of the errors from ``MINIMUM``,
        but attempts to point out and remedy issues with the objects values.
        Also includes conceptual faults that will not result in the intended
        effect, such as setting an assembling machine's recipe to something that
        it cannot produce.
    * ``PEDANTIC``
        The most verbose option. Includes all of the previous errors and
        warnings, in addition to more linting-like behavior.
    """

    DISABLED = "disabled"
    MINIMUM = "minimum"
    STRICT = "strict"
    PEDANTIC = "pedantic"

    def __bool__(self) -> bool:
        return self is not ValidationMode.DISABLED

    def __eq__(self, other):
        if isinstance(other, ValidationMode):
            return self._member_names_.index(self.name) == self._member_names_.index(
                other.name
            )
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, ValidationMode):
            return self._member_names_.index(self.name) > self._member_names_.index(
                other.name
            )
        return NotImplemented


class Inventory(IntEnum):
    """
    Constants which define which internal inventories
    :py:attr:`Entity.item_requests` should reside in.
    """

    artillery_turret_ammo = 1
    artillery_wagon_ammo = 1
    assembling_machine_dump = 7
    assembling_machine_input = 2
    assembling_machine_modules = 4
    assembling_machine_output = 3
    beacon_modules = 1
    burnt_result = 6
    car_ammo = 3
    car_trunk = 2
    cargo_landing_pad_main = 1
    cargo_landing_pad_trash = 2
    cargo_unit = 1
    cargo_wagon = 1
    character_ammo = 4
    character_armor = 5
    character_corpse = 1
    character_guns = 3
    character_main = 1
    character_trash = 8
    character_vehicle = 7
    chest = 1
    editor_ammo = 4
    editor_armor = 5
    editor_guns = 3
    editor_main = 1
    fuel = 1
    furnace_modules = 4
    furnace_result = 3
    furnace_source = 2
    god_main = 2
    hub_main = 1
    hub_trash = 2
    item_main = 1
    lab_input = 2
    lab_modules = 3
    logistic_container_trash = 2
    mining_drill_modules = 2
    roboport_material = 2
    roboport_robot = 1
    robot_cargo = 1
    robot_repair = 2
    rocket_silo_input = 2
    rocket_silo_modules = 4
    rocket_silo_output = 3
    rocket_silo_rocket = 9
    rocket_silo_trash = 11
    spider_ammo = 3
    spider_trash = 4
    spider_trunk = 2
    turret_ammo = 1
