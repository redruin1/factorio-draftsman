# test_linked_belt.py

from draftsman.entity import LinkedBelt, linked_belts
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from unittest import TestCase

class LinkedBeltTesting(TestCase):
    def test_constructor_init(self):
        linked_belt = LinkedBelt()

        # Warnings
        with self.assertWarns(DraftsmanWarning):
            LinkedBelt(unused_keyword = "whatever")

        # Errors
        with self.assertRaises(InvalidEntityError):
            LinkedBelt("this is not a linked belt")