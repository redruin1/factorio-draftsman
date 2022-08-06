# tile.py
# -*- encoding: utf-8 -*-


from __future__ import unicode_literals

from draftsman.classes.collisionset import CollisionSet
from draftsman.classes.spatiallike import SpatialLike
from draftsman.classes.vector import Vector
from draftsman.error import InvalidTileError, DraftsmanError
from draftsman.utils import AABB

import draftsman.data.tiles as tiles

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.blueprint import Blueprint


class Tile(SpatialLike):
    """
    Tile class. Used for keeping track of tiles in Blueprints.
    """

    def __init__(self, name, position=(0, 0)):
        # type: (str, int, int) -> None
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
        self.name = name

        # Tile positions are in grid coordinates
        self.position = position

        # Tile AABB for SpatialHashMap
        # self._collision_box = [[0, 0], [1, 1]]
        self._collision_set = CollisionSet([AABB(0, 0, 1, 1)])

        # Tile mask for SpatialHashMap
        self._collision_mask = set(tiles.raw[self.name]["collision_mask"])

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

        Must be one of the entries in :py:data:`draftsman.data.tiles.raw` in
        order for the tile to be recognized as valid.

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
        if value in tiles.raw:
            self._name = value
        else:
            raise InvalidTileError("'{}'".format(value))

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

        # if isinstance(value, Vector):
        #     self._position = Vector(int(value.x), int(value.y))
        # else:
        #     try:
        #         self._position = Vector(int(value["x"]), int(value["y"]))
        #     except TypeError:
        #         self._position = Vector(int(value[0]), int(value[1]))

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
        return self._collision_set

    # =========================================================================

    @property
    def collision_mask(self):
        return self._collision_mask

    # =========================================================================

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
        does nothing, and is simply added for compatibility with entity merging.

        :param other: The other tile to inherit data from, if such a thing were
            to happen.
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
