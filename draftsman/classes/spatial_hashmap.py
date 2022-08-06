# spatial_hashmap.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.collection import EntityCollection
from draftsman.classes.spatiallike import SpatialLike
from draftsman.classes.spatial_data_structure import SpatialDataStructure
from draftsman.prototypes.straight_rail import StraightRail
from draftsman.prototypes.curved_rail import CurvedRail
from draftsman import utils
from draftsman.warning import OverlappingObjectsWarning

import math
from typing import Sequence
import warnings


class SpatialHashMap(SpatialDataStructure):
    """
    Implementation of a :py:class:`.SpatialDataStructure` using a hash-map.
    Accellerates spatial queries of :py:class:`~.EntityCollection`.
    """

    def __init__(self, cell_size=8):
        # type: (int) -> None
        """
        Create a new :py:class:`.SpatialHashMap`.

        :param cell_size: Size of the grid in tiles to divide the space up into.
        """
        self.cell_size = cell_size
        self.map = {}

    def add(self, item):
        # type: (SpatialLike, bool) -> None
        item_region = item.get_world_bounding_box()

        # Get cells based off of collision_box
        cell_coords = self._cell_coords_from_aabb(item_region)
        for cell_coord in cell_coords:
            try:
                self.map[cell_coord].append(item)
            except KeyError:
                self.map[cell_coord] = [item]

    def recursive_add(self, item):
        # type: (SpatialLike, bool) -> None
        if hasattr(item, "entities"):
            for sub_item in item.entities:
                self.recursive_add(sub_item)
        else:
            self.add(item)

    def remove(self, item):
        # type: (SpatialLike) -> None
        cell_coords = self._cell_coords_from_aabb(item.get_world_bounding_box())
        for cell_coord in cell_coords:
            try:
                cell = self.map[cell_coord]
                cell.remove(item)
                if not cell:
                    del self.map[cell_coord]
            except:
                pass

    def recursive_remove(self, item):
        # type: (SpatialLike) -> None
        if hasattr(item, "entities"):
            for sub_item in item.entities:
                self.recursive_remove(sub_item)
        else:
            self.remove(item)

    def clear(self):
        # type: () -> None
        self.map.clear()

    def handle_overlapping(self, item, merge):
        # type: (SpatialLike, bool) -> None
        """
        Handles overlapping items if ``item`` were to be added to this hashmap.
        Issues overlapping objects warnings and merges entities if desired.

        .. Warning::

            This function may not be permanent, or it may move somewhere else in
            future versions.
        """
        if isinstance(item, EntityCollection):
            # Recurse through all subentities
            merged_entities = []  # keep track of merged entities, if any
            for i, sub_entity in enumerate(item.entities):
                result = self.handle_overlapping(sub_entity, merge)
                if result is None:
                    merged_entities.append(sub_entity)

            # Remove all merged entities from the list
            for entity in merged_entities:
                item.entities.remove(entity)

            # Note: `item` here might be a Group with NO entities in it; this is
            # deliberate
            return item
        else:
            item_region = item.get_world_bounding_box()
            overlapping_items = self.get_in_area(item_region)
            for overlapping_item in overlapping_items:
                # If we can merge the two items and this is desired, do so first
                if merge and overlapping_item.mergable_with(item):
                    overlapping_item.merge(item)
                    return None

                # Otherwise, we now check to issue and OverlappingObjectsWarning
                # Only the broadphase has taken place up until this point, so we
                # now do the proper collision check
                item_collision_set = item.get_world_collision_set()
                overlapping_collision_set = overlapping_item.get_world_collision_set()
                if not item_collision_set.overlaps(overlapping_collision_set):
                    continue

                # If we get here, we know that geometrically at least they are
                # overlapping, but we also need to check to see if they have the
                # same collision layers
                item_layers = item.collision_mask
                other_layers = overlapping_item.collision_mask

                # StraightRails and CurvedRails cannot collide with each other
                # UNLESS they are the same type, face the same direction, and
                # exist at the exact same place
                if isinstance(item, (StraightRail, CurvedRail)) and isinstance(
                    overlapping_item, (StraightRail, CurvedRail)
                ):
                    identical = (
                        item.name == overlapping_item.name
                        and item.direction == overlapping_item.direction
                        and item.global_position == overlapping_item.global_position
                    )
                    if not identical:
                        continue

                if len(other_layers.intersection(item_layers)) > 0:
                    warnings.warn(
                        "Added object '{}' ({}) at {} intersects '{}' ({}) at {}".format(
                            item.name,
                            type(item).__name__,
                            item.global_position,
                            overlapping_item.name,
                            type(overlapping_item).__name__,
                            overlapping_item.global_position,
                        ),
                        OverlappingObjectsWarning,
                        stacklevel=2,
                    )

            return item

    def get_all_entities(self):
        # type: () -> list[SpatialLike]
        items = []
        for cell_coord in self.map:
            for item in self.map[cell_coord]:
                items.append(item)

        return items

    def get_in_radius(self, radius, point, limit=None):
        # type: (float, Sequence[float], int) -> list[SpatialLike]
        cell_coords = self._cell_coords_from_radius(radius, point)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                for item in self.map[cell_coord]:
                    item_pos = (item.global_position.x, item.global_position.y)
                    if utils.point_in_circle(item_pos, radius, point):
                        if limit is not None and len(items) >= limit:
                            break
                        # Make sure we dont add the same item multiple times if
                        # it is spread across multiple cells
                        try:
                            items.index(item)
                        except ValueError:
                            items.append(item)

        return items

    def get_on_point(self, point, limit=None):
        # type: (utils.Point, int) -> list[SpatialLike]
        cell_coord = self._map_coords(point)
        items = []
        if cell_coord in self.map:
            for item in self.map[cell_coord]:
                if utils.point_in_aabb(point, item.get_world_bounding_box()):
                    if limit is not None and len(items) >= limit:
                        break
                    items.append(item)

        return items

    def get_in_area(self, area, limit=None):
        # type: (utils.AABB, int) -> list[SpatialLike]
        cell_coords = self._cell_coords_from_aabb(area)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                for item in self.map[cell_coord]:
                    if utils.aabb_overlaps_aabb(item.get_world_bounding_box(), area):
                        if limit is not None and len(items) >= limit:
                            break
                        # Make sure we dont add the same item multiple times if
                        # it is spread across multiple cells
                        try:
                            items.index(item)
                        except ValueError:
                            items.append(item)

        return items

    def _map_coords(self, point):
        # type: (list[float]) -> tuple[int, int]
        """
        Get the internal map-coordinates from the world-space coordinates.

        :returns: A tuple of ``(map_x, map_y)``
        """
        return (
            int(math.floor(point[0] / self.cell_size)),
            int(math.floor(point[1] / self.cell_size)),
        )

    def _cell_coords_from_aabb(self, aabb):
        # type: (utils.AABB) -> list[tuple[int, int]]
        """
        Get a list of map-coordinates that correspond to a world-space AABB.

        :param aabb: AABB to search, or ``None``.

        :returns: ``list`` of tuples, each one a map-coordinate.
        """
        # TODO: AABB or PrimitveAABB?
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

    def _cell_coords_from_radius(self, radius, point):
        # type: (float, utils.Point) -> list[tuple[int, int]]
        """
        Get a list of map-coordinates that correspond to a world-space circle.

        :param radius: The radius of the circle.
        :param pos: The position to examine; Can be specified as a sequence or
            as a ``dict`` with ``"x"`` and ``"y"`` keys.

        :returns: A ``list`` of tuples, each one a map-coordinate.
        """
        grid_min = self._map_coords((point[0] - radius, point[1] - radius))
        grid_max = self._map_coords((point[0] + radius, point[1] + radius))

        grid_width = grid_max[0] - grid_min[0] + 1
        grid_height = grid_max[1] - grid_min[1] + 1

        cells = []
        for j in range(grid_min[1], grid_min[1] + grid_height):
            for i in range(grid_min[0], grid_min[0] + grid_width):
                cell_aabb = utils.AABB(
                    i * self.cell_size,
                    j * self.cell_size,
                    (i + 1) * self.cell_size,
                    (j + 1) * self.cell_size,
                )
                if utils.aabb_overlaps_circle(cell_aabb, radius, point):
                    cells.append((i, j))

        return cells
