# tile.py
# -*- encoding: utf-8 -*-

"""
.. code-block:: python

    {
        "name": str, # Name of the tile
        "position": {"x": int, "y": int} # Position of the tile
    }
"""

from __future__ import unicode_literals

from draftsman.classes.collision_set import CollisionSet
from draftsman.classes.spatial_like import SpatialLike
from draftsman.classes.vector import Vector
from draftsman.error import InvalidTileError, DraftsmanError
from draftsman.utils import AABB

import draftsman.data.tiles as tiles

from typing import TYPE_CHECKING, Union, Tuple

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.blueprint import Blueprint

_TILE_COLLISION_SET = CollisionSet([AABB(0, 0, 1, 1)])


class Tile(SpatialLike):
    """
    Tile class. Used for keeping track of tiles in Blueprints.
    """

    def __init__(self, name, position=(0, 0)):
        # type: (str, Tuple[int, int]) -> None
        """
        Create a new Tile with ``name`` at ``position``. ``position`` defaults
        to ``(0, 0)``.

        :param name: Name of the Tile to create.
        :param position: Position of the tile, in grid-coordinates.

        :exception InvalidTileError: If the name is not a valid Factorio tile id.
        :exception IndexError: If the position does not match the correct
            specification.
        """
        # Reference to parent blueprint
        self._parent = None

        # Tile name
        self.name = name  # TODO: optional error checking

        # Tile positions are in grid coordinates
        self.position = position

        # Tile AABB for SpatialHashMap
        # self._collision_set = _TILE_COLLISION_SET

        # Tile mask for SpatialHashMap
        # TODO: extract this to generic data to save memory like entity
        # try:
        #     self._collision_mask = set(tiles.raw[self.name]["collision_mask"])
        #     self._collision_mask = tiles.collision_masks[self.name]
        # except KeyError:
        #     # Maybe add a new entry?
        #     # tiles.raw[self.name] = {"name": self.name, "collision_mask": set()}
        #     self._collision_mask = set()
        # if self.name not in tiles.raw:
        #     tiles.add_tile(self.name)

    # =========================================================================

    @property
    def parent(self):
        # type: () -> Blueprint
        return self._parent

    # =========================================================================

    @property
    def name(self):
        # type: () -> str
        """
        The name of the Tile.

        Must be a string representing the name of a valid Factorio tile. If the
        name is not recognized in :py:data:`.draftsman.data.tiles.raw`, then
        ``Tile().validate()`` will return errors.

        :getter: Gets the name of the Tile.
        :setter: Sest the name of the Tile.
        :type: ``str``

        :exception InvalidTileError: If the set name is not a valid Factorio
            tile id.
        """
        return self._name

    @name.setter
    def name(self, value):
        # type: (str) -> None
        # TODO: validate that name is string using deal
        self._name = value

    # =========================================================================

    @property
    def position(self):
        # type: () -> dict
        """
        The position of the tile, in tile-grid coordinates.

        ``position`` can be specified as a ``dict`` with ``"x"`` and
        ``"y"`` keys, or more succinctly as a sequence of floats, usually a
        ``list`` or ``tuple``.

        This property is updated in tandem with ``position``, so using them both
        interchangeably is both allowed and encouraged.

        :getter: Gets the position of the Entity.
        :setter: Sets the position of the Entity.
        :type: ``dict{"x": int, "y": int}``

        :exception IndexError: If the set value does not match the above
            specification.
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[dict, list, tuple]) -> None

        if self.parent:
            raise DraftsmanError("Cannot move tile while it's inside a TileCollection")

        self._position = Vector.from_other(value, int)

    # =========================================================================

    @property
    def global_position(self):
        # This is redundant in this case because tiles cannot be placed inside
        # of Groups (yet)
        # However, it's still necessary.
        return self.position

    # =========================================================================

    @property
    def collision_set(self):
        # type: () -> CollisionSet
        return _TILE_COLLISION_SET

    # =========================================================================

    @property
    def collision_mask(self):
        # type: () -> set
        try:
            return tiles.raw[self.name]["collision_mask"]
        except KeyError:
            return set()

    # =========================================================================

    def inspect(self):
        # type: () -> list[Exception]
        """
        Checks the tile to see if Draftsman thinks that it can be loaded in game,
        and returns a list of all potential issues that Draftsman cannot fix on
        it's own. Also performs any data normalization steps, if needed.
        Returns an empty list if there are no issues.

        :raises InvalidTileError: If :py:attr:`name` is not recognized by
            Draftsman to be a valid tile name.

        :example:

        .. code-block:: python

            tile = Tile("unknown-name")
            for issue in tile.valdiate():
                if type(issue) is InvalidTileError:
                    tile = Tile("concrete")  # swap the tile to a known one
                else:  # some other error
                    raise issue
        """
        issues = []

        if self.name not in tiles.raw:
            issues.append(InvalidTileError("'{}'".format(self.name)))

        return issues

    def mergable_with(self, other):
        # type: (Tile) -> bool
        """
        Determines if two entities are mergeable, or that they can be combined
        into a single tile. Two tiles are considered mergable if they have the
        same ``name`` and exist at the same ``position``

        :param other: The other ``Tile`` to check against.

        :returns: ``True`` if the tiles are mergable, ``False`` otherwise.
        """
        return (
            isinstance(other, Tile)
            and self.name == other.name
            and self.position == other.position
        )

    def merge(self, other):
        # type: (Tile) -> None
        """
        Merges this tile with another one. Due to the simplicity of tiles, this
        does nothing as long as the merged tiles are of the same name. Allows
        you to overlap areas of concrete and landfill without issuing
        :py:class:`.OverlappingObjectsWarning`s.

        :param other: The other tile underneath this one.
        """
        pass

    def to_dict(self):
        # type: () -> dict
        """
        Converts the Tile to its JSON-dict representation.

        :returns: The exported JSON-dict representation of the Tile.
        """
        return {"name": self.name, "position": self.position.to_dict()}

    def __repr__(self):  # pragma: no coverage
        # type: () -> str
        return "<Tile>{}".format(self.to_dict())
