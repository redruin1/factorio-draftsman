# test_electric_pole.py

from draftsman.entity import ElectricPole, electric_poles
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class ElectricPoleTesting(TestCase):
    def test_default_constructor(self):
        loader = ElectricPole()
        self.assertEqual(
            loader.to_dict(),
            {
                "name": "small-electric-pole",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        electric_pole = ElectricPole(
            "substation", position = [1, 1],
            neighbours = [1, 2, "3"])

        # Warnings
        with self.assertWarns(UserWarning):
            ElectricPole("small-electric-pole", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityID):
            ElectricPole("this is not an electric pole")