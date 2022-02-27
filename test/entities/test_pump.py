# test_pump.py

from draftsman.entity import Pump, pumps
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class PumpTesting(TestCase):
    def test_default_constructor(self):
        pump = Pump()
        self.assertEqual(
            pump.to_dict(),
            {
                "name": "pump",
                "position": {"x": 0.5, "y": 1.0}
            }
        )

    def test_constructor_init(self):
        #loader = Loader()

        # Warnings
        with self.assertWarns(UserWarning):
            Pump("pump", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityID):
            Pump("this is not a pump")