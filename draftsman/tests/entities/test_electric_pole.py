# test_electric_pole.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import ElectricPole, electric_poles
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class ElectricPoleTesting(TestCase):
    def test_constructor_init(self):
        electric_pole = ElectricPole(
            "substation", position=[1, 1], neighbours=[1, 2, "3"]
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            ElectricPole("small-electric-pole", unused_keyword=10)

        # Errors
        with self.assertRaises(InvalidEntityError):
            ElectricPole("this is not an electric pole")
