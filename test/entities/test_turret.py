# test_turret.py

from draftsman.entity import Turret, turrets
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class TurretTesting(TestCase):
    def test_contstructor_init(self):
        turret = Turret()

        with self.assertWarns(DraftsmanWarning):
            Turret(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityError):
            Turret("this is not a turret")