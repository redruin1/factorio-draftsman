# test_spatial_hash_map.py

from draftsman.classes.blueprint import SpatialHashMap
from draftsman.tile import Tile
from draftsman import utils

import pytest


class TestSpatialHashMap:
    def test_init(self):
        map = SpatialHashMap()
        assert map.map == {}
        assert map.cell_size == 8

        assert map._map_coords((10, 10)) == (1, 1)

    def test_add(self):
        map = SpatialHashMap()
        tile_to_add = Tile("refined-concrete", (0, 0))
        map.add(tile_to_add)
        assert map.map == {(0, 0): [tile_to_add]}
        other_tile_to_add = Tile("landfill", (1, 1))
        map.add(other_tile_to_add)
        assert map.map == {(0, 0): [tile_to_add, other_tile_to_add]}

    def test_remove(self):
        map = SpatialHashMap()
        tile_to_add = Tile("refined-concrete", (0, 0))
        map.add(tile_to_add)
        other_tile_to_add = Tile("landfill", (1, 1))
        map.add(other_tile_to_add)
        map.remove(other_tile_to_add)
        assert map.map == {(0, 0): [tile_to_add]}
        map.remove(tile_to_add)
        assert map.map == {}
        map.remove(Tile("landfill", (0, 0)))
        assert map.map == {}

    def test_get_all_entities(self):
        map = SpatialHashMap()
        tile_to_add = Tile("refined-concrete", (0, 0))
        map.add(tile_to_add)
        other_tile_to_add = Tile("landfill", (1, 1))
        map.add(other_tile_to_add)

        assert map.get_all_entities() == [tile_to_add, other_tile_to_add]

    def test_get_in_radius(self):
        map = SpatialHashMap()
        tile_to_add = Tile("refined-concrete", (0, 0))
        map.add(tile_to_add)
        other_tile_to_add = Tile("landfill", (10, 0))
        map.add(other_tile_to_add)
        another_tile_to_add = Tile("refined-hazard-concrete-left", (7, 7))
        map.add(another_tile_to_add)
        results = map.get_in_radius(5, (0, 0))
        assert results == [tile_to_add]
        results = map.get_in_radius(100, (0, 0))
        assert results == [tile_to_add, another_tile_to_add, other_tile_to_add]
        results = map.get_in_radius(100, (0, 0), limit=1)
        assert results == [tile_to_add]

    def test_get_on_point(self):
        map = SpatialHashMap()
        tile_to_add = Tile("refined-concrete", (0, 0))
        map.add(tile_to_add)
        results = map.get_on_point((0, 0))
        assert results == [tile_to_add]
        other_tile_to_add = Tile("landfill", (0, 0))
        # with self.assertWarns(OverlappingObjectsWarning):
        map.add(other_tile_to_add)
        results = map.get_on_point((0, 0))
        assert results == [tile_to_add, other_tile_to_add]
        results = map.get_on_point((0, 0), limit=1)
        assert results == [tile_to_add]
        # Point not in map case
        results = map.get_on_point((100, 100))
        assert results == []

    def test_get_in_aabb(self):
        map = SpatialHashMap()
        tile_to_add = Tile("refined-concrete", (0, 0))
        map.add(tile_to_add)
        other_tile_to_add = Tile("landfill", (10, 0))
        map.add(other_tile_to_add)
        another_tile_to_add = Tile("refined-hazard-concrete-left", (7, 7))
        map.add(another_tile_to_add)
        results = map.get_in_aabb(utils.AABB(0, 0, 4, 4))
        assert results == [tile_to_add]
        results = map.get_in_aabb(utils.AABB(0, 0, 8, 8))
        assert results == [tile_to_add, another_tile_to_add]
        results = map.get_in_aabb(utils.AABB(-100, -100, 100, 100))
        assert results == [tile_to_add, another_tile_to_add, other_tile_to_add]
        results = map.get_in_aabb(utils.AABB(-100, -100, 100, 100), limit=1)
        assert results == [tile_to_add]
