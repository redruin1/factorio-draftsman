# test_simple_entity_with_force.py

from draftsman.constants import Direction
from draftsman.entity import SimpleEntityWithForce, simple_entities_with_force
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

import pytest


class TestSimpleEntityWithForce:
    def test_contstructor_init(self):
        entity = SimpleEntityWithForce(variation=13)
        assert entity.name == simple_entities_with_force[0]
        assert entity.variation == 13

        with pytest.warns(UnknownKeywordWarning):
            SimpleEntityWithForce(unused_keyword="whatever").validate().reissue_all()

        with pytest.warns(UnknownEntityWarning):
            SimpleEntityWithForce("this is not correct").validate().reissue_all()

    def test_to_dict(self):
        entity = SimpleEntityWithForce("simple-entity-with-force")
        assert entity.variation == 1
        assert entity.to_dict(exclude_defaults=False) == {
            "name": "simple-entity-with-force",
            "quality": "normal",  # Default
            "position": {"x": 0.5, "y": 0.5},
            "direction": Direction.NORTH,  # Default
            "variation": 1,  # Default
            "tags": {},  # Default
        }

        entity.variation = None
        assert entity.variation == None
        assert entity.to_dict(exclude_defaults=False) == {
            "name": "simple-entity-with-force",
            "quality": "normal",  # Default
            "position": {"x": 0.5, "y": 0.5},
            "direction": Direction.NORTH,  # Default
            "tags": {},  # Default
        }

    def test_power_and_circuit_flags(self):
        for name in simple_entities_with_force:
            entity = SimpleEntityWithForce(name)
            assert entity.power_connectable == False
            assert entity.dual_power_connectable == False
            assert entity.circuit_connectable == False
            assert entity.dual_circuit_connectable == False

    def test_mergable_with(self):
        entity1 = SimpleEntityWithForce("simple-entity-with-force")
        entity2 = SimpleEntityWithForce(
            "simple-entity-with-force", tags={"some": "stuff"}
        )

        assert entity1.mergable_with(entity1)

        assert entity1.mergable_with(entity2)
        assert entity2.mergable_with(entity1)

        entity2.tile_position = (1, 1)
        assert not entity1.mergable_with(entity2)

    def test_merge(self):
        entity1 = SimpleEntityWithForce("simple-entity-with-force")
        entity2 = SimpleEntityWithForce(
            "simple-entity-with-force", tags={"some": "stuff"}
        )

        entity1.merge(entity2)
        del entity2

        assert entity1.tags == {"some": "stuff"}
