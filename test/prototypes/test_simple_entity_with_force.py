# test_simple_entity_with_force.py

from __future__ import unicode_literals

from draftsman.entity import SimpleEntityWithForce, simple_entities_with_force
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class SimpleEntityWithForceTesting(unittest.TestCase):
    def test_contstructor_init(self):
        entity = SimpleEntityWithForce(variation=13)
        assert entity.name == simple_entities_with_force[0]
        assert entity.variation == 13

        with pytest.warns(DraftsmanWarning):
            SimpleEntityWithForce(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            SimpleEntityWithForce("this is not correct")

    def test_to_dict(self):
        entity = SimpleEntityWithForce("simple-entity-with-force")
        assert entity.variation == 1
        assert entity.to_dict() == {
            "name": "simple-entity-with-force",
            "position": {"x": 0.5, "y": 0.5},
            "variation": 1,
        }

        entity.variation = None
        assert entity.to_dict() == {
            "name": "simple-entity-with-force",
            "position": {"x": 0.5, "y": 0.5},
        }

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
