# test_simple_entity_with_owner.py

from __future__ import unicode_literals

from draftsman.entity import SimpleEntityWithOwner, simple_entities_with_owner
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class SimpleEntityWithOwnerTesting(unittest.TestCase):
    def test_contstructor_init(self):
        entity = SimpleEntityWithOwner(variation=13)
        assert entity.name == simple_entities_with_owner[0]
        assert entity.variation == 13

        with self.assertWarns(DraftsmanWarning):
            SimpleEntityWithOwner(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            SimpleEntityWithOwner("this is not correct")

    def test_to_dict(self):
        entity = SimpleEntityWithOwner("simple-entity-with-owner")
        self.assertEqual(entity.variation, 1)
        self.assertEqual(
            entity.to_dict(),
            {
                "name": "simple-entity-with-owner",
                "position": {"x": 0.5, "y": 0.5},
                "variation": 1,
            },
        )

        entity.variation = None
        self.assertEqual(
            entity.to_dict(),
            {
                "name": "simple-entity-with-owner",
                "position": {"x": 0.5, "y": 0.5},
            },
        )

    def test_mergable_with(self):
        entity1 = SimpleEntityWithOwner("simple-entity-with-owner")
        entity2 = SimpleEntityWithOwner(
            "simple-entity-with-owner", tags={"some": "stuff"}
        )

        self.assertTrue(entity1.mergable_with(entity1))

        self.assertTrue(entity1.mergable_with(entity2))
        self.assertTrue(entity2.mergable_with(entity1))

        entity2.tile_position = (1, 1)
        self.assertFalse(entity1.mergable_with(entity2))

    def test_merge(self):
        entity1 = SimpleEntityWithOwner("simple-entity-with-owner")
        entity2 = SimpleEntityWithOwner(
            "simple-entity-with-owner", tags={"some": "stuff"}
        )

        entity1.merge(entity2)
        del entity2

        self.assertEqual(entity1.tags, {"some": "stuff"})
