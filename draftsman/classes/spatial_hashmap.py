# spatial_hashmap.py

from draftsman.classes.spatial_like import SpatialLike
from draftsman.classes.spatial_data_structure import SpatialDataStructure
from draftsman.classes.vector import PrimitiveVector, PrimitiveIntVector
from draftsman.prototypes.straight_rail import StraightRail
from draftsman.prototypes.legacy_straight_rail import LegacyStraightRail
from draftsman.prototypes.legacy_curved_rail import LegacyCurvedRail
from draftsman.prototypes.gate import Gate
from draftsman.utils import (
    AABB,
    aabb_overlaps_aabb,
    aabb_overlaps_circle,
    point_in_aabb,
    point_in_circle,
)
from draftsman.warning import OverlappingObjectsWarning

import math
from typing import Optional
import warnings


class SpatialHashMap(SpatialDataStructure):
    """
    Implementation of a :py:class:`.SpatialDataStructure` using a hash-map.
    Accellerates spatial queries of :py:class:`~.Collection`.
    """

    def __init__(self, cell_size: int = 8) -> None:
        """
        Create a new :py:class:`.SpatialHashMap`.

        :param cell_size: Size of the grid in tiles to divide the space up into.
        """
        self.cell_size = cell_size
        self.map = {}

    def add(self, item: SpatialLike, merge: bool = False) -> Optional[SpatialLike]:
        item_region = item.get_world_bounding_box()

        # If we want to merge
        if merge:
            overlapping_items = self.get_in_aabb(item_region)
            for overlapping_item in overlapping_items:
                # If we can merge the two items and this is desired, do so first
                if overlapping_item.mergable_with(item):
                    overlapping_item.merge(item)
                    return None

        # Get cells based off of collision_box
        cell_coords = self._cell_coords_from_aabb(item_region)
        for cell_coord in cell_coords:
            try:
                self.map[cell_coord].append(item)
            except KeyError:
                self.map[cell_coord] = [item]

        return item

    def remove(self, item: SpatialLike) -> None:
        cell_coords = self._cell_coords_from_aabb(item.get_world_bounding_box())
        for cell_coord in cell_coords:
            try:
                cell = self.map[cell_coord]
                cell.remove(item)
                if not cell:
                    del self.map[cell_coord]
            except KeyError:
                pass

    def clear(self) -> None:
        self.map.clear()

    def validate_insert(self, item: SpatialLike, merge: bool) -> None:
        """
        Issues OverlappingObjectWarnings if adding this particular ``item``
        would be unplacable in the current blueprint/group configuration.
        """
        item_region = item.get_world_bounding_box()
        overlapping_items = self.get_in_aabb(item_region)
        for overlapping_item in overlapping_items:
            # If we can merge the two items and this is desired later on,
            # don't issue any overlapping warnings for this entity
            # (Note that the actual merge is performed later on in
            # `recursive_add()`)
            if merge and overlapping_item.mergable_with(item):
                return

            # If the two objects have no shared collision layers they can
            # never intersect
            item_layers = item.collision_mask
            other_layers = overlapping_item.collision_mask
            if len(other_layers.intersection(item_layers)) == 0:
                continue

            # StraightRails and CurvedRails cannot collide with each other
            # UNLESS they are the same type, face the same direction, and
            # exist at the exact same place
            if isinstance(
                item, (StraightRail, LegacyStraightRail, LegacyCurvedRail)) and isinstance(
                overlapping_item, (StraightRail, LegacyStraightRail, LegacyCurvedRail)
            ):
                identical = (
                    item.name == overlapping_item.name
                    and item.direction == overlapping_item.direction
                    and item.global_position == overlapping_item.global_position
                )
                if not identical:
                    continue

            # StraightRails and Gates collide with each other ONLY IF the
            # direction of the gate and rail are parallel
            if (
                isinstance(item, (StraightRail, LegacyStraightRail))
                and isinstance(overlapping_item, Gate)
                or isinstance(item, Gate)
                and isinstance(overlapping_item, (StraightRail, LegacyStraightRail))
            ):
                parallel = (item.direction - overlapping_item.direction) % 8 == 0
                if not parallel:
                    continue

            # Finally, the actual geometric collision check:
            item_collision_set = item.get_world_collision_set()
            overlapping_collision_set = overlapping_item.get_world_collision_set()
            if item_collision_set.overlaps(overlapping_collision_set):
                warnings.warn(
                    "Added object\n" 
                    "\t'{}' ({}) at {}{}\n"
                    "intersects\n"
                    "\t'{}' ({}) at {}{}".format(
                        item.name,
                        type(item).__name__,
                        item.global_position,
                        " facing {}".format(repr(item.direction)) if hasattr(item, "rotatable") and item.rotatable else "",
                        overlapping_item.name,
                        type(overlapping_item).__name__,
                        overlapping_item.global_position,
                        " facing {}".format(repr(overlapping_item.direction)) if hasattr(overlapping_item, "rotatable") and overlapping_item.rotatable else ""
                    ),
                    OverlappingObjectsWarning,
                    stacklevel=2,
                )

    def get_all_entities(self) -> list[SpatialLike]:
        items = []
        for cell_coord in self.map:
            for item in self.map[cell_coord]:
                items.append(item)

        return items

    def get_in_radius(
        self, radius: float, point: PrimitiveVector, limit: Optional[int] = None
    ) -> list[SpatialLike]:
        cell_coords = self._cell_coords_from_radius(radius, point)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                for item in self.map[cell_coord]:
                    item_pos = (item.global_position.x, item.global_position.y)
                    if point_in_circle(item_pos, radius, point):
                        if limit is not None and len(items) >= limit:
                            break
                        # Make sure we dont add the same item multiple times if
                        # it is spread across multiple cells
                        try:
                            items.index(item)
                        except ValueError:
                            items.append(item)

        return items

    def get_on_point(
        self, point: PrimitiveVector, limit: Optional[int] = None
    ) -> list[SpatialLike]:
        cell_coord = self._map_coords(point)
        items = []
        if cell_coord in self.map:
            for item in self.map[cell_coord]:
                if point_in_aabb(point, item.get_world_bounding_box()):
                    if limit is not None and len(items) >= limit:
                        break
                    items.append(item)

        return items

    def get_in_aabb(self, aabb: AABB, limit: Optional[int] = None) -> list[SpatialLike]:
        cell_coords = self._cell_coords_from_aabb(aabb)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                for item in self.map[cell_coord]:
                    if aabb_overlaps_aabb(item.get_world_bounding_box(), aabb):
                        if limit is not None and len(items) >= limit:
                            break
                        # Make sure we dont add the same item multiple times if
                        # it is spread across multiple cells
                        try:
                            items.index(item)
                        except ValueError:
                            items.append(item)

        return items

    def _map_coords(self, point: PrimitiveVector) -> PrimitiveIntVector:
        """
        Get the internal map-coordinates from the world-space coordinates.

        :returns: A tuple of ``(map_x, map_y)``
        """
        return (
            int(math.floor(point[0] / self.cell_size)),
            int(math.floor(point[1] / self.cell_size)),
        )

    def _cell_coords_from_aabb(self, aabb: AABB) -> list[PrimitiveIntVector]:
        """
        Get a list of map cell coordinates that correspond to a world-space AABB.

        :param aabb: AABB to search, or ``None``.

        :returns: ``list`` of tuples, each one a map-coordinate.
        """
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
    ) -> list[PrimitiveIntVector]:
        """
        Get a list of map cell coordinates that correspond to a world-space
        circle.

        :param radius: The radius of the circle.
        :param point: The position around which the radius is centered.

        :returns: A ``list`` of tuples, each one a map-coordinate.
        """
        grid_min = self._map_coords((point[0] - radius, point[1] - radius))
        grid_max = self._map_coords((point[0] + radius, point[1] + radius))

        grid_width = grid_max[0] - grid_min[0] + 1
        grid_height = grid_max[1] - grid_min[1] + 1

        cells = []
        for j in range(grid_min[1], grid_min[1] + grid_height):
            for i in range(grid_min[0], grid_min[0] + grid_width):
                cell_aabb = AABB(
                    i * self.cell_size,
                    j * self.cell_size,
                    (i + 1) * self.cell_size,
                    (j + 1) * self.cell_size,
                )
                if aabb_overlaps_circle(cell_aabb, radius, point):
                    cells.append((i, j))

        return cells
