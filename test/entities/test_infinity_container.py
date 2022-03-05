# test_infinity_container.py

from draftsman.entity import InfinityContainer, infinity_containers
from draftsman.errors import InvalidEntityID, InvalidItemID

from schema import SchemaError

from unittest import TestCase

class InfinityContainerTesting(TestCase):
    def test_default_constructor(self):
        container = InfinityContainer()
        self.assertEqual(
            container.to_dict(),
            {
                "name": "infinity-chest",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        container = InfinityContainer(
            infinity_settings = {
                "remove_unfiltered_items": True,
                "filters": [
                    {
                        "index": 1,
                        "name": "iron-ore",
                        "count": 100,
                        "mode": "at-least"
                    }
                ]
            }
        )
        self.assertEqual(
            container.to_dict(),
            {
                "name": "infinity-chest",
                "position": {"x": 0.5, "y": 0.5},
                "infinity_settings": {
                    "remove_unfiltered_items": True,
                    "filters": [
                        {
                            "index": 1,
                            "name": "iron-ore",
                            "count": 100,
                            "mode": "at-least"
                        }
                    ]
                }
            }
        )

        # Warnings
        with self.assertWarns(UserWarning):
            InfinityContainer(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            InfinityContainer("this is not an infinity container")

    def test_set_infinity_settings(self):
        container = InfinityContainer()
        container.set_infinity_settings(
            {
                "remove_unfiltered_items": True,
                "filters": [
                    {
                        "index": 1,
                        "name": "iron-ore",
                        "count": 100,
                        "mode": "at-least"
                    }
                ]
            }
        )
        self.assertEqual(
            container.infinity_settings,
            {
                "remove_unfiltered_items": True,
                "filters": [
                    {
                        "index": 1,
                        "name": "iron-ore",
                        "count": 100,
                        "mode": "at-least"
                    }
                ]
            }
        )
        container.set_infinity_settings(None)
        self.assertEqual(container.infinity_settings, {})
        with self.assertRaises(SchemaError):
            container.set_infinity_settings(
                {
                    "this is": ["incorrect", "for", "sure"]
                }
            )

    def test_set_remove_unfiltered_items(self):
        container = InfinityContainer()
        container.set_remove_unfiltered_items(True)
        self.assertEqual(
            container.infinity_settings,
            {
                "remove_unfiltered_items": True
            }
        )
        container.set_remove_unfiltered_items(None)
        self.assertEqual(container.infinity_settings, {})
        with self.assertRaises(SchemaError):
            container.set_remove_unfiltered_items("incorrect")

    def test_set_infinity_filters(self):
        container = InfinityContainer()
        container.set_infinity_filters([
            {
                "index": 1,
                "name": "iron-ore",
                "count": 100,
                "mode": "at-least"
            }
        ])
        self.assertEqual(
            container.infinity_settings,
            {
                "filters": [
                    {
                        "index": 1,
                        "name": "iron-ore",
                        "count": 100,
                        "mode": "at-least"
                    }
                ]
            }
        )
        container.set_infinity_filters(None)
        self.assertEqual(container.infinity_settings, {})
        with self.assertRaises(SchemaError):
            container.set_infinity_filters("incorrect")

    def test_set_infinity_filter(self):
        container = InfinityContainer()
        container.set_infinity_filter(0, "iron-ore", "at-least", 100)
        self.assertEqual(
            container.infinity_settings,
            {
                "filters": [
                    {
                        "index": 1,
                        "name": "iron-ore",
                        "count": 100,
                        "mode": "at-least"
                    }
                ]
            }
        )
        container.set_infinity_filter(1, "copper-ore", "exactly", 200)
        self.assertEqual(
            container.infinity_settings,
            {
                "filters": [
                    {
                        "index": 1,
                        "name": "iron-ore",
                        "count": 100,
                        "mode": "at-least"
                    },
                    {
                        "index": 2,
                        "name": "copper-ore",
                        "count": 200,
                        "mode": "exactly"
                    }
                ]
            }
        )
        container.set_infinity_filter(0, "uranium-ore", "at-least", 1000)
        self.assertEqual(
            container.infinity_settings,
            {
                "filters": [
                    {
                        "index": 1,
                        "name": "uranium-ore",
                        "count": 1000,
                        "mode": "at-least"
                    },
                    {
                        "index": 2,
                        "name": "copper-ore",
                        "count": 200,
                        "mode": "exactly"
                    }
                ]
            }
        )
        container.set_infinity_filter(0, None)
        self.assertEqual(
            container.infinity_settings,
            {
                "filters": [
                    {
                        "index": 2,
                        "name": "copper-ore",
                        "count": 200,
                        "mode": "exactly"
                    }
                ]
            }
        )
        
        with self.assertRaises(SchemaError):
            container.set_infinity_filter("incorrect", "iron-ore")
        with self.assertRaises(SchemaError):
            container.set_infinity_filter(0, SchemaError)
        with self.assertRaises(InvalidItemID):
            container.set_infinity_filter(0, "signal-A")
        with self.assertRaises(SchemaError):
            container.set_infinity_filter(0, "iron-ore", SchemaError)
        with self.assertRaises(AssertionError):
            container.set_infinity_filter(0, "iron-ore", "incorrect")
        with self.assertRaises(SchemaError):
            container.set_infinity_filter(0, "iron-ore", "exactly", "incorrect")
