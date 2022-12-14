# constants.py

"""
Enumerations of frequently used constants.
"""

from enum import IntEnum


class Direction(IntEnum):
    """
    Factorio direction enum. Encompasses all 8 cardinal directions and diagonals
    where north is 0 and increments clockwise.

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
