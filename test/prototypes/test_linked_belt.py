# test_linked_belt.py

from draftsman.entity import LinkedBelt, linked_belts, Container
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


# For compatibility with versions of Factorio prior to 1.1.6
pytest.mark.skipif(len(linked_belts) == 0, "No linked belts to test")


class TestLinkedBelt:
    def test_constructor_init(self):
        linked_belt = LinkedBelt("linked-belt")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            LinkedBelt(unused_keyword="whatever")
        with pytest.warns(UnknownEntityWarning):
            LinkedBelt("this is not a linked belt")

        # Errors

    def test_mergable_with(self):
        belt1 = LinkedBelt("linked-belt")
        belt2 = LinkedBelt("linked-belt", tags={"some": "stuff"})

        assert belt1.mergable_with(belt1)

        assert belt1.mergable_with(belt2)
        assert belt2.mergable_with(belt1)

        belt2.tile_position = (1, 1)
        assert not belt1.mergable_with(belt2)

    def test_merge(self):
        belt1 = LinkedBelt("linked-belt")
        belt2 = LinkedBelt("linked-belt", tags={"some": "stuff"})

        belt1.merge(belt2)
        del belt2

        assert belt1.tags == {"some": "stuff"}

    def test_eq(self):
        belt1 = LinkedBelt("linked-belt")
        belt2 = LinkedBelt("linked-belt")

        assert belt1 == belt2

        belt1.tags = {"some": "stuff"}

        assert belt1 != belt2

        container = Container()

        assert belt1 != container
        assert belt2 != container

        # hashable
        assert isinstance(belt1, Hashable)
