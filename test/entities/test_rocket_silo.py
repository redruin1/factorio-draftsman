# test_rocket_silo.py

from draftsman.entity import RocketSilo, rocket_silos
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class RocketSiloTesting(TestCase):
    def test_default_constructor(self):
        silo = RocketSilo()
        self.assertEqual(
            silo.to_dict(),
            {
                "name": "rocket-silo",
                "position": {"x": 4.5, "y": 4.5}
            }
        )

    def test_contstructor_init(self):
        silo = RocketSilo(
            auto_launch = True
        )
        self.assertEqual(
            silo.to_dict(),
            {
                "name": "rocket-silo",
                "position": {"x": 4.5, "y": 4.5},
                "auto_launch": True
            }
        )

        with self.assertWarns(UserWarning):
            RocketSilo(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityID):
            RocketSilo("this is not a rocket silo")