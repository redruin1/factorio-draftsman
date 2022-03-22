# test_group.py

from draftsman.classes import Group
from draftsman.entity import *
from draftsman.warning import DraftsmanWarning

from unittest import TestCase


class GroupTesting(TestCase):
    def test_default_constructor(self):
        group = Group()
        self.assertEqual(group.name, "group")
        self.assertEqual(group.type, "group")
        self.assertEqual(group.id, None)
        self.assertEqual(group.tile_width, 0)
        self.assertEqual(group.tile_height, 0)
        self.assertEqual(group.to_dict(), [])

    def test_constructor_init(self):
        entity_list = [
            Furnace(),
            Container(),
            ProgrammableSpeaker()
        ]
        group = Group(
            name = "groupA",
            type = "custom_type",
            id = "test_group",
            position = {"x": 124.4, "y": 1.645},
            entities = entity_list
        )
        self.assertEqual(group.name, "groupA")
        self.assertEqual(group.type, "custom_type")
        self.assertEqual(group.id, "test_group")
        self.assertEqual(group.position, {"x": 124.4, "y": 1.645})
        self.assertEqual(group.entities, entity_list)

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            Group(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(TypeError):
            Group(name = TypeError)

        with self.assertRaises(TypeError):
            Group(type = TypeError)

        with self.assertRaises(TypeError):
            Group(id = TypeError)

        with self.assertRaises(TypeError):
            Group(position = "incorrect")

        with self.assertRaises(TypeError): # TODO: maybe change this?
            Group(entities = InvalidEntityError)

        with self.assertRaises(InvalidEntityError):
            Group(entities = ["incorrect"])

    def test_add_entity(self):
        group = Group()
        furnace = Furnace("electric-furnace", position = [2.0, 2.0])
        group.add_entity(furnace)
        self.assertEqual(
            group.entities,
            [furnace]
        )

        with self.assertRaises(InvalidEntityError):
            group.add_entity(InvalidEntityError)

    def test_remove_entity(self):
        pass

    def test_get_area(self):
        pass

    def test_to_dict(self):
        pass