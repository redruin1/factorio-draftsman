# test_linked_belt.py

from draftsman.entity import LinkedBelt, linked_belts
from draftsman.errors import InvalidEntityID

from unittest import TestCase

class LinkedBeltTesting(TestCase):
    def test_default_constructor(self):
        linked_belt = LinkedBelt()
        self.assertEqual(
            linked_belt.to_dict(),
            {
                "name": "linked-belt",
                "position": {"x": 0.5, "y": 0.5}
            }
        )

    def test_constructor_init(self):
        linked_belt = LinkedBelt()

        # Warnings
        with self.assertWarns(UserWarning):
            LinkedBelt(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityID):
            LinkedBelt("this is not a linked belt")