# test_pump.py

from draftsman.entity import Pump, pumps, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestPump:
    def test_constructor_init(self):
        # pump = Pump("pump")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Pump("pump", unused_keyword=10)
        with pytest.warns(UnknownEntityWarning):
            Pump("this is not a pump")
        with pytest.warns(UnknownKeywordWarning):
            Pump(control_behavior={"unused_key": "something"})

        # Errors
        with pytest.raises(DataFormatError):
            Pump(control_behavior="incorrect")

    def test_mergable_with(self):
        pump1 = Pump("pump")
        pump2 = Pump("pump", tags={"some": "stuff"})

        assert pump1.mergable_with(pump1)

        assert pump1.mergable_with(pump2)
        assert pump2.mergable_with(pump1)

        pump2.tile_position = (1, 1)
        assert not pump1.mergable_with(pump2)

    def test_merge(self):
        pump1 = Pump("pump")
        pump2 = Pump("pump", tags={"some": "stuff"})

        pump1.merge(pump2)
        del pump2

        assert pump1.tags == {"some": "stuff"}

    def test_eq(self):
        pump1 = Pump("pump")
        pump2 = Pump("pump")

        assert pump1 == pump2

        pump1.tags = {"some": "stuff"}

        assert pump1 != pump2

        container = Container()

        assert pump1 != container
        assert pump2 != container

        # hashable
        assert isinstance(pump1, Hashable)
