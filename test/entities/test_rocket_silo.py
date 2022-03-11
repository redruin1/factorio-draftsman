# test_rocket_silo.py

from draftsman.entity import RocketSilo, rocket_silos
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class RocketSiloTesting(TestCase):
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

        with self.assertWarns(DraftsmanWarning):
            RocketSilo(unused_keyword = "whatever")

        with self.assertRaises(InvalidEntityError):
            RocketSilo("this is not a rocket silo")