# test_entitylist.py
# -*- encoding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from draftsman._factorio_version import __factorio_version_info__
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.entitylist import EntityList
from draftsman.classes.group import Group
from draftsman.entity import Container, ElectricPole, new_entity
from draftsman.error import DuplicateIDError
from draftsman.utils import encode_version
from draftsman.warning import OverlappingObjectsWarning, HiddenEntityWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class EntityListTesting(unittest.TestCase):
    def test_constructor(self):
        blueprint = Blueprint()
        test = EntityList(blueprint)
        self.assertEqual(test.data, [])
        self.assertEqual(test.key_map, {})
        self.assertEqual(test.key_to_idx, {})
        self.assertEqual(test.idx_to_key, {})

        regular_list = []
        test = EntityList(blueprint, regular_list)
        self.assertEqual(test.data, [])
        self.assertEqual(test.key_map, {})
        self.assertEqual(test.key_to_idx, {})
        self.assertEqual(test.idx_to_key, {})

    def test_insert(self):
        blueprint = Blueprint()
        test = EntityList(blueprint)
        test.insert(0, "wooden-chest", id="test")

        with self.assertWarns(OverlappingObjectsWarning):
            test.insert(1, "wooden-chest")

        test.insert(0, "substation", tile_position=(10, 10), id="other")
        self.assertEqual(test.data[0].name, "substation")
        self.assertEqual(test.data[1].name, "wooden-chest")
        self.assertEqual(test.key_to_idx, {"other": 0, "test": 1})
        self.assertEqual(test.idx_to_key, {0: "other", 1: "test"})

        # Test no copy
        example = Container("steel-chest", id="test2", tile_position=(1, 0))
        test.insert(0, example, copy=False)
        self.assertEqual(test.data[0].name, "steel-chest")

        example.bar = 10
        self.assertIs(test.data[0], example)
        self.assertEqual(test.data[0].bar, 10)

        with self.assertWarns(HiddenEntityWarning):
            test.insert(1, "express-loader", tile_position=(5, 0))

        with self.assertRaises(DuplicateIDError):
            test.insert(1, "steel-chest", id="test")

        # Test poorly defined no-copy + merge
        with self.assertRaises(ValueError):
            blueprint.entities.append(Container(), copy=False, merge=True)

    def test_extend(self):
        # Test appending a list vs individually
        blueprint1 = Blueprint()
        blueprint2 = Blueprint()
        entity_list = [
            new_entity("transport-belt", tile_position=(0, 0)),
            new_entity("wooden-chest", tile_position=(1, 1)),
        ]
        blueprint1.entities.extend(entity_list)
        for e in entity_list:
            blueprint2.entities.append(e)

        self.assertEqual(blueprint1.to_dict(), blueprint2.to_dict())

    def test_remove(self):
        pass  # TODO

    def test_recursive_remove(self):
        # Test regular remove functionality
        blueprint = Blueprint()
        entity_to_remove = new_entity("transport-belt")
        blueprint.entities.append(entity_to_remove, copy=False)

        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "entity_number": 1,
                        "name": "transport-belt",
                        "position": {"x": 0.5, "y": 0.5},
                    }
                ],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        blueprint.entities.recursive_remove(entity_to_remove)

        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "version": encode_version(*__factorio_version_info__),
            },
        )

        # Test recursion
        blueprint = Blueprint()
        entity_to_remove = new_entity("transport-belt")
        group = Group()
        group.entities.append(entity_to_remove, copy=False)
        blueprint.entities.append(group, copy=False)
        blueprint.entities.append("transport-belt", tile_position=(2, 2))

        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "entity_number": 1,
                        "name": "transport-belt",
                        "position": {"x": 0.5, "y": 0.5},
                    },
                    {
                        "entity_number": 2,
                        "name": "transport-belt",
                        "position": {"x": 2.5, "y": 2.5},
                    },
                ],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        blueprint.entities.recursive_remove(entity_to_remove)

        self.assertEqual(
            blueprint.to_dict()["blueprint"],
            {
                "item": "blueprint",
                "entities": [
                    {
                        "entity_number": 1,
                        "name": "transport-belt",
                        "position": {"x": 2.5, "y": 2.5},
                    }
                ],
                "version": encode_version(*__factorio_version_info__),
            },
        )

        # Test ValueError
        with self.assertRaises(ValueError):
            blueprint.entities.recursive_remove(entity_to_remove)

    def test_getitem(self):
        blueprint = Blueprint()
        test = EntityList(blueprint)

        test.append("wooden-chest", tile_position=(0, 0))
        test.append("wooden-chest", tile_position=(1, 0), id="something")

        self.assertIs(test[0], test.data[0])

        self.assertIs(test[1], test.data[1])
        self.assertIs(test["something"], test.key_map["something"])

        # Test tuple access
        g = Group("example_group")
        g.entities.append("inserter", tile_position=(0, 1), id="example")
        test.append(g)
        self.assertIs(
            test[("example_group", "example")],
            test["example_group"].entities["example"],
        )

        del test["example_group"]

        g2 = Group("other_group")
        g2.entities.append(g)
        test.append(g2)
        self.assertIs(
            test[("other_group", "example_group", "example")],
            test["other_group"].entities["example_group"].entities["example"],
        )

        self.assertEqual(test[:], [test.data[0], test.data[1], test.data[2]])

    def test_setitem(self):
        blueprint = Blueprint()

        blueprint.entities.append("small-electric-pole", id="something")
        blueprint.entities.append("steel-chest", tile_position=(1, 1))

        self.assertEqual(blueprint.entities["something"], blueprint.entities.data[0])
        self.assertEqual(
            blueprint.entities.key_map, {"something": blueprint.entities.data[0]}
        )
        self.assertEqual(blueprint.entities.key_to_idx, {"something": 0})
        self.assertEqual(blueprint.entities.idx_to_key, {0: "something"})

        # Set index
        blueprint.entities[0] = Container(tile_position=(10, 10))
        self.assertEqual(len(blueprint.entities), 2)

        with self.assertRaises(KeyError):
            blueprint.entities["something"]

        # Set index with id
        blueprint.entities[0] = Container(tile_position=(10, 10), id="new")
        self.assertEqual(blueprint.entities["new"], blueprint.entities.data[0])
        self.assertEqual(blueprint.entities.key_to_idx, {"new": 0})
        self.assertEqual(blueprint.entities.idx_to_key, {0: "new"})

        # Set key
        # blueprint.entities["new"] = Container(tile_position = (10, 10))

        with self.assertWarns(OverlappingObjectsWarning):
            blueprint.entities[0] = new_entity("substation")

        with self.assertRaises(TypeError):
            blueprint.entities[0] = "something incorrect"

    def test_delitem(self):
        blueprint = Blueprint()

        blueprint.entities.append("wooden-chest")
        blueprint.entities.append("wooden-chest", tile_position=(1, 0), id="a")

        # Test index
        del blueprint.entities[0]

        self.assertEqual(blueprint.entities.data, [blueprint.entities[0]])
        self.assertEqual(blueprint.entities.key_map, {"a": blueprint.entities[0]})
        self.assertEqual(blueprint.entities.key_to_idx, {"a": 0})
        self.assertEqual(blueprint.entities.idx_to_key, {0: "a"})

        # Test key
        del blueprint.entities["a"]

        self.assertEqual(blueprint.entities.data, [])
        self.assertEqual(blueprint.entities.key_map, {})
        self.assertEqual(blueprint.entities.key_to_idx, {})
        self.assertEqual(blueprint.entities.idx_to_key, {})

        # Test slice
        blueprint.entities.append("wooden-chest")
        blueprint.entities.append("wooden-chest", tile_position=(1, 0), id="a")

        del blueprint.entities[:]

        self.assertEqual(blueprint.entities.data, [])
        self.assertEqual(blueprint.entities.key_map, {})
        self.assertEqual(blueprint.entities.key_to_idx, {})
        self.assertEqual(blueprint.entities.idx_to_key, {})

    def test_contains(self):
        blueprint = Blueprint()

        entityA = ElectricPole("small-electric-pole")
        entityB = ElectricPole("small-electric-pole", tile_position=(1, 0))
        entityC = Container("wooden-chest", tile_position=(2, 0))

        group = Group()
        group.entities.append(entityA, copy=False)
        group.entities.append(entityB, copy=False)

        blueprint.entities.append(group, copy=False)
        blueprint.entities.append(entityC, copy=False)

        self.assertIn(entityA, group.entities)
        self.assertIn(entityA, blueprint.entities)
        self.assertIn(entityB, group.entities)
        self.assertIn(entityB, blueprint.entities)
        self.assertNotIn(entityC, group.entities)
        self.assertIn(entityC, blueprint.entities)
