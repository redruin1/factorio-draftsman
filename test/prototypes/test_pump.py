# test_pump.py

from draftsman.constants import Direction
from draftsman.entity import Pump, pumps, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.signatures import Condition
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_pump():
    return Pump(
        "pump",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        circuit_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        connect_to_logistic_network=True,
        logistic_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        tags={"blah": "blah"},
    )


class TestPump:
    def test_constructor_init(self):
        # pump = Pump("pump")

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            Pump.from_dict(
                {"name": "pump", "unused_keyword": 10}
            ).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            Pump("this is not a pump").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            Pump(tags="incorrect").validate().reissue_all()

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
