# test_linked_container.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.entity import LinkedContainer, linked_containers, Container
from draftsman.error import InvalidEntityError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class LinkedContainerTesting(unittest.TestCase):
    def test_contstructor_init(self):
        container = LinkedContainer(link_id=1000)
        assert container.to_dict() == {
            "name": container.name,
            "position": container.position.to_dict(),
            "link_id": 1000,
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            LinkedContainer(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            LinkedContainer("this is not a linked container")
        with pytest.raises(TypeError):
            LinkedContainer(link_id="incorrect")

    def test_set_link(self):
        container = LinkedContainer()
        container.set_link(0, True)
        container.set_link(1, True)
        assert container.link_id == 0x0003
        container.set_link(0, False)
        assert container.link_id == 0x0002

        with pytest.raises(ValueError):
            container.set_link(100, True)
        with pytest.raises(ValueError):
            container.set_link("incorrect", False)

    def test_set_links(self):
        container = LinkedContainer()
        container.link_id = 0xFFFF
        assert container.link_id == 0xFFFF
        container.link_id = None
        assert container.link_id == 0
        with pytest.raises(TypeError):
            container.link_id = "incorrect"

    def test_mergable_with(self):
        container1 = LinkedContainer()
        container2 = LinkedContainer(link_id=0xFFFF, tags={"some": "stuff"})

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LinkedContainer()
        container2 = LinkedContainer(link_id=0xFFFF, tags={"some": "stuff"})

        container1.merge(container2)
        del container2

        assert container1.link_id == 0xFFFF
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LinkedContainer()
        container2 = LinkedContainer()

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
