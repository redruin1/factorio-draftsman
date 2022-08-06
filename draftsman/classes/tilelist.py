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

    def append(self, tile, copy=True, merge=False, **kwargs):
        # type: (Tile, bool, bool, **dict) -> None
        """
        Appends the Tile to the end of the sequence.
        """
        self.insert(len(self.data), tile, copy, merge, **kwargs)

    def insert(self, idx, tile, copy=True, merge=False, **kwargs):
        # type: (int, Tile, bool, bool, **dict) -> None
        """
        Inserts an element into the TileList.
        """
        if isinstance(tile, six.string_types):
            tile = Tile(six.text_type(tile), **kwargs)
        elif copy:
            tile = deepcopy(tile)

        # Check tile
        self.check_tile(tile)

        tile = self._parent.on_tile_insert(tile, merge)

        if tile is None:  # Tile was merged
            return  # Don't add this tile to the list

        # Manage TileList
        self.data.insert(idx, tile)

        # Keep a reference of the parent blueprint in the tile
        tile._parent = self._parent

        # TODO: this sucks, but it has to be like this
        self._parent.recalculate_area()

    def __getitem__(self, idx):
        return self.data[idx]

    def __setitem__(self, idx, value):
        # type: (int, Tile) -> None

        # Check tile
        self.check_tile(value)

        # Handle parent
        self._parent.on_tile_set(self.data[idx], value)

        # Manage the TileList
        self.data[idx] = value

        # Add a reference to the container in the object
        value._parent = self._parent

        # TODO: this sucks, but it has to be like this
        self._parent.recalculate_area()

    def __delitem__(self, idx):
        # type: (int) -> None
        if isinstance(idx, slice):
            # Get slice parameters
            start, stop, step = idx.indices(len(self))
            for i in range(start, stop, step):
                # Remove from parent
                self._parent.on_tile_remove(self.data[i])
        else:
            self._parent.on_tile_remove(self.data[idx])

        # Remove from self
        del self.data[idx]

        # TODO: this sucks, but it has to be like this
        self._parent.recalculate_area()

    def __len__(self):
        return len(self.data)

    def check_tile(self, tile):
        # type: (Tile) -> None
        if not isinstance(tile, Tile):
            raise TypeError("Entry in TileList must be a Tile")
