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
            entity_type="container",
            collision_box=[[-0.4, -0.4], [0.4, 0.4]],
        )
        assert entities.raw["new-entity-1"] == {
            "name": "new-entity-1",
            "type": "container",
            "collision_box": [[-0.4, -0.4], [0.4, 0.4]],
            "collision_mask": {
                "player-layer",
                "item-layer",
                "water-tile",
                "object-layer",
            },
            "flags": set(),
        }
        assert "new-entity-1" in entities.containers
        # test
        Container("new-entity-1")

        # Hidden with custom collision mask
        entities.add_entity(
            name="new-entity-2",
            entity_type="storage-tank",
            collision_box=[[-0.4, -0.4], [0.4, 0.4]],
            collision_mask={"player-layer"},
            hidden=True,
        )
        assert entities.raw["new-entity-2"] == {
            "name": "new-entity-2",
            "type": "storage-tank",
            "collision_box": [[-0.4, -0.4], [0.4, 0.4]],
            "collision_mask": {"player-layer"},
            "flags": {"hidden"},
        }
        assert "new-entity-2" in entities.storage_tanks
        # test
        StorageTank("new-entity-2")

        # Incorrect type
        with pytest.raises(ValueError):
            entities.add_entity("new-entity-3", "incorrect", [[0, 0], [1, 1]])

        del entities.raw["new-entity-1"]
        del entities.containers[-1]
        del entities.raw["new-entity-2"]
        del entities.storage_tanks[-1]


class TestModulesData:
    def test_add_modules(self):
        pass  # TODO


class TestSignalsData:
    def test_add_signal(self):
        # Signals of each valid type
        signals.add_signal("new-signal-1", "item")
        assert signals.raw["new-signal-1"] == {"name": "new-signal-1", "type": "item"}
        assert signals.type_of["new-signal-1"] == "item"
        assert "new-signal-1" in signals.item
        signals.add_signal("new-signal-2", "fluid")
        assert signals.raw["new-signal-2"] == {"name": "new-signal-2", "type": "fluid"}
        assert signals.type_of["new-signal-2"] == "fluid"
        assert "new-signal-2" in signals.fluid
        signals.add_signal("new-signal-3", "virtual")
        assert signals.raw["new-signal-3"] == {
            "name": "new-signal-3",
            "type": "virtual",
        }
        assert signals.type_of["new-signal-3"] == "virtual"
        assert "new-signal-3" in signals.virtual

        # Incorrect type
        with pytest.raises(ValueError):
            signals.add_signal("new-signal-4", "incorrect")


class TestTilesData:
    def test_add_tile(self):
        tiles.add_tile("new-tile")
        # Test
        Tile("new-tile")
