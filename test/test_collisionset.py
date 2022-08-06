# test_collisionset.py

from draftsman.classes.collisionset import CollisionSet
from draftsman.utils import AABB, Rectangle

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class CollisionSetTesting(unittest.TestCase):
    def test_constructor(self):
        # Empty constructor
        cs = CollisionSet([])
        self.assertEqual(cs.shapes, [])

        # Test regular contents
        cs = CollisionSet([AABB(0, 0, 1, 1), Rectangle((10, 10), 1, 1, 45)])
        self.assertEqual(cs.shapes, [AABB(0, 0, 1, 1), Rectangle((10, 10), 1, 1, 45)])

        # Test position offset
        cs = CollisionSet([AABB(0, 0, 1, 1), Rectangle((10, 10), 1, 1, 45)], (-5, -5))
        self.assertEqual(
            cs.shapes, [AABB(0, 0, 1, 1, (-5, -5)), Rectangle((5, 5), 1, 1, 45)]
        )

    def test_rotate(self):
        pass  # TODO

    def test_overlap(self):
        cs1 = CollisionSet([AABB(0, 0, 1, 1), Rectangle((10, 10), 1, 1, 45)])
        cs2 = CollisionSet([AABB(0, 0, 1, 1)])
        cs3 = CollisionSet([AABB(0, 0, 1, 1)], (2, 2))

        # Identity case / early-out optimization
        self.assertTrue(cs2.overlaps(cs2))
        # Reciprocal
        self.assertTrue(cs1.overlaps(cs2))
        self.assertTrue(cs2.overlaps(cs1))
        # Test position offset
        self.assertFalse(cs1.overlaps(cs3))

    def test_get_bounding_box(self):
        pass  # TODO

    def test_eq(self):
        pass  # TODO
