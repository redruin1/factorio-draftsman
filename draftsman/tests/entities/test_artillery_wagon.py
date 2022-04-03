# test_artillery_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import ArtilleryWagon, artillery_wagons
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    from unittest import TestCase
else:  # pragma: no coverage
    from unittest2 import TestCase


class ArtilleryWagonTesting(TestCase):
    def test_constructor_init(self):
        artillery_wagon = ArtilleryWagon(
            "artillery-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
        )
        self.assertEqual(
            artillery_wagon.to_dict(),
            {
                "name": "artillery-wagon",
                "position": {"x": 1.0, "y": 1.0},
                "orientation": 0.75,
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            ArtilleryWagon("artillery-wagon", unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            ArtilleryWagon("this is not an artillery wagon")
        with self.assertRaises(TypeError):
            ArtilleryWagon("artillery-wagon", orientation="wrong")
