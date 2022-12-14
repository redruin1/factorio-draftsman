# test_artillery_wagon.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import ArtilleryWagon, artillery_wagons
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class ArtilleryWagonTesting(unittest.TestCase):
    def test_constructor_init(self):
        artillery_wagon = ArtilleryWagon(
            "artillery-wagon",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
        )
        assert artillery_wagon.to_dict() == {
            "name": "artillery-wagon",
            "position": {"x": 1.0, "y": 1.0},
            "orientation": 0.75,
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            ArtilleryWagon("artillery-wagon", unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            ArtilleryWagon("this is not an artillery wagon")
        with pytest.raises(TypeError):
            ArtilleryWagon("artillery-wagon", orientation="wrong")

    def test_mergable_with(self):
        wagon1 = ArtilleryWagon("artillery-wagon")
        wagon2 = ArtilleryWagon("artillery-wagon")

        assert wagon1.mergable_with(wagon2)
        assert wagon2.mergable_with(wagon1)

        wagon1.orientation = 0.5
        assert not wagon1.mergable_with(wagon2)

    def test_merge(self):
        wagon1 = ArtilleryWagon("artillery-wagon")
        wagon2 = ArtilleryWagon("artillery-wagon")
        wagon2.tags = {"some": "stuff"}

        wagon1.merge(wagon2)
        assert wagon1.tags == {"some": "stuff"}
        # Ensure wagon1's data remains valid even if wagon2 gets destroyed
        del wagon2
        assert wagon1.tags == {"some": "stuff"}
