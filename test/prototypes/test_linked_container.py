# test_linked_container.py

from draftsman.entity import LinkedContainer, linked_containers, Container
from draftsman.error import DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_linked_container():
    if len(linked_containers) == 0:
        return None
    return LinkedContainer(
        "linked-chest",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        # item_requests=[],
        bar=10,
        link_id=123,
        tags={"blah": "blah"},
    )


# For compatibility with versions of Factorio prior to 1.0.0
@pytest.mark.skipif(len(linked_containers) == 0, reason="No linked containers to test")
class TestLinkedContainer:
    def test_constructor_init(self):
        container = LinkedContainer("linked-chest", link_id=1000)
        assert container.to_dict() == {
            "name": container.name,
            "position": container.position.to_dict(),
            "link_id": 1000,
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            LinkedContainer("this is not a linked container").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            LinkedContainer(
                "linked-chest", link_id="incorrect"
            ).validate().reissue_all()

    def test_set_link(self):
        container = LinkedContainer("linked-chest")
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
        container = LinkedContainer("linked-chest")
        container.link_id = 0xFFFF
        assert container.link_id == 0xFFFF

        container.link_id = 0xFFFF_FFFF_FFFF
        assert container.link_id == 0xFFFF_FFFF

        with pytest.raises(DataFormatError):
            container.link_id = "incorrect"

    def test_mergable_with(self):
        container1 = LinkedContainer("linked-chest")
        container2 = LinkedContainer(link_id=0xFFFF, tags={"some": "stuff"})

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = LinkedContainer("linked-chest")
        container2 = LinkedContainer(link_id=0xFFFF, tags={"some": "stuff"})

        container1.merge(container2)
        del container2

        assert container1.link_id == 0xFFFF
        assert container1.tags == {"some": "stuff"}

    def test_eq(self):
        container1 = LinkedContainer("linked-chest")
        container2 = LinkedContainer("linked-chest")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container1, Hashable)
