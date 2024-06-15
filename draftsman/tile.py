# tile.py

"""
Alias module. Imports :py:class:`.Tile` under the namespace ``draftsman``.
"""

from draftsman.classes.tile import Tile
from draftsman.data import tiles
from draftsman.error import InvalidTileError

from typing import Literal


def new_tile(
    name: str, if_unknown: Literal["error", "ignore", "accept"] = "error", **kwargs
):
    """
    Factory function for creating a new :py:class:`.Tile`.

    Currently, it's not required to construct a generic tile using this function,
    since there is only one kind of ``Tile`` class. However, this function has
    the same behavior as :py:func:`new_entity`, in that you can specify the
    keyword ``if_unknown`` to raise an error if the tile is not a recognized
    entity.

    :param name: The string name of a Tile.
    :param if_unknown: How to behave if the name of the entity is unrecognized 
        by Draftsman. See TODO for more information.
    :param kwargs: A dict of all the keyword arguments to pass to the
        constructor.

    :returns: A new :py:class:`.Tile` instance, or ``None`` if none could be
        found and ``if_unknown`` was ``"ignore"``.

    :exception InvalidTileError: If the name passed in is not recognized as any
        valid tile name, and ``if_unknown`` was ``"error"``.
    :exception ValueError: If ``unknown`` is set to a string that is not
        ``"error"``, ``"ignore"``, nor ``"pass"``.
    """
    if name in tiles.raw or if_unknown == "accept":
        # Construct tile as normal
        return Tile(name=name, **kwargs)

    # At this point, the name is unrecognized by the current environment:
    if if_unknown == "error":
        # Raise an issue where this entity is not known; useful in cases where
        # the user wants to make sure that Draftsman knows about every entity in
        # a modded blueprint, for example.
        raise InvalidTileError("Unknown tile '{}'".format(name))
    elif if_unknown == "ignore":
        # Simply return nothing; if importing from a blueprint string, any
        # unrecognized entity will simply be omitted from the Draftsman
        # blueprint; matches the game's behavior.
        return None
    else:
        raise ValueError(
            "Unknown parameter value '{}' for `if_unknown`; must be one of 'error', 'ignore', or 'accept'",
            if_unknown,
        )
