# test_offshore_pump.py

from draftsman.constants import Direction, ValidationMode
from draftsman.entity import OffshorePump, offshore_pumps, Container
from draftsman.error import DataFormatError
from draftsman.signatures import (
    Condition,
    SignalID,
)
import draftsman.validators
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_offshore_pump():
    if len(offshore_pumps) == 0:
        return None
    return OffshorePump(
        "offshore-pump",
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


class TestOffshorePump:
    def test_constructor_init(self):
        pump = OffshorePump()

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            OffshorePump("not a heat pipe").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            OffshorePump(tags="incorrect").validate().reissue_all()

    def test_tile_width_height(self):
        splitter = OffshorePump()
        assert splitter.tile_width == 1
        assert splitter.tile_height == 1
        assert splitter.static_tile_width == 1
        assert splitter.static_tile_height == 1

        splitter.direction = Direction.EAST
        assert splitter.tile_width == 1
        assert splitter.tile_height == 1
        assert splitter.static_tile_width == 1
        assert splitter.static_tile_height == 1

    def test_set_circuit_condition(self):
        pump = OffshorePump("offshore-pump")

        pump.set_circuit_condition("iron-ore", ">", 1000)
        assert pump.circuit_condition == Condition(
            first_signal="iron-ore", comparator=">", constant=1000
        )
        assert pump.circuit_condition.first_signal == SignalID(
            name="iron-ore", type="item"
        )
        assert pump.to_dict() == {
            "name": "offshore-pump",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "circuit_condition": {
                    "first_signal": {"name": "iron-ore", "type": "item"},
                    "comparator": ">",
                    "constant": 1000,
                }
            },
        }

        pump.set_circuit_condition("iron-ore", ">=", "copper-ore")
        assert pump.circuit_condition == Condition(
            first_signal="iron-ore", comparator=">=", second_signal="copper-ore"
        )
        assert pump.to_dict() == {
            "name": "offshore-pump",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "circuit_condition": {
                    "first_signal": {"name": "iron-ore", "type": "item"},
                    "comparator": "≥",
                    "second_signal": {"name": "copper-ore", "type": "item"},
                }
            },
        }

        # pump.remove_circuit_condition()
        # assert pump.control_behavior.circuit_condition == None

    def test_connect_to_logistic_network(self):
        pump = OffshorePump("offshore-pump")
        assert pump.connect_to_logistic_network == False
        assert pump.to_dict() == {
            "name": "offshore-pump",
            "position": {"x": 0.5, "y": 0.5},
        }

        pump.connect_to_logistic_network = True
        assert pump.connect_to_logistic_network == True
        assert pump.to_dict() == {
            "name": "offshore-pump",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"connect_to_logistic_network": True},
        }

        with pytest.raises(DataFormatError):
            pump.connect_to_logistic_network = "incorrect"
        assert pump.connect_to_logistic_network == True

        with draftsman.validators.disabled():
            pump.connect_to_logistic_network = "incorrect"
            assert pump.connect_to_logistic_network == "incorrect"
            assert pump.to_dict() == {
                "name": "offshore-pump",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {"connect_to_logistic_network": "incorrect"},
            }

    def test_set_logistics_condition(self):
        pump = OffshorePump("offshore-pump")

        pump.set_logistic_condition("iron-ore", ">", 1000)
        assert pump.logistic_condition == Condition(
            first_signal="iron-ore", comparator=">", constant=1000
        )

        # pump.remove_logistic_condition()
        # assert pump.logistic_condition == None

    def test_mergable_with(self):
        pump1 = OffshorePump("offshore-pump")
        pump2 = OffshorePump("offshore-pump", tags={"some": "stuff"})

        assert pump1.mergable_with(pump1)

        assert pump1.mergable_with(pump2)
        assert pump2.mergable_with(pump1)

        pump2.tile_position = (1, 1)
        assert not pump1.mergable_with(pump2)

    def test_merge(self):
        pump1 = OffshorePump("offshore-pump")
        pump2 = OffshorePump("offshore-pump", tags={"some": "stuff"})

        pump1.merge(pump2)
        del pump2

        assert pump1.tags == {"some": "stuff"}

    def test_eq(self):
        pump1 = OffshorePump("offshore-pump")
        pump2 = OffshorePump("offshore-pump")

        assert pump1 == pump2

        pump1.tags = {"some": "stuff"}

        assert pump1 != pump2

        container = Container()

        assert pump1 != container
        assert pump2 != container

        # hashable
        assert isinstance(pump1, Hashable)
