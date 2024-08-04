# test_offshore_pump.py

from draftsman.constants import ValidationMode
from draftsman.entity import OffshorePump, offshore_pumps, Container
from draftsman.error import DataFormatError
from draftsman.signatures import Condition
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestOffshorePump:
    def test_constructor_init(self):
        pump = OffshorePump()

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            OffshorePump(unused_keyword="whatever").validate().reissue_all()
        with pytest.warns(UnknownKeywordWarning):
            OffshorePump(control_behavior={"unused_key": "something"}).validate().reissue_all()
        with pytest.warns(UnknownEntityWarning):
            OffshorePump("not a heat pipe").validate().reissue_all()

        # Errors
        with pytest.raises(DataFormatError):
            OffshorePump(control_behavior="incorrect").validate().reissue_all()

    def test_control_behavior(self):
        pump = OffshorePump("offshore-pump")

        with pytest.raises(DataFormatError):
            pump.control_behavior = "incorrect"

        pump.validate_assignment = "none"
        assert pump.validate_assignment == ValidationMode.NONE

        pump.control_behavior = "incorrect"
        assert pump.control_behavior == "incorrect"
        assert pump.to_dict() == {
            "name": "offshore-pump",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": "incorrect",
        }

    def test_set_circuit_condition(self):
        pump = OffshorePump("offshore-pump")

        pump.set_circuit_condition("iron-ore", ">", 1000)
        assert pump.control_behavior.circuit_condition == Condition(
            **{"first_signal": "iron-ore", "comparator": ">", "constant": 1000}
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
        assert pump.control_behavior.circuit_condition == Condition(
            **{
                "first_signal": "iron-ore",
                "comparator": ">=",
                "second_signal": "copper-ore",
            }
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

        pump.remove_circuit_condition()
        assert pump.control_behavior.circuit_condition == None

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

        pump.connect_to_logistic_network = None
        assert pump.connect_to_logistic_network == None
        assert pump.to_dict() == {
            "name": "offshore-pump",
            "position": {"x": 0.5, "y": 0.5},
        }

        with pytest.raises(DataFormatError):
            pump.connect_to_logistic_network = "incorrect"
        assert pump.connect_to_logistic_network == None

        pump.validate_assignment = "none"
        assert pump.validate_assignment == ValidationMode.NONE

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
        assert pump.control_behavior.logistic_condition == Condition(
            **{"first_signal": "iron-ore", "comparator": ">", "constant": 1000}
        )

        pump.remove_logistic_condition()
        assert pump.control_behavior.logistic_condition == None

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
