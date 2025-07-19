# test_infinity_container.py

from draftsman.constants import ValidationMode
from draftsman.entity import InfinityContainer, infinity_containers, Container
from draftsman.error import (
    DataFormatError,
)
import draftsman.validators
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_infinity_container():
    return InfinityContainer(
        "infinity-chest",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        # item_requests=[],
        bar=10,
        filters=[InfinityContainer.Filter(index=0, name="iron-ore", count=50)],
        remove_unfiltered_items=True,
        tags={"blah": "blah"},
    )


class TestInfinityContainer:
    def test_constructor_init(self):
        container = InfinityContainer(
            remove_unfiltered_items=True,
            filters=[
                InfinityContainer.Filter(
                    index=1, name="iron-ore", count=100, mode="at-least"
                )
            ],
        )
        assert container.to_dict() == {
            "name": "infinity-chest",
            "position": {"x": 0.5, "y": 0.5},
            "infinity_settings": {
                "remove_unfiltered_items": True,
                "filters": [
                    {
                        "index": 1,
                        "name": "iron-ore",
                        "count": 100,
                        # "mode": "at-least", # Default
                    }
                ],
            },
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            InfinityContainer(
                "this is not an infinity container"
            ).validate().reissue_all()

    def test_set_remove_unfiltered_items(self):
        container = InfinityContainer()
        assert container.remove_unfiltered_items == False

        container.remove_unfiltered_items = True
        assert container.remove_unfiltered_items == True

        with pytest.raises(DataFormatError):
            container.remove_unfiltered_items = "incorrect"

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            container.remove_unfiltered_items = "incorrect"
            assert container.remove_unfiltered_items == "incorrect"

    def test_set_infinity_filter(self):
        container = InfinityContainer()

        container.set_infinity_filter(0, "iron-ore", "at-least", 100)
        assert container.filters == [
            InfinityContainer.Filter(
                **{"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
            )
        ]

        container.set_infinity_filter(1, "copper-ore", "exactly", 200)
        assert container.filters == [
            InfinityContainer.Filter(
                **{"index": 1, "name": "iron-ore", "count": 100, "mode": "at-least"}
            ),
            InfinityContainer.Filter(
                **{"index": 2, "name": "copper-ore", "count": 200, "mode": "exactly"}
            ),
        ]

        container.set_infinity_filter(0, "uranium-ore", "at-least", 1000)
        assert container.filters == [
            InfinityContainer.Filter(
                **{"index": 1, "name": "uranium-ore", "count": 1000, "mode": "at-least"}
            ),
            InfinityContainer.Filter(
                **{"index": 2, "name": "copper-ore", "count": 200, "mode": "exactly"}
            ),
        ]

        container.set_infinity_filter(0, None)
        assert container.filters == [
            InfinityContainer.Filter(
                **{"index": 2, "name": "copper-ore", "count": 200, "mode": "exactly"}
            ),
        ]

        # Default count
        container.set_infinity_filter(0, "iron-ore", "at-least")
        assert container.filters == [
            InfinityContainer.Filter(
                **{"index": 2, "name": "copper-ore", "count": 200, "mode": "exactly"}
            ),
            InfinityContainer.Filter(
                **{"index": 1, "name": "iron-ore", "count": 50, "mode": "at-least"}
            ),
        ]

        with pytest.raises(DataFormatError):
            container.filters = "incorrect"

        with pytest.raises(ValueError):  # TODO fix
            container.set_infinity_filter("incorrect", "iron-ore")
        with pytest.raises(DataFormatError):
            container.set_infinity_filter(0, TypeError)
        # with pytest.raises(InvalidItemError): # TODO
        #     container.set_infinity_filter(0, "signal-A")
        with pytest.raises(DataFormatError):
            container.set_infinity_filter(0, "iron-ore", TypeError)
        with pytest.raises(DataFormatError):
            container.set_infinity_filter(0, "iron-ore", "incorrect")
        with pytest.raises(DataFormatError):
            container.set_infinity_filter(0, "iron-ore", "exactly", "incorrect")
        # with pytest.raises(DataFormatError): # TODO
        #     container.set_infinity_filter(-1, "iron-ore", "exactly", 200)
        # with pytest.raises(IndexError): # TODO(?)
        #     container.set_infinity_filter(1000, "iron-ore", "exactly", 200)
        # with pytest.raises(DataFormatError): # TODO
        #     container.set_infinity_filter(1, "iron-ore", "exactly", -1)

    def test_mergable_with(self):
        container1 = InfinityContainer("infinity-chest")
        container2 = InfinityContainer(
            "infinity-chest",
            # items={"copper-plate": 100},
            remove_unfiltered_items=True,
            filters=[
                InfinityContainer.Filter(
                    index=1, name="iron-ore", count=100, mode="at-least"
                )
            ],
        )

        assert container1.mergable_with(container1)

        assert container1.mergable_with(container2)
        assert container2.mergable_with(container1)

        container2.tile_position = (1, 1)
        assert not container1.mergable_with(container2)

    def test_merge(self):
        container1 = InfinityContainer("infinity-chest")
        container2 = InfinityContainer(
            "infinity-chest",
            remove_unfiltered_items=True,
            filters=[
                InfinityContainer.Filter(
                    index=1, name="iron-ore", count=100, mode="at-least"
                )
            ],
        )

        container1.merge(container2)
        del container2

        assert container1.remove_unfiltered_items == True
        assert container1.filters == [
            InfinityContainer.Filter(
                index=1, name="iron-ore", count=100, mode="at-least"
            )
        ]

    def test_eq(self):
        container1 = InfinityContainer("infinity-chest")
        container2 = InfinityContainer("infinity-chest")

        assert container1 == container2

        container1.tags = {"some": "stuff"}

        assert container1 != container2

        container = Container()

        assert container1 != container
        assert container2 != container

        # hashable
        assert isinstance(container, Hashable)
