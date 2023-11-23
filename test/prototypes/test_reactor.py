# test_reactor.py

from draftsman.entity import Reactor, reactors, Container
from draftsman.error import DataFormatError
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
            Reactor("nuclear-reactor", unused_keyword="whatever")
        with pytest.warns(UnknownEntityWarning):
            Reactor("not a reactor")

    def test_set_fuel_request(self):
        reactor = Reactor("nuclear-reactor")
        assert reactor.allowed_fuel_items == {"uranium-fuel-cell"}
        assert reactor.total_fuel_slots == 1

        reactor.set_item_request("uranium-fuel-cell", 50)
        assert reactor.items == {"uranium-fuel-cell": 50}

        with pytest.warns(FuelCapacityWarning):
            reactor.set_item_request("uranium-fuel-cell", 100)
        assert reactor.items == {"uranium-fuel-cell": 100}

        with pytest.warns(FuelLimitationWarning):
            reactor.items = {"coal": 50}
        assert reactor.items == {"coal": 50}

        with pytest.warns(ItemLimitationWarning):
            reactor.items = {"iron-plate": 100}
        assert reactor.items == {"iron-plate": 100}

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
