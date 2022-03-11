# test_linked_container.py

from draftsman.entity import LinkedContainer, linked_containers
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from schema import SchemaError

from unittest import TestCase

class LinkedContainerTesting(TestCase):
    def test_contstructor_init(self):
        container = LinkedContainer(
            link_id = 1000
        )
        self.assertEqual(
            container.to_dict(),
            {
                "name": container.name,
                "position": container.position,
                "link_id": 1000
            }
        )

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LinkedContainer(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            LinkedContainer("this is not a linked container")
        with self.assertRaises(SchemaError):
            LinkedContainer(link_id = "incorrect")

    def test_set_links(self):
        container = LinkedContainer()
        container.set_links(0xFFFF)
        self.assertEqual(container.link_id, 0xFFFF)
        container.set_links(None)
        self.assertEqual(container.link_id, 0)
        with self.assertRaises(SchemaError):
            container.set_links("incorrect")

    def test_set_link(self):
        container = LinkedContainer()
        container.set_link(0, True)
        container.set_link(1, True)
        self.assertEqual(container.link_id, 0x0003)
        container.set_link(0, False)
        self.assertEqual(container.link_id, 0x0002)
        with self.assertRaises(AssertionError):
            container.set_link(100, True)
        # with self.assertRaises(SchemaError):
        #     container.set_links("incorrect")