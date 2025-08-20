# tilelist.py

from draftsman.classes.spatial_hashmap import SpatialDataStructure
from draftsman.classes.exportable import Exportable, ValidationResult
from draftsman.constants import ValidationMode
from draftsman.tile import Tile, new_tile
from draftsman.error import DataFormatError
from draftsman.serialization import draftsman_converters
from draftsman.utils import (
    PrimitiveAABB,
    PrimitiveVector,
    AABB,
    aabb_overlaps_circle,
)
from draftsman.validators import get_mode
from draftsman.warning import OverlappingObjectsWarning

import attrs
from collections.abc import MutableSequence
from copy import deepcopy
from math import floor
from typing import (
    Callable,
    Iterator,
    Optional,
    Union,
    TYPE_CHECKING,
)
import warnings

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.collection import Collection


class TileHashMap(SpatialDataStructure):
    # Operates under the assumptions that:
    #   * Tiles can only ever be 1 tile square in area
    #   * Only 1 tile instance can occupy a particular coordinate at a time
    def __init__(self):
        self.map: dict[tuple[int, int], Tile] = {}

    def add(self, item: Tile, merge: bool = False) -> Tile:
        pos = self._map_coords(item.global_position)
        if merge and pos in self.map:
            if item.mergable_with(self.map[pos]):
                self.map[pos].merge(item)
                return None

        self.map[pos] = item

        return item

    def remove(self, item: Tile):
        try:
            del self.map[self._map_coords(item.global_position)]
        except KeyError:
            pass

    def clear(self) -> None:
        self.map.clear()

    def validate_insert(self, item: Tile, merge: bool):
        pos = self._map_coords(item.global_position)
        if pos in self.map:
            existing_tile = self.map[pos]
            if not merge or not existing_tile.mergable_with(item):
                # If the two objects have no shared collision layers they can
                # never intersect
                item_layers = item.collision_mask
                other_layers = existing_tile.collision_mask
                if (
                    len(other_layers.intersection(item_layers)) == 0
                ):  # pragma: no coverage
                    return

                warnings.warn(
                    "Added tile '{}' intersects '{}' at {}".format(
                        item.name,
                        existing_tile.name,
                        existing_tile.global_position,
                    ),
                    OverlappingObjectsWarning,
                    stacklevel=2,
                )

    def get_all(self) -> list[Tile]:
        return [tile for tile in self.map.values()]

    def get_on_point(self, point: PrimitiveVector, limit=None):
        try:
            return [self.map[self._map_coords(point)]]
        except KeyError:
            return []

    def get_in_radius(
        self, radius: float, point: PrimitiveVector, limit: Optional[int] = None
    ):
        cell_coords = self._cell_coords_from_radius(radius, point)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                if limit is not None and len(items) >= limit:
                    break
                items.append(self.map[cell_coord])

        return items

    def get_in_aabb(self, aabb: PrimitiveAABB, limit: Optional[int] = None):
        cell_coords = self._cell_coords_from_aabb(aabb)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                if limit is not None and len(items) >= limit:
                    break
                items.append(self.map[cell_coord])

        return items

    def _map_coords(self, point):
        return (floor(point[0]), floor(point[1]))

    def _cell_coords_from_aabb(self, aabb: AABB) -> list[tuple[int, int]]:
        if aabb is None:
            return []

        # Add a small error to under-round if aabb lands on cell boundary
        eps = 0.001
        grid_min = self._map_coords(aabb.top_left)
        grid_max = self._map_coords([aabb.bot_right[0] - eps, aabb.bot_right[1] - eps])

        grid_width = grid_max[0] - grid_min[0] + 1
        grid_height = grid_max[1] - grid_min[1] + 1

        cells = []
        for j in range(grid_min[1], grid_min[1] + grid_height):
            for i in range(grid_min[0], grid_min[0] + grid_width):
                cells.append((i, j))

        return cells

    def _cell_coords_from_radius(
        self, radius: float, point: PrimitiveVector
    ) -> list[tuple[int, int]]:
        grid_min = self._map_coords((point[0] - radius, point[1] - radius))
        grid_max = self._map_coords((point[0] + radius, point[1] + radius))

        grid_width = grid_max[0] - grid_min[0] + 1
        grid_height = grid_max[1] - grid_min[1] + 1

        cells = []
        for j in range(grid_min[1], grid_min[1] + grid_height):
            for i in range(grid_min[0], grid_min[0] + grid_width):
                cell_aabb = AABB(
                    i,
                    j,
                    (i + 1),
                    (j + 1),
                )
                if aabb_overlaps_circle(cell_aabb, radius, point):
                    cells.append((i, j))

        return cells


@attrs.define
class TileList(Exportable, MutableSequence):
    """
    A list which exclusively contains Factorio tiles.
    """

    # FIXME: I would like to annotate this, but cattrs cannot find the location of `Collection`
    _parent = attrs.field(
        default=None,
        init=False,
        repr=False,
        eq=False,
        # metadata={"deepcopy_func": lambda value, memo: None},
    )

    data: list[Tile] = attrs.field(
        factory=list,
        init=False,
    )

    # spatial_map: SpatialDataStructure = attrs.field(
    #     factory=SpatialHashMap,
    #     init=False,
    #     repr=False
    # )

    def __init__(  # TODO: rely on attrs generated one
        self,
        parent: "Collection",
        initlist: Optional[list[Tile]] = None,
    ) -> None:
        # Init Exportable
        super().__init__()

        self.data = []

        self.spatial_map: SpatialDataStructure = TileHashMap()

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
    ) -> Tile:
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
            :py:class:`.OverlappingObjectWarning` s in these cases.
        :param kwargs: Any other keyword arguments that should be passed to the
            newly created tile instance, if creating from a string ``name``.

        :returns: The newly appended :py:class:`.Tile`.
        """
        return self.insert(idx=len(self), name=name, copy=copy, merge=merge, **kwargs)

    def insert(
        self,
        idx: int,
        name: Union[str, Tile],
        copy: bool = True,
        merge: bool = False,
        **kwargs,
    ) -> Tile:
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
            :py:class:`.OverlappingObjectWarning` s in these cases.
        :param kwargs: Any other keyword arguments that should be passed to the
            newly created tile instance, if creating from a string ``name``.

        :returns: The newly inserted :py:class:`.Tile`.
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

        if get_mode() and self._parent is not None:
            # tile.validate(mode=get_mode()).reissue_all()
            self.spatial_map.validate_insert(
                tile, merge=merge
            )  # TODO: remove this and integrate it into `add()`

        # Add to tile map
        tile = self.spatial_map.add(tile, merge=merge)

        if tile is None:  # Tile was merged
            return  # Don't add this tile to the list

        # Manage TileList
        self.data.insert(idx, tile)

        # Keep a reference of the parent blueprint in the tile
        tile._parent = self._parent

        return tile

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

    def intersection(self, other: "TileList") -> "TileList":
        """
        Calculate the set intersection between this list and another
        :py:class:`.TileList`.
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

    def difference(self, other: "TileList") -> "TileList":
        """
        Calculate the set difference between this list and another
        :py:class:`.TileList`.
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

    def __getitem__(self, idx: Union[int, slice]) -> Union[Tile, list[Tile]]:
        return self.data[idx]

    def __setitem__(self, idx: int, value: Tile) -> None:
        # TODO: handle slices

        # Check tile
        if get_mode():
            if not isinstance(value, Tile):
                raise TypeError("Entry in TileList must be a Tile")

        self.spatial_map.remove(self.data[idx])

        if get_mode():
            # value.validate(mode=self.validate_assignment).reissue_all()
            self.spatial_map.validate_insert(value, merge=False)

        self.spatial_map.add(value, merge=False)

        # Manage the TileList
        self.data[idx] = value

        # Add a reference to the container in the object
        value._parent = self._parent

    def __delitem__(self, idx: Union[int, slice]) -> None:
        if isinstance(idx, slice):
            # Get slice parameters
            start, stop, step = idx.indices(len(self))
            for i in range(start, stop, step):
                # Remove from parent
                self.spatial_map.remove(self.data[i])
        else:
            self.spatial_map.remove(self.data[idx])

        # Remove from self
        del self.data[idx]

    def __len__(self) -> int:
        return len(self.data)

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
        return self.data == other.data

    def __repr__(self) -> str:  # pragma: no coverage
        return "TileList({})".format(self.data)

    def __deepcopy__(self, memo: dict) -> "TileList":
        # TODO: I think we want to delete this function
        parent = memo.get("new_parent", self._parent)
        new = TileList(parent)

        for tile in self.data:
            new.append(memo.get(id(tile), deepcopy(tile, memo)))

        # TODO: could maybe copy `spatial_map` verbatim

        return new


draftsman_converters.register_structure_hook(
    TileList,
    # This does work even though parent is None; this is on_setattr correctly
    # handles the cases where we pass a new entity list
    # It is inefficient since we construct 2 TileList objects, but...
    # TODO replace
    lambda d, _: TileList(None, d),
)
