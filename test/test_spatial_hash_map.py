# test_spatial_hash_map.py

from draftsman.classes.blueprint import Blueprint
from draftsman.classes.spatial_hashmap import SpatialHashMap
from draftsman.entity import Container
from draftsman.tile import Tile
from draftsman import utils
from draftsman.warning import OverlappingObjectsWarning

import pytest


class TestSpatialHashMap:
    def test_init(self):
        map = SpatialHashMap()
        assert map.map == {}
        assert map.cell_size == 4

        assert map._map_coords((10, 10)) == (2, 2)

    def test_add(self):
        map = SpatialHashMap()
        tile_to_add = Tile("refined-concrete", (0, 0))
        map.add(tile_to_add)
        assert map.map == {(0, 0): [tile_to_add]}
        other_tile_to_add = Tile("landfill", (1, 1))
        map.add(other_tile_to_add)
        assert map.map == {(0, 0): [tile_to_add, other_tile_to_add]}

    def test_clear(self):
        blueprint = Blueprint()
        for i in range(5):
            blueprint.tiles.append("landfill", position=(i, 0))
        assert len(blueprint.tiles) == 5
        assert len(blueprint.tiles.spatial_map.get_all()) == 5

        blueprint.tiles.spatial_map.clear()

        assert len(blueprint.tiles) == 5  # separate
        assert len(blueprint.tiles.spatial_map.get_all()) == 0

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
        blueprint = Blueprint()

        entity1 = Container("wooden-chest", tile_position=(0, 0))
        blueprint.entities.append(entity1, copy=False)
        entity2 = Container("iron-chest", tile_position=(1, 1))
        blueprint.entities.append(entity2, copy=False)

        assert blueprint.entities.spatial_map.get_all() == [entity1, entity2]

    def test_get_all_tiles(self):
        blueprint = Blueprint()

        tile_to_add = Tile("refined-concrete", (0, 0))
        blueprint.tiles.append(tile_to_add, copy=False)
        other_tile_to_add = Tile("landfill", (1, 1))
        blueprint.tiles.append(other_tile_to_add, copy=False)

        assert blueprint.tiles.spatial_map.get_all() == [tile_to_add, other_tile_to_add]

    def test_get_entities_in_radius(self):
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
        assert results == [tile_to_add, other_tile_to_add, another_tile_to_add]
        results = map.get_in_radius(100, (0, 0), limit=1)
        assert results == [tile_to_add]

    def test_get_tiles_in_radius(self):
        blueprint = Blueprint()
        tile_to_add = Tile("refined-concrete", (0, 0))
        blueprint.tiles.append(tile_to_add, copy=False)
        other_tile_to_add = Tile("landfill", (10, 0))
        blueprint.tiles.append(other_tile_to_add, copy=False)
        another_tile_to_add = Tile("refined-hazard-concrete-left", (7, 7))
        blueprint.tiles.append(another_tile_to_add, copy=False)
        results = blueprint.tiles.spatial_map.get_in_radius(5, (0, 0))
        assert results == [tile_to_add]
        results = blueprint.tiles.spatial_map.get_in_radius(100, (0, 0))
        assert results == [tile_to_add, other_tile_to_add, another_tile_to_add]
        results = blueprint.tiles.spatial_map.get_in_radius(100, (0, 0), limit=1)
        assert results == [tile_to_add]

    def test_get_entities_on_point(self):
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
        # Point in cell coord, but not overlapping entity
        results = map.get_on_point((1.5, 1.5))
        assert results == []

    def test_get_tiles_on_point(self):
        blueprint = Blueprint()

        tile_to_add = Tile("refined-concrete", (0, 0))
        blueprint.tiles.append(tile_to_add, copy=False)
        results = blueprint.tiles.spatial_map.get_on_point((0, 0))
        assert results == [tile_to_add]

        other_tile_to_add = Tile("landfill", (0, 0))
        with pytest.warns(OverlappingObjectsWarning):
            # Attempt to merge, but have it fail
            other_tile_to_add = blueprint.tiles.append(other_tile_to_add, merge=True)

        # Only returns 1 due to contstraints of TileHashMap
        results = blueprint.tiles.spatial_map.get_on_point((0, 0))
        assert results == [other_tile_to_add]
        results = blueprint.tiles.spatial_map.get_on_point((0, 0), limit=1)
        assert results == [other_tile_to_add]
        # Point not in map case
        results = blueprint.tiles.spatial_map.get_on_point((100, 100))
        assert results == []
        # Point in cell coord, but not overlapping entity
        results = blueprint.tiles.spatial_map.get_on_point((1.5, 1.5))
        assert results == []

    def test_get_entity_in_aabb(self):
        blueprint = Blueprint()
        entity1 = Container("wooden-chest", tile_position=(0, 0))
        blueprint.entities.append(entity1, copy=False)
        entity2 = Container("iron-chest", tile_position=(10, 0))
        blueprint.entities.append(entity2, copy=False)
        entity3 = Container("steel-chest", tile_position=(7, 7))
        blueprint.entities.append(entity3, copy=False)
        results = blueprint.entities.spatial_map.get_in_aabb(utils.AABB(0, 0, 4, 4))
        assert results == [entity1]
        results = blueprint.entities.spatial_map.get_in_aabb(utils.AABB(0, 0, 8, 8))
        assert results == [entity1, entity3]
        results = blueprint.entities.spatial_map.get_in_aabb(
            utils.AABB(-100, -100, 100, 100)
        )
        assert results == [entity1, entity2, entity3]
        results = blueprint.entities.spatial_map.get_in_aabb(
            utils.AABB(-100, -100, 100, 100), limit=1
        )
        assert results == [entity1]

    def test_get_tile_in_aabb(self):
        blueprint = Blueprint()
        tile_to_add = Tile("refined-concrete", (0, 0))
        blueprint.tiles.append(tile_to_add, copy=False)
        other_tile_to_add = Tile("landfill", (10, 0))
        blueprint.tiles.append(other_tile_to_add, copy=False)
        another_tile_to_add = Tile("refined-hazard-concrete-left", (7, 7))
        blueprint.tiles.append(another_tile_to_add, copy=False)
        results = blueprint.tiles.spatial_map.get_in_aabb(utils.AABB(0, 0, 4, 4))
        assert results == [tile_to_add]
        results = blueprint.tiles.spatial_map.get_in_aabb(utils.AABB(0, 0, 8, 8))
        assert results == [tile_to_add, another_tile_to_add]
        results = blueprint.tiles.spatial_map.get_in_aabb(
            utils.AABB(-100, -100, 100, 100)
        )
        assert results == [tile_to_add, other_tile_to_add, another_tile_to_add]
        results = blueprint.tiles.spatial_map.get_in_aabb(
            utils.AABB(-100, -100, 100, 100), limit=1
        )
        assert results == [tile_to_add]

        assert blueprint.tiles.spatial_map.get_in_aabb(None) == []
