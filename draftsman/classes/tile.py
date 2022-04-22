# tile.py
# -*- encoding: utf-8 -*-

"""
Tile module. Contains the ``Tile`` class.
"""

from __future__ import unicode_literals

from draftsman.classes.spatiallike import SpatialLike
from draftsman.error import InvalidTileError, DraftsmanError

import draftsman.data.tiles as tiles

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.blueprint import Blueprint


class Tile(SpatialLike):
    """ """

    def __init__(self, name, position=[0, 0]):
        # type: (str, int, int) -> None
        """ """
        # Reference to parent blueprint
        self._parent = None

        # Tile name
        if name not in tiles.raw:
            raise InvalidTileError("'{}'".format(str(name)))
        self.name = name

        # Tile positions are in grid coordinates
        self.position = position

        # Tile aabb for SpatialHashMap
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
        The name of the Entity.

        Must be one of the entries in ``draftsman.data.tiles.raw`` in order for
        the tile to be recognized as valid.

        :exception InvalidTileError: If the set name is not a valid Factorio
            tile id.

        :type: ``str``
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
        The position of the tile, in tile grid coordinates.
        """
        return self._position

    @position.setter
    def position(self, value):
        # type: (Union[dict, list, tuple]) -> None

        if self.parent:
            raise DraftsmanError("Cannot move tile while it's inside a Blueprint")

        try:
            self._position = {"x": int(value["x"]), "y": int(value["y"])}
        except TypeError:
            self._position = {"x": int(value[0]), "y": int(value[1])}

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
