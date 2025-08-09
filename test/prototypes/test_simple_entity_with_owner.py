# test_simple_entity_with_owner.py

from draftsman.constants import Direction, LegacyDirection
from draftsman.entity import SimpleEntityWithOwner, simple_entities_with_owner
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

import pytest


@pytest.fixture
def valid_simple_entity_with_owner():
    return SimpleEntityWithOwner(
        "simple-entity-with-owner",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        variation=13,
        tags={"blah": "blah"},
    )


class TestSimpleEntityWithOwner:
    def test_constructor_init(self):
        entity = SimpleEntityWithOwner(variation=13)
        assert entity.name == simple_entities_with_owner[0]
        assert entity.variation == 13

        with pytest.warns(UnknownEntityWarning):
            SimpleEntityWithOwner("this is not correct").validate().reissue_all()

    def test_to_dict(self):
        entity = SimpleEntityWithOwner("simple-entity-with-owner")
        assert entity.variation == 1
        assert entity.to_dict() == {
            "name": "simple-entity-with-owner",
            "position": {"x": 0.5, "y": 0.5},
        }
        assert entity.to_dict(version=(1, 0), exclude_defaults=False) == {
            "name": "simple-entity-with-owner",
            "position": {"x": 0.5, "y": 0.5},
            "direction": LegacyDirection.NORTH,  # Default
            "items": {},  # Default
            "variation": 1,  # Default
            "tags": {},  # Default
        }
        assert entity.to_dict(version=(2, 0), exclude_defaults=False) == {
            "name": "simple-entity-with-owner",
            "quality": "normal",  # Default
            "position": {"x": 0.5, "y": 0.5},
            "direction": Direction.NORTH,  # Default
            "items": [],  # Default
            "mirror": False,  # Default,
            "variation": 1,  # Default
            "tags": {},  # Default
        }

        entity.variation = 10
        assert entity.variation == 10
        assert entity.to_dict() == {
            "name": "simple-entity-with-owner",
            "position": {"x": 0.5, "y": 0.5},
            "variation": 10,
        }

    def test_power_and_circuit_flags(self):
        for name in simple_entities_with_owner:
            entity = SimpleEntityWithOwner(name)
            assert entity.power_connectable == False
            assert entity.dual_power_connectable == False
            assert entity.circuit_connectable == False
            assert entity.dual_circuit_connectable == False

    def test_mergable_with(self):
        entity1 = SimpleEntityWithOwner("simple-entity-with-owner")
        entity2 = SimpleEntityWithOwner(
            "simple-entity-with-owner", tags={"some": "stuff"}
        )

        assert entity1.mergable_with(entity1)

        assert entity1.mergable_with(entity2)
        assert entity2.mergable_with(entity1)

        entity2.tile_position = (1, 1)
        assert not entity1.mergable_with(entity2)

    def test_merge(self):
        entity1 = SimpleEntityWithOwner("simple-entity-with-owner")
        entity2 = SimpleEntityWithOwner(
            "simple-entity-with-owner", tags={"some": "stuff"}
        )

        entity1.merge(entity2)
        del entity2

        assert entity1.tags == {"some": "stuff"}
