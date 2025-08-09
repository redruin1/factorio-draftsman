# test_data.py

from draftsman.entity import Container, StorageTank
from draftsman.tile import Tile
from draftsman.data import entities, modules, tiles, signals
from draftsman.utils import AABB

import pytest


class TestEntitiesData:
    def test_all_entities_have_flippable(self):
        for entity_name in entities.raw:
            try:
                entities.flippable[entity_name]
            except KeyError:  # pragma: no coverage
                # raise Exception("'{}' had no entry in entities.flippable".format(entity_name))
                pytest.fail(
                    "'{}' had no entry in entities.flippable".format(entity_name)
                )

    def test_add_entity(self):
        # Normal
        entities.add_entity(
            name="new-entity-1",
            type="container",
            collision_box=[[-0.4, -0.4], [0.4, 0.4]],
        )
        assert entities.raw["new-entity-1"] == {
            "name": "new-entity-1",
            "type": "container",
            "collision_box": [[-0.4, -0.4], [0.4, 0.4]],
            "flags": set(),
        }
        assert "new-entity-1" in entities.containers
        # test
        Container("new-entity-1")

        # Hidden with custom collision mask
        entities.add_entity(
            name="new-entity-2",
            type="storage-tank",
            collision_box=[[-0.4, -0.4], [0.4, 0.4]],
            collision_mask={"layers": {"player-layer"}},
            hidden=True,
        )
        assert entities.raw["new-entity-2"] == {
            "name": "new-entity-2",
            "type": "storage-tank",
            "collision_box": [[-0.4, -0.4], [0.4, 0.4]],
            "collision_mask": {"layers": {"player-layer"}},
            "flags": {"hidden"},
        }
        assert "new-entity-2" in entities.storage_tanks
        # test
        StorageTank("new-entity-2")

        # Incorrect type
        # with pytest.raises(ValueError):
        #     entities.add_entity("new-entity-3", "incorrect", [[0, 0], [1, 1]])

        del entities.raw["new-entity-1"]
        del entities.containers[-1]
        del entities.raw["new-entity-2"]
        del entities.storage_tanks[-1]


class TestModulesData:
    def test_add_modules(self):
        pass  # TODO


class TestTilesData:
    def test_add_tile(self):
        tiles.add_tile("new-tile")
        # Test
        Tile("new-tile")
