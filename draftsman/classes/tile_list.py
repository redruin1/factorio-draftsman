# tilelist.py

from draftsman.classes.tile import Tile
from draftsman.error import DataFormatError

try:  # pragma: no coverage
    from collections.abc import MutableSequence
except ImportError:  # pragma: no coverage
    from collections import MutableSequence
from copy import deepcopy
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Any, TYPE_CHECKING
import six

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import TileCollection


class TileList(MutableSequence):
    """
    TODO
    """
    
    def __init__(self, parent, initlist=None, unknown="error"):
        # type: (TileCollection, list[Tile], str) -> None
        """
        TODO
        """

        self.data = []
        self._parent = parent
        if initlist is not None:
            for elem in initlist:
                print(elem)
                if isinstance(elem, Tile):
                    self.append(elem, unknown=unknown)
                elif isinstance(elem, dict):
                    name = elem.pop("name")
                    self.append(name, **elem, unknown=unknown)
                else:
                    raise DataFormatError("TileList only takes either Tile or dict entries")

    def append(self, tile, copy=True, merge=False, unknown="error", **kwargs):
        # type: (Tile, bool, bool, str, **dict) -> None
        """
        Appends the Tile to the end of the sequence.
        """
        self.insert(len(self.data), tile, copy, merge, unknown=unknown, **kwargs)

    def insert(self, idx, tile, copy=True, merge=False, unknown="error", **kwargs):
        # type: (int, Tile, bool, bool, str, **dict) -> None
        """
        Inserts an element into the TileList.
        """
        if isinstance(tile, six.string_types):
            tile = Tile(six.text_type(tile), **kwargs)
        elif copy:
            tile = deepcopy(tile)

        # Check tile
        self.check_tile(tile)

        if self._parent:
            tile = self._parent.on_tile_insert(tile, merge)

        if tile is None:  # Tile was merged
            return  # Don't add this tile to the list

        # Manage TileList
        self.data.insert(idx, tile)

        # Keep a reference of the parent blueprint in the tile
        tile._parent = self._parent

    def check_tile(self, tile):
        # type: (Tile) -> None
        if not isinstance(tile, Tile):
            raise TypeError("Entry in TileList must be a Tile")

    def union(self, other):
        # type: (TileList) -> TileList
        """
        TODO
        """
        new_tile_list = TileList(None)

        for tile in self.data:
            new_tile_list.append(tile)
            new_tile_list[-1]._parent = None

        for other_tile in other.data:
            already_in = False
            for tile in self.data:
                if tile == other_tile:
                    already_in = True
                    break
            if not already_in:
                new_tile_list.append(other_tile)

        return new_tile_list

    def intersection(self, other):
        # type: (TileList) -> TileList
        """
        TODO
        """
        new_tile_list = TileList(None)

        for tile in self.data:
            in_both = False
            for other_tile in other.data:
                if other_tile == tile:
                    in_both = True
                    break
            if in_both:
                new_tile_list.append(tile)

        return new_tile_list

    def difference(self, other):
        # type: (TileList) -> TileList
        """
        TODO
        """
        new_tile_list = TileList(None)

        for tile in self.data:
            different = True
            for other_tile in other.data:
                if other_tile == tile:
                    different = False
                    break
            if different:
                new_tile_list.append(tile)

        return new_tile_list

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
        # type: () -> int
        return len(self.data)

    def __or__(self, other):
        # type: (TileList) -> TileList
        return self.union(other)

    # def __ior__(self, other):
    #     # type: (TileList) -> None
    #     self.union(other)

    def __and__(self, other):
        # type: (TileList) -> TileList
        return self.intersection(other)

    # def __iand__(self, other):
    #     # type: (TileList) -> None
    #     self.intersection(other)

    def __sub__(self, other):
        # type: (TileList) -> TileList
        return self.difference(other)

    # def __isub__(self, other):
    #     # type: (TileList) -> None
    #     self.difference(other)

    def __eq__(self, other):
        # type: (TileList) -> bool
        if not isinstance(other, TileList):
            return False
        if len(self.data) != len(other.data):
            return False
        for i in range(len(self.data)):
            if self.data[i] != other.data[i]:
                return False
        return True
    
    def __repr__(self) -> str:
        return "<TileList>{}".format(self.data)

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(list[Tile])) # TODO: correct annotation
