# test_rocket_silo.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import RocketSilo, rocket_silos
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class RocketSiloTesting(unittest.TestCase):
    def test_contstructor_init(self):
        silo = RocketSilo(auto_launch=True)
        assert silo.to_dict() == {
            "name": "rocket-silo",
            "position": {"x": 4.5, "y": 4.5},
            "auto_launch": True,
        }

        with pytest.warns(DraftsmanWarning):
            RocketSilo(unused_keyword="whatever")

        with pytest.raises(InvalidEntityError):
            RocketSilo("this is not a rocket silo")
        with pytest.raises(TypeError):
            RocketSilo(auto_launch="incorrect")

    def test_mergable_with(self):
        silo1 = RocketSilo("rocket-silo")
        silo2 = RocketSilo("rocket-silo", auto_launch=True, tags={"some": "stuff"})

        assert silo1.mergable_with(silo1)

        assert silo1.mergable_with(silo2)
        assert silo2.mergable_with(silo1)

        silo2.tile_position = (1, 1)
        assert not silo1.mergable_with(silo2)

    def test_merge(self):
        silo1 = RocketSilo("rocket-silo")
        silo2 = RocketSilo("rocket-silo", auto_launch=True, tags={"some": "stuff"})

        silo1.merge(silo2)
        del silo2

        assert silo1.auto_launch == True
        assert silo1.tags == {"some": "stuff"}
