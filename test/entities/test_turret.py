# test_turret.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Turret, turrets
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class TurretTesting(unittest.TestCase):
    def test_contstructor_init(self):
        turret = Turret()

        with self.assertWarns(DraftsmanWarning):
            Turret(unused_keyword="whatever")

        with self.assertRaises(InvalidEntityError):
            Turret("this is not a turret")

    def test_mergable_with(self):
        turret1 = Turret("gun-turret")
        turret2 = Turret("gun-turret", tags={"some": "stuff"})

        self.assertTrue(turret1.mergable_with(turret1))

        self.assertTrue(turret1.mergable_with(turret2))
        self.assertTrue(turret2.mergable_with(turret1))

        turret2.tile_position = (1, 1)
        self.assertFalse(turret1.mergable_with(turret2))

    def test_merge(self):
        turret1 = Turret("gun-turret")
        turret2 = Turret("gun-turret", tags={"some": "stuff"})

        turret1.merge(turret2)
        del turret2

        self.assertEqual(turret1.tags, {"some": "stuff"})
