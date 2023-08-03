# test_infinity_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import InfinityContainer, infinity_containers
from draftsman.error import (
    InvalidEntityError,
    InvalidItemError,
    InvalidModeError,
    DataFormatError,
)
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class InfinityContainerTesting(unittest.TestCase):
    def test_constructor_init(self):
        container = InfinityContainer(
            infinity_settings={
                "remove_unfiltered_items": True,
                "filters": [
                    {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
                ],
            }
        )
        assert container.to_dict() == {
            "name": "infinity-chest",
            "position": {"x": 0.5, "y": 0.5},
            "infinity_settings": {
                "remove_unfiltered_items": True,
                "filters": [
                    {
                        "index": 1,
                        "name": "iron-ore",
                        "count": 100,
                        "mode": "at-least",
                    }
                ],
            },
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            InfinityContainer(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            InfinityContainer("this is not an infinity container")

    def test_set_infinity_settings(self):
        container = InfinityContainer()
        container.infinity_settings = {
            "remove_unfiltered_items": True,
            "filters": [
                {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
            ],
        }
        assert container.infinity_settings == {
            "remove_unfiltered_items": True,
            "filters": [
                {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
            ],
        }
        container.infinity_settings = None
        assert container.infinity_settings == {}
        with pytest.raises(DataFormatError):
            container.infinity_settings = {"this is": ["incorrect", "for", "sure"]}

    def test_set_remove_unfiltered_items(self):
        container = InfinityContainer()
        container.remove_unfiltered_items = True
        assert container.remove_unfiltered_items == True
        assert container.infinity_settings == {"remove_unfiltered_items": True}
        container.remove_unfiltered_items = None
        assert container.infinity_settings == {}
        with pytest.raises(TypeError):
            container.remove_unfiltered_items = "incorrect"

    def test_set_infinity_filters(self):
        container = InfinityContainer()
        container.set_infinity_filters(
            [{"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}]
        )
        assert container.infinity_settings == {
            "filters": [
                {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
            ]
        }
        container.set_infinity_filters(None)
        assert container.infinity_settings == {}
        with pytest.raises(DataFormatError):
            container.set_infinity_filters("incorrect")

    def test_set_infinity_filter(self):
        container = InfinityContainer()
        container.set_infinity_filter(0, "iron-ore", "at-least", 100)
        assert container.infinity_settings == {
            "filters": [
                {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
            ]
        }
        container.set_infinity_filter(1, "copper-ore", "exactly", 200)
        assert container.infinity_settings == {
            "filters": [
                {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"},
                {"index": 2, "name": "copper-ore", "count": 200, "mode": "exactly"},
            ]
        }
        container.set_infinity_filter(0, "uranium-ore", "at-least", 1000)
        assert container.infinity_settings == {
            "filters": [
                {
                    "index": 1,
                    "name": "uranium-ore",
                    "count": 1000,
                    "mode": "at-least",
                },
                {"index": 2, "name": "copper-ore", "count": 200, "mode": "exactly"},
            ]
        }
        container.set_infinity_filter(0, None)
        assert container.infinity_settings == {
            "filters": [
                {"index": 2, "name": "copper-ore", "count": 200, "mode": "exactly"}
            ]
        }

        # Default count
        container.set_infinity_filter(0, "iron-ore", "at-least")
        assert container.infinity_settings == {
            "filters": [
                {"index": 2, "name": "copper-ore", "count": 200, "mode": "exactly"},
                {"index": 1, "name": "iron-ore", "count": 50, "mode": "at-least"},
            ]
        }

        with pytest.raises(TypeError):
            container.set_infinity_filter("incorrect", "iron-ore")
        with pytest.raises(TypeError):
            container.set_infinity_filter(0, SchemaError)
        with pytest.raises(InvalidItemError):
            container.set_infinity_filter(0, "signal-A")
        with pytest.raises(TypeError):
            container.set_infinity_filter(0, "iron-ore", SchemaError)
        with pytest.raises(InvalidModeError):
            container.set_infinity_filter(0, "iron-ore", "incorrect")
        with pytest.raises(TypeError):
            container.set_infinity_filter(0, "iron-ore", "exactly", "incorrect")
        with pytest.raises(IndexError):
            container.set_infinity_filter(-1, "iron-ore", "exactly", 200)
        with pytest.raises(IndexError):
            container.set_infinity_filter(1000, "iron-ore", "exactly", 200)
        with pytest.raises(ValueError):
            container.set_infinity_filter(1, "iron-ore", "exactly", -1)

    def test_mergable_with(self):
        container1 = InfinityContainer("infinity-chest")
        container2 = InfinityContainer(
            "infinity-chest",
            items={"copper-plate": 100},
            infinity_settings={
                "remove_unfiltered_items": True,
                "filters": [
                    {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
                ],
            },
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = InfinityContainer("infinity-chest")
        container2 = InfinityContainer(
            "infinity-chest",
            items={"copper-plate": 100},
            infinity_settings={
                "remove_unfiltered_items": True,
                "filters": [
                    {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
                ],
            },
        )

        container1.merge(container2)
        del container2

        assert container1.items == {"copper-plate": 100}
        assert container1.infinity_settings == {
            "remove_unfiltered_items": True,
            "filters": [
                {"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
            ],
        }
