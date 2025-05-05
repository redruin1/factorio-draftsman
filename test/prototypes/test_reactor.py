# test_reactor.py

from draftsman.constants import Inventory
from draftsman.entity import Reactor, reactors, Container
from draftsman.error import DataFormatError
from draftsman.signatures import AttrsItemRequest
from draftsman.warning import (
    FuelLimitationWarning,
    FuelCapacityWarning,
    ItemLimitationWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


class TestReactor:
    def test_constructor_init(self):
        reactor = Reactor("nuclear-reactor")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Reactor.from_dict(
                {"name": "nuclear-reactor", "unused_keyword": "whatever"}
            ).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            Reactor("this is not a reactor").validate().reissue_all()

    def test_set_fuel_request(self):
        reactor = Reactor("nuclear-reactor")
        assert reactor.allowed_fuel_items == {"uranium-fuel-cell"}
        assert reactor.fuel_input_size == 1

        reactor.set_item_request("uranium-fuel-cell", 50, inventory=Inventory.fuel)
        assert reactor.item_requests == [
            AttrsItemRequest(
                **{
                    "id": "uranium-fuel-cell",
                    "items": {
                        "in_inventory": [{"inventory": 1, "stack": 0, "count": 50}],
                        "grid_count": 0,
                    },
                }
            )
        ]

        # TODO: reimplment
        # with pytest.warns(FuelCapacityWarning):
        #     reactor.set_item_request("uranium-fuel-cell", 100, slot=0)
        # assert reactor.items == [
        #     ItemRequest(**{
        #         "id": "uranium-fuel-cell",
        #         "items": {
        #             "in_inventory": [{"inventory": 1, "stack": 0, "count": 100}],
        #             "grid_count": 0
        #         }
        #     })
        # ]

        # TODO: reimplement
        # with pytest.warns(FuelLimitationWarning):
        #     reactor.items = [
        #         {
        #             "id": {"name": "coal"},
        #             "items": {
        #                 "in_inventory": [{"inventory": 1, "stack": 0, "count": 50}],
        #                 "grid_count": 0,
        #             },
        #         }
        #     ]
        # assert reactor.items == [
        #     AttrsItemRequest(
        #         **{
        #             "id": {"name": "coal"},
        #             "items": {
        #                 "in_inventory": [{"inventory": 1, "stack": 0, "count": 50}],
        #                 "grid_count": 0,
        #             },
        #         }
        #     )
        # ]

        # with pytest.warns(ItemLimitationWarning): # TODO: reimplement
        #     reactor.items = reactor.items = [{
        #         "id": {"name": "iron-plate"},
        #         "items": {
        #             "in_inventory": [{"inventory": 1, "stack": 0, "count": 100}],
        #             "grid_count": 0
        #         }
        #     }]
        # assert reactor.items == [ItemRequest(**{
        #     "id": {"name": "iron-plate"},
        #     "items": {
        #         "in_inventory": [{"inventory": 1, "stack": 0, "count": 50}],
        #         "grid_count": 0
        #     }
        # })]

    def test_mergable_with(self):
        reactor1 = Reactor("nuclear-reactor")
        reactor2 = Reactor("nuclear-reactor", tags={"some": "stuff"})

        assert reactor1.mergable_with(reactor1)

        assert reactor1.mergable_with(reactor2)
        assert reactor2.mergable_with(reactor1)

        reactor2.tile_position = (1, 1)
        assert not reactor1.mergable_with(reactor2)

    def test_merge(self):
        reactor1 = Reactor("nuclear-reactor")
        reactor2 = Reactor("nuclear-reactor", tags={"some": "stuff"})

        reactor1.merge(reactor2)
        del reactor2

        assert reactor1.tags == {"some": "stuff"}

    def test_eq(self):
        reactor1 = Reactor("nuclear-reactor")
        reactor2 = Reactor("nuclear-reactor")

        assert reactor1 == reactor2

        reactor1.tags = {"some": "stuff"}

        assert reactor1 != reactor2

        container = Container()

        assert reactor1 != container
        assert reactor2 != container

        # hashable
        assert isinstance(reactor1, Hashable)
