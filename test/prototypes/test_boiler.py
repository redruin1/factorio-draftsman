# test_boiler.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Boiler, boilers
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class BoilerTesting(unittest.TestCase):
    def test_constructor_init(self):
        boiler = Boiler("boiler")

        # Warnings
        with pytest.warns(DraftsmanWarning):
            Boiler(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            Boiler("not a boiler")

    def test_mergable_with(self):
        boiler1 = Boiler("boiler")
        boiler2 = Boiler("boiler", tags={"some": "stuff"})

        assert boiler1.mergable_with(boiler2)
        assert boiler2.mergable_with(boiler1)

        boiler2.tile_position = [-10, -10]
        assert not boiler1.mergable_with(boiler2)

    def test_merge(self):
        boiler1 = Boiler("boiler")
        boiler2 = Boiler("boiler", tags={"some": "stuff"})

        boiler1.merge(boiler2)
        del boiler2

        assert boiler1.tags == {"some": "stuff"}
