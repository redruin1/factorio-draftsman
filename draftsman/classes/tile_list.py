# tilelist.py

from draftsman.classes.spatial_hashmap import SpatialDataStructure, SpatialHashMap
from draftsman.classes.exportable import Exportable, ValidationResult
from draftsman.constants import ValidationMode
from draftsman.tile import Tile, new_tile
from draftsman.error import DataFormatError
from draftsman.serialization import draftsman_converters
from draftsman.validators import get_mode

import attrs
from collections.abc import MutableSequence
from copy import deepcopy
from typing import (
    Callable,
    Iterator,
    Optional,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import TileCollection


@attrs.define
class TileList(Exportable, MutableSequence):
    """
    A list which exclusively contains Factorio tiles.
    """

    # FIXME: I would like to annotate this, but cattrs cannot find the location of `EntityCollection`
    _parent = attrs.field(
        default=None,
        init=False,
        repr=False,
        eq=False,
        metadata={"deepcopy_func": lambda value, memo: None},
    )

    _root: list[Tile] = attrs.field(  # TODO: rename to data (perhaps use UserList?)
        factory=list,
        init=False,
    )

    def __init__(  # TODO: rely on attrs generated one
        self,
        parent: "TileCollection",
        initlist: Optional[list[Tile]] = None,
    ) -> None:
        # Init Exportable
        super().__init__()

        self._root = []

        self.spatial_map: SpatialDataStructure = SpatialHashMap()

        self._parent = parent

        if initlist is not None:
            for elem in initlist:
                if isinstance(elem, Tile):
                    self.append(elem)
                elif isinstance(elem, dict):
                    name = elem.pop("name")
                    self.append(name, **elem)
                else:
                    raise DataFormatError(
                        "TileList only takes either Tile or dict entries"
                    )

    def append(
        self, name: Union[str, Tile], copy: bool = True, merge: bool = False, **kwargs
    ) -> None:
        """
        Appends the Tile to the end of the sequence.

        :param name: The string name of the tile, or an already existing
            :py:class:`.Tile` instance.
        :param copy: Whether or not to create a deepcopy of the given tile
            instance and add that to the list. If ``name`` was a string instead,
            then this parameter does nothing since a new tile instance is always
            created.
        :param merge: Whether or not tiles with the same name and position
            should combine into one entity. If not, Draftsman will issue
            :py:class:`.OverlappingObjectWarning`s in these cases.
        :param kwargs: Any other keyword arguments that should be passed to the
            newly created tile instance, if creating from a string ``name``.
        """
        self.insert(idx=len(self), name=name, copy=copy, merge=merge, **kwargs)

    def insert(
        self,
        idx: int,
        name: Union[str, Tile],
        copy: bool = True,
        merge: bool = False,
        **kwargs
    ) -> None:
        """
        Inserts an element into the TileList.

        :param idx: The numeric index to insert this tile into the parent list.
        :param name: The string name of the tile, or an already existing
            :py:class:`.Tile` instance.
        :param copy: Whether or not to create a deepcopy of the given tile
            instance and add that to the list. If ``name`` was a string instead,
            then this parameter does nothing since a new tile instance is always
            created.
        :param merge: Whether or not tiles with the same name and position
            should combine into one entity. If not, Draftsman will issue
            :py:class:`.OverlappingObjectWarning`s in these cases.
        :param kwargs: Any other keyword arguments that should be passed to the
            newly created tile instance, if creating from a string ``name``.
        """
        # Convert to new Tile if constructed via string keyword
        new = False
        if isinstance(name, str):
            tile = new_tile(name, **kwargs)
            new = True
        else:
            tile = name

        if copy and not new:
            # Create a DEEPcopy of the entity if desired
            tile = deepcopy(tile)
            # Overwrite any user keywords if specified in the function signature
            for k, v in kwargs.items():
                setattr(tile, k, v)

        # If we attempt to merge an tile that isn't a copy, bad things will
        # probably happen
        # Not really sure what *should* happen in that case, so lets just nip
        # that in the bud for now
        if not copy and merge:
            raise ValueError(
                "Attempting to merge a non-copy, which is disallowed (for now at least)"
            )

        # Check tile
        if not isinstance(tile, Tile):
            raise TypeError("Entry in TileList must be a Tile")

        tile.validate(mode=get_mode()).reissue_all()
        self.spatial_map.validate_insert(
            tile, merge=merge
        )  # TODO: remove this and integrate it into `add()`

        # Add to tile map
        tile = self.spatial_map.add(tile, merge=merge)

        if tile is None:  # Tile was merged
            return  # Don't add this tile to the list

        # Manage TileList
        self._root.insert(idx, tile)

        # Keep a reference of the parent blueprint in the tile
        tile._parent = self._parent

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT
    ) -> ValidationResult:
        mode = ValidationMode(mode)
        output = ValidationResult([], [])

        if mode is ValidationMode.DISABLED:
            return output

        for tile in self:
            output += tile.validate(mode=mode)

        return output

    def union(self, other: "TileList") -> "TileList":
        """
        Calculate the set union between this list and another
        :py:class:`.TileList`.
        """
        new_tile_list = TileList(None)

        for tile in self._root:
            new_tile_list.append(tile)
            new_tile_list[-1]._parent = None

        for other_tile in other._root:
            already_in = False
            for tile in self._root:
                if tile == other_tile:
                    already_in = True
                    break
            if not already_in:
                new_tile_list.append(other_tile)

        return new_tile_list

    def intersection(self, other: "TileList") -> "TileList":
        """
        Calculate the set intersection between this list and another
        :py:class:`.TileList`.
        """
        new_tile_list = TileList(None)

        for tile in self._root:
            in_both = False
            for other_tile in other._root:
                if other_tile == tile:
                    in_both = True
                    break
            if in_both:
                new_tile_list.append(tile)

        return new_tile_list

    def difference(self, other: "TileList") -> "TileList":
        """
        Calculate the set difference between this list and another
        :py:class:`.TileList`.
        """
        new_tile_list = TileList(None)

        for tile in self._root:
            different = True
            for other_tile in other._root:
                if other_tile == tile:
                    different = False
                    break
            if different:
                new_tile_list.append(tile)

        return new_tile_list

    def __getitem__(self, idx: Union[int, slice]) -> Union[Tile, list[Tile]]:
        return self._root[idx]

    def __setitem__(self, idx: int, value: Tile) -> None:
        # TODO: handle slices

        # Check tile
        if get_mode():
            if not isinstance(value, Tile):
                raise TypeError("Entry in TileList must be a Tile")

        self.spatial_map.remove(self._root[idx])

        if get_mode():
            # value.validate(mode=self.validate_assignment).reissue_all()
            self.spatial_map.validate_insert(value, merge=False)

        self.spatial_map.add(value, merge=False)

        # Manage the TileList
        self._root[idx] = value

        # Add a reference to the container in the object
        value._parent = self._parent

    def __delitem__(self, idx: Union[int, slice]) -> None:
        if isinstance(idx, slice):
            # Get slice parameters
            start, stop, step = idx.indices(len(self))
            for i in range(start, stop, step):
                # Remove from parent
                self.spatial_map.remove(self._root[i])
        else:
            self.spatial_map.remove(self._root[idx])

        # Remove from self
        del self._root[idx]

    def __len__(self) -> int:
        return len(self._root)

    __iter__: Callable[..., Iterator[Tile]]

    def __or__(self, other: "TileList") -> "TileList":
        # TODO: NotImplemented when given arguments that are not TileList
        return self.union(other)

    # def __ior__(self, other: "TileList") -> None:
    #     self.union(other)

    def __and__(self, other: "TileList") -> "TileList":
        # TODO: NotImplemented
        return self.intersection(other)

    # def __iand__(self, other: "TileList") -> None:
    #     self.intersection(other)

    def __sub__(self, other: "TileList") -> "TileList":
        # TODO: NotImplemented
        return self.difference(other)

    # def __isub__(self, other: "TileList") -> None:
    #     self.difference(other)

    def __eq__(self, other: "TileList") -> bool:
        if not isinstance(other, TileList):
            return NotImplemented
        return self._root == other._root

    def __repr__(self) -> str:  # pragma: no coverage
        return "<TileList>{}".format(self._root)


draftsman_converters.register_structure_hook(
    TileList,
    # This does work even though parent is None; this is on_setattr correctly
    # handles the cases where we pass a new entity list
    # It is inefficient since we construct 2 TileList objects, but...
    lambda d, _: TileList(None, d),
)
