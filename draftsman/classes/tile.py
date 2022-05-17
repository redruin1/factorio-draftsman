# tile.py
# -*- encoding: utf-8 -*-


from __future__ import unicode_literals

from draftsman.classes.spatiallike import SpatialLike
from draftsman.error import InvalidTileError, DraftsmanError

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
        self._collision_box = [[0, 0], [1, 1]]

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
            raise DraftsmanError(
                "Cannot move tile while it's inside an EntityCollection"
            )

        try:
            self._position = {"x": int(value["x"]), "y": int(value["y"])}
        except TypeError:
            self._position = {"x": int(value[0]), "y": int(value[1])}

    # =========================================================================

    @property
    def global_position(self):
        return self.position

    # =========================================================================

    @property
    def collision_box(self):
        return self._collision_box

    # =========================================================================

    @property
    def collision_mask(self):
        return self._collision_mask

    # =========================================================================

    def to_dict(self):
        # type: () -> dict
        """
        Converts the Tile to its JSON-dict representation.

        :returns: The exported JSON-dict representation of the Tile.
        """
        return {"name": self.name, "position": self.position}

    def __repr__(self):
        return (
            "<Tile>{'name': '" + self.name + "', 'position': "
            "{'x': "
            + str(self.position["x"])
            + ", 'y': "
            + str(self.position["y"])
            + "}}"
        )
