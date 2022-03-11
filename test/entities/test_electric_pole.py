# test_electric_pole.py

from draftsman.entity import ElectricPole, electric_poles
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class ElectricPoleTesting(TestCase):
    def test_constructor_init(self):
        electric_pole = ElectricPole(
            "substation", position = [1, 1],
            neighbours = [1, 2, "3"])

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            ElectricPole("small-electric-pole", unused_keyword = 10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            ElectricPole("this is not an electric pole")