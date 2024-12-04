# tilelist.py

from draftsman.classes.spatial_hashmap import SpatialDataStructure, SpatialHashMap
from draftsman.classes.exportable import Exportable, ValidationResult
from draftsman.constants import ValidationMode
from draftsman.tile import Tile, new_tile
from draftsman.data import tiles
from draftsman.error import DataFormatError, InvalidTileError
from draftsman.signatures import DraftsmanBaseModel

from collections.abc import MutableSequence
from copy import deepcopy
from pydantic import ValidationError
from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Literal,
    Optional,
    Union,
    TYPE_CHECKING,
)

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import TileCollection


class TileList(Exportable, MutableSequence):
    """
    TODO
    """

    class Format(DraftsmanBaseModel):
        _root: List[Tile.Format]  # TODO: TileLike?

        root: List[Any]  # TODO: there should be a way to validate this

    def __init__(
        self,
        parent: "TileCollection",
        initlist: Optional[list[Tile]] = None,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
    ) -> None:
        """
        TODO
        """
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

        self.validate_assignment = validate_assignment

    def append(
        self, name: Union[str, Tile], copy: bool = True, merge: bool = False, **kwargs
    ) -> None:
        """
        Appends the Tile to the end of the sequence.

        TODO
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

        TODO
        """
        # Convert to new Tile if constructed via string keyword
        new = False
        if isinstance(name, str):
            tile = new_tile(name, **kwargs)
            if tile is None:
                return
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

        # Handle overlapping and merging
        if self.validate_assignment:
            tile.validate(mode=self.validate_assignment).reissue_all()
            self.spatial_map.validate_insert(tile, merge=merge)

        # Add to tile map
        tile = self.spatial_map.add(tile, merge=merge)

        if tile is None:  # Tile was merged
            return  # Don't add this tile to the list

        # Manage TileList
        self._root.insert(idx, tile)

        # Keep a reference of the parent blueprint in the tile
        tile._parent = self._parent

    def clear(self) -> None:
        del self._root[:]
        self.spatial_map.clear()

    def validate(
        self, mode: ValidationMode = ValidationMode.STRICT, force: bool = False
    ) -> ValidationResult:
        mode = ValidationMode(mode)

        output = ValidationResult([], [])

        if mode is ValidationMode.NONE and not force:  # (self.is_valid and not force):
            return output

        context: dict[str, Any] = {
            "mode": mode,
            "object": self,
            "warning_list": [],
            "assignment": False,
        }

        try:
            result = self.Format.model_validate(
                {"root": self._root},
                strict=False,  # TODO: ideally this should be strict
                context=context,
            )
            # Reassign private attributes
            # Acquire the newly converted data
            self._root = result["root"]
        except ValidationError as e:  # pragma: no coverage
            output.error_list.append(DataFormatError(e))

        output.warning_list += context["warning_list"]

        return output

    def union(self, other: "TileList") -> "TileList":
        """
        TODO
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
        TODO
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
        TODO
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
        if not isinstance(value, Tile):
            raise TypeError("Entry in TileList must be a Tile")

        self.spatial_map.remove(self._root[idx])

        if self.validate_assignment:
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
        # TODO: not implmented
        if not isinstance(other, TileList):
            return False
        # if len(self.data) != len(other.data):
        #     return False
        # for i in range(len(self.data)):
        #     if self.data[i] != other.data[i]:
        #         return False
        # return True
        return self._root == other._root

    def __repr__(self) -> str:  # pragma: no coverage
        return "<TileList>{}".format(self._root)

    # @classmethod
    # def __get_pydantic_core_schema__(
    #     cls, _source_type: Any, handler: GetCoreSchemaHandler
    # ) -> CoreSchema:
    #     return core_schema.no_info_after_validator_function(
    #         cls, handler(list[Tile])
    #     )  # TODO: correct annotation
