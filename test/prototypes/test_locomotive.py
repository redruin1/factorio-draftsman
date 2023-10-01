# test_locomotive.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import Locomotive, locomotives, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LocomotiveTesting(unittest.TestCase):
    def test_constructor_init(self):
        locomotive = Locomotive(
            "locomotive",
            position={"x": 1.0, "y": 1.0},
            orientation=0.75,
            color=[0.0, 1.0, 0.0],
        )
        assert locomotive.to_dict() == {
            "name": "locomotive",
            "position": {"x": 1.0, "y": 1.0},
            "orientation": 0.75,
            "color": {"r": 0.0, "g": 1.0, "b": 0.0},
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            Locomotive("locomotive", unused_keyword="whatever")
        # Warn if the locomotive is not on a rail (close enough to one?)
        # TODO (Complex)

        # Errors
        with pytest.raises(InvalidEntityError):
            Locomotive("this is not a locomotive")
        with pytest.raises(TypeError):
            Locomotive("locomotive", orientation="wrong")
        # TODO: move to validate
        # with pytest.raises(DataFormatError):
        #     Locomotive("locomotive", color="also wrong")

    def test_mergable_with(self):
        train1 = Locomotive("locomotive")
        train2 = Locomotive("locomotive", color=(100, 100, 100), tags={"some": "stuff"})

        assert train1.mergable_with(train1)

        assert train1.mergable_with(train2)
        assert train2.mergable_with(train1)

        train2.orientation = 0.5
        assert not train1.mergable_with(train2)

    def test_merge(self):
        train1 = Locomotive("locomotive")
        train2 = Locomotive("locomotive", color=(100, 100, 100), tags={"some": "stuff"})

        train1.merge(train2)
        del train2

        assert train1.color == (100, 100, 100)
        assert train1.tags == {"some": "stuff"}

        assert train1.to_dict() == {
            "name": "locomotive",
            "position": {"x": 1.0, "y": 3.0},
            "color": {"r": 100, "g": 100, "b": 100},
            "tags": {"some": "stuff"}
        }

    def test_eq(self):
        train1 = Locomotive("locomotive")
        train2 = Locomotive("locomotive")

        assert train1 == train2

        train1.tags = {"some": "stuff"}

        assert train1 != train2

        container = Container()

        assert train1 != container
        assert train2 != container

        # hashable
        assert isinstance(train1, Hashable)
