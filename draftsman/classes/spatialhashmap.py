# spatialhashmap.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman import signatures
from draftsman import utils

import math


class SpatialHashMap(object):
    """
    TODO
    """

    def __init__(self, cell_size=8):
        # type: (int) -> None
        """ """
        self.cell_size = cell_size
        self.map = {}

    def add(self, item):
        """ """
        # get cells based off of collision_box
        cell_coords = self._cell_coords_from_aabb(item.get_area())
        for cell_coord in cell_coords:
            try:
                self.map[cell_coord].append(item)
            except KeyError:
                self.map[cell_coord] = [item]

    def remove(self, item):
        """ """
        cell_coords = self._cell_coords_from_aabb(item.get_area())
        for cell_coord in cell_coords:
            try:
                cell = self.map[cell_coord]
                cell.remove(item)
                if not cell:
                    del self.map[cell_coord]
            except:
                pass

    def get_in_radius(self, radius, pos, limit=None):
        """ """
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
        """ """
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
        """ """
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
        """ """
        return (
            int(math.floor(x / self.cell_size)),
            int(math.floor(y / self.cell_size)),
        )

    def _cell_coords_from_aabb(self, aabb):
        """ """
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
        """ """
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
