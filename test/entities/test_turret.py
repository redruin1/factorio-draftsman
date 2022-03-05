# test_turret.py

from draftsman.entity import Turret, turrets
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class TurretTesting(TestCase):
    def test_default_constructor(self):
        turret = Turret()
        self.assertEqual(
            turret.to_dict(),
            {
                "name": "gun-turret",
                "position": {"x": 1.0, "y": 1.0}
            }
        )

    def test_contstructor_init(self):
        turret = Turret()

        with self.assertWarns(UserWarning):
            Turret(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            Turret("this is not a turret")