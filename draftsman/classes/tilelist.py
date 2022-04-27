# tilelist.py
# -*- encoding: utf-8 -*-

from draftsman.classes.tile import Tile
from draftsman.error import UnreasonablySizedBlueprintError
from draftsman import utils

try:  # pragma: no coverage
    from collections.abc import MutableSequence
except ImportError:  # pragma: no coverage
    from collections import MutableSequence
from copy import deepcopy
from typing import TYPE_CHECKING
import six
import warnings

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import TileCollection


class TileList(MutableSequence):
    def __init__(self, parent, initlist=None):
        # type: (TileCollection, list[Tile]) -> None
        self.data = []
        self._parent = parent
        if initlist is not None:
            for elem in initlist:
                self.append(elem)

    def append(self, tile, **kwargs):
        # type: (Tile, **dict) -> None
        """
        Appends the Tile to the end of the sequence.
        """
        self.insert(len(self.data), tile, **kwargs)

    def insert(self, idx, tile, **kwargs):
        # type: (int, Tile, **dict) -> None
        """
        Inserts an element into the TileList.
        """
        if isinstance(tile, six.string_types):
            tile_copy = Tile(six.text_type(tile), **kwargs)
        else:
            tile_copy = deepcopy(tile)

        # Check tile
        self.check_tile(tile_copy)

        # Manage TileList
        self.data.insert(idx, tile_copy)

        # Keep a reference of the parent blueprint in the tile
        tile_copy._parent = self._parent

        # Add to hashmap
        self._parent.tile_hashmap.add(tile_copy)

        # Update dimensions
        self._parent._area = utils.extend_aabb(self._parent._area, tile_copy.get_area())
        (
            self._parent._tile_width,
            self._parent._tile_height,
        ) = utils.aabb_to_dimensions(self._parent.area)

        # Check the blueprint for unreasonable size
        if self._parent.tile_width > 10000 or self._parent.tile_height > 10000:
            raise UnreasonablySizedBlueprintError(
                "Current blueprint dimensions ({}, {}) exceeds the maximum size"
                " (10,000 x 10,000)".format(
                    self._parent.tile_width, self._parent.tile_height
                )
            )

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, value):
        # type: (int, Tile) -> None

        # Remove from hashmap
        self._parent.tile_hashmap.remove(self.data[idx])

        # Check tile
        self.check_tile(value)

        # Add to hashmap
        self._parent.tile_hashmap.add(value)

        # Add a reference to the container in the object
        value._parent = self._parent

        # Manage the TileList
        self.data[idx] = value

        self._parent.recalculate_area()

    def __delitem__(self, idx):
        del self.data[idx]

    def __len__(self):
        return len(self.data)

    def check_tile(self, tile):
        # type: (Tile) -> None
        if not isinstance(tile, Tile):
            raise TypeError("Entry in TileList must be a Tile")
