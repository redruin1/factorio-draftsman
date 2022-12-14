# test_linked_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LinkedContainer, linked_containers
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

import sys

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LinkedContainerTesting(unittest.TestCase):
    def test_contstructor_init(self):
        container = LinkedContainer(link_id=1000)
        self.assertEqual(
            container.to_dict(),
            {
                "name": container.name,
                "position": container.position.to_dict(),
                "link_id": 1000,
            },
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LinkedContainer(unused_keyword="whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            LinkedContainer("this is not a linked container")
        with self.assertRaises(TypeError):
            LinkedContainer(link_id="incorrect")

    def test_set_link(self):
        container = LinkedContainer()
        container.set_link(0, True)
        container.set_link(1, True)
        self.assertEqual(container.link_id, 0x0003)
        container.set_link(0, False)
        self.assertEqual(container.link_id, 0x0002)

        with self.assertRaises(ValueError):
            container.set_link(100, True)
        with self.assertRaises(ValueError):
            container.set_link("incorrect", False)

    def test_set_links(self):
        container = LinkedContainer()
        container.link_id = 0xFFFF
        self.assertEqual(container.link_id, 0xFFFF)
        container.link_id = None
        self.assertEqual(container.link_id, 0)
        with self.assertRaises(TypeError):
            container.link_id = "incorrect"

    def test_mergable_with(self):
        container1 = LinkedContainer()
        container2 = LinkedContainer(link_id=0xFFFF, tags={"some": "stuff"})

        self.assertTrue(container1.mergable_with(container1))

        self.assertTrue(container1.mergable_with(container2))
        self.assertTrue(container2.mergable_with(container1))

        container2.tile_position = (1, 1)
        self.assertFalse(container1.mergable_with(container2))

    def test_merge(self):
        container1 = LinkedContainer()
        container2 = LinkedContainer(link_id=0xFFFF, tags={"some": "stuff"})

        container1.merge(container2)
        del container2

        self.assertEqual(container1.link_id, 0xFFFF)
        self.assertEqual(container1.tags, {"some": "stuff"})
