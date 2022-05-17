# spatialhashmap.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.classes.spatiallike import SpatialLike
from draftsman import signatures
from draftsman import utils
from draftsman.warning import OverlappingObjectsWarning

import math
from typing import Sequence
import warnings


class SpatialHashMap(object):
    """
    Implementation of a Spatial hash-map. Accellerates spatial queries of
    :py:class:`~draftsman.classes.collection.EntityCollection`. A quadtree might
    ultimately be more appropriate, but this is good enough for now.
    """

    def __init__(self, cell_size=8):
        # type: (int) -> None
        """
        Create a new SpatialHashMap.

        :param cell_size: Size of the grid in tiles to divide the space up into.
        """
        self.cell_size = cell_size
        self.map = {}

    def add(self, item):
        # type: (SpatialLike) -> None
        """
        Add a ``SpatialLike`` instance to the ``SpatialHashMap``.

        :param: The object to add.
        """
        # Get cells based off of collision_box
        cell_coords = self._cell_coords_from_aabb(item.get_area())

        # Check to see if any entries currently in the hashmap overlap with the new
        overlapping = self.get_in_area(item.get_area())
        for overlapping_item in overlapping:
            item_layers = item.collision_mask
            other_layers = overlapping_item.collision_mask
            if len(other_layers.intersection(item_layers)) > 0:
                warnings.warn(
                    "Added object '{}' ({}) at {} intersects '{}' ({}) at {}".format(
                        item.name,
                        type(item).__name__,
                        item.position,
                        overlapping_item.name,
                        type(overlapping_item).__name__,
                        overlapping_item.position,
                    ),
                    OverlappingObjectsWarning,
                    stacklevel=2,
                )

        for cell_coord in cell_coords:
            try:
                self.map[cell_coord].append(item)
            except KeyError:
                self.map[cell_coord] = [item]

    def recursively_add(self, item):
        # type: (SpatialLike) -> None
        """
        Add the leaf-most entities to the hashmap.

        This is used for Groups and other EntityCollections, where you need to
        add the Group's children to the hashmap instead of the Group itself.
        Works with as many nested Groups as desired.

        :param item: The object to add, or its children (if it has any).
        """
        if hasattr(item, "entities"):
            for sub_item in item.entities:
                self.recursively_add(sub_item)
        else:
            self.add(item)

    def remove(self, item):
        # type: (SpatialLike) -> None
        """
        Remove the ``SpatialLike`` instance from the ``SpatialHashMap``.

        :param item: The object to remove.
        """
        cell_coords = self._cell_coords_from_aabb(item.get_area())
        for cell_coord in cell_coords:
            try:
                cell = self.map[cell_coord]
                cell.remove(item)
                if not cell:
                    del self.map[cell_coord]
            except:
                pass

    def recursively_remove(self, item):
        # type: (SpatialLike) -> None
        """
        Inverse of :py:meth:`recursively_add`.

        :param item: The object to remove, or its children (if it has any).
        """
        if hasattr(item, "entities"):
            for sub_item in item.entities:
                self.recursively_remove(sub_item)
        else:
            self.remove(item)

    def clear(self):
        # type: () -> None
        """
        Deletes all entries in the map.
        """
        self.map.clear()

    def get_all(self):
        """
        Get all the entities in the hash map. Iterates over every cell and
        returns the contents sequentially. Useful if you want to get all the
        Entities in a Blueprint without including structural ones like Groups.

        :returns: A ``list`` of all entities inside the hash map.
        """
        items = []
        for cell_coord in self.map:
            for item in self.map[cell_coord]:
                items.append(item)

        return items

    def get_in_radius(self, radius, pos, limit=None):
        # type: (float, Sequence[float], int) -> list[SpatialLike]
        """
        Get all the entities whose ``collision_box`` overlaps a circle.

        :param radius: The radius of the circle.
        :param pos: The center of the circle; Can be specified as a sequence or
            as a ``dict`` with ``"x"`` and ``"y"`` keys.
        :param limit: A maximum amount of entities to return.

        :returns: A ``list`` of all entities that intersect the region. Can be
            empty.
        """
        # TODO: change this
        try:
            pos = [pos["x"], pos["y"]]
        except TypeError:
            pass

        cell_coords = self._cell_coords_from_radius(radius, pos)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                for item in self.map[cell_coord]:
                    item_pos = (item.position["x"], item.position["y"])
                    if utils.point_in_circle(item_pos, radius, pos):
                        if limit is not None and len(items) >= limit:
                            break
                        # Make sure we dont add the same item multiple times if
                        # it is spread across multiple cells
                        try:
                            items.index(item)
                        except ValueError:
                            items.append(item)

        return items

    def get_on_point(self, pos, limit=None):
        # type: (Sequence[float], int) -> list[SpatialLike]
        """
        Get all the entities whose ``collision_box`` overlaps a point.

        :param pos: The position to examine; Can be specified as a sequence or
            as a ``dict`` with ``"x"`` and ``"y"`` keys.
        :param limit: A maximum amount of entities to return.

        :returns: A ``list`` of all entities that intersect the point. Can be
            empty.
        """
        # TODO: change this
        try:
            pos = [pos["x"], pos["y"]]
        except TypeError:
            pass

        cell_coord = self.map_coords(pos[0], pos[1])
        items = []
        if cell_coord in self.map:
            for item in self.map[cell_coord]:
                if utils.point_in_aabb(pos, item.get_area()):
                    if limit is not None and len(items) >= limit:
                        break
                    items.append(item)

        return items

    def get_in_area(self, area, limit=None):
        # type (list[list[float]], int) -> list[SpatialLike]
        """
        Get all the entities whose ``collision_box`` overlaps a point.

        :param pos: The position to examine; Can be specified as a sequence or
            as a ``dict`` with ``"x"`` and ``"y"`` keys.
        :param limit: A maximum amount of entities to return.

        :returns: A ``list`` of all entities that intersect the point. Can be
            empty.
        """
        cell_coords = self._cell_coords_from_aabb(area)
        items = []
        for cell_coord in cell_coords:
            if cell_coord in self.map:
                for item in self.map[cell_coord]:
                    if utils.aabb_overlaps_aabb(item.get_area(), area):
                        if limit is not None and len(items) >= limit:
                            break
                        # Make sure we dont add the same item multiple times if
                        # it is spread across multiple cells
                        try:
                            items.index(item)
                        except ValueError:
                            items.append(item)

        return items

    def map_coords(self, x, y):
        # type: (float, float) -> tuple[int, int]
        """
        Get the internal map-coordinates from the world-space coordinates.

        :returns: A tuple of ``(map_x, map_y)``
        """
        return (
            int(math.floor(x / self.cell_size)),
            int(math.floor(y / self.cell_size)),
        )

    def _cell_coords_from_aabb(self, aabb):
        # type: (list[list[float]]) -> list[tuple[int, int]]
        """
        Get a list of map-coordinates that correspond to a world-space AABB.

        :param aabb: AABB

        :returns: ``list`` of tuples, each one a map-coordinate.
        """
        # Add a small error to under-round if aabb lands on cell boundary
        eps = 0.001
        grid_min = self.map_coords(aabb[0][0], aabb[0][1])
        grid_max = self.map_coords(aabb[1][0] - eps, aabb[1][1] - eps)

        grid_width = grid_max[0] - grid_min[0] + 1
        grid_height = grid_max[1] - grid_min[1] + 1

        cells = []
        for j in range(grid_min[1], grid_min[1] + grid_height):
            for i in range(grid_min[0], grid_min[0] + grid_width):
                cells.append((i, j))

        return cells

    def _cell_coords_from_radius(self, radius, pos):
        # type: (float, Sequence[float]) -> list[tuple[int, int]]
        """
        Get a list of map-coordinates that correspond to a world-space circle.

        :param radius: The radius of the circle.
        :param pos: The position to examine; Can be specified as a sequence or
            as a ``dict`` with ``"x"`` and ``"y"`` keys.

        :returns: A ``list`` of tuples, each one a map-coordinate.
        """
        # TODO: change this
        try:
            pos = [pos["x"], pos["y"]]
        except TypeError:
            pass

        grid_min = self.map_coords(pos[0] - radius, pos[1] - radius)
        grid_max = self.map_coords(pos[0] + radius, pos[1] + radius)

        grid_width = grid_max[0] - grid_min[0] + 1
        grid_height = grid_max[1] - grid_min[1] + 1

        cells = []
        for j in range(grid_min[1], grid_min[1] + grid_height):
            for i in range(grid_min[0], grid_min[0] + grid_width):
                cell_aabb = [
                    [i * self.cell_size, j * self.cell_size],
                    [(i + 1) * self.cell_size, (j + 1) * self.cell_size],
                ]
                if utils.aabb_overlaps_circle(cell_aabb, radius, pos):
                    cells.append((i, j))

        return cells
