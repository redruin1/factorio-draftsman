# test_transport_belt.py

from draftsman.constants import Direction, ReadMode
from draftsman.entity import TransportBelt, transport_belts, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


class TestTransportBelt:
    def test_constructor_init(self):
        # Valid
        fast_belt = TransportBelt(
            "fast-transport-belt",
            tile_position=[0, 0],
            direction=Direction.EAST,
            connections={"1": {"green": [{"entity_id": 1}]}},
            control_behavior={
                "circuit_enable_disable": True,
                "circuit_condition": {
                    "first_signal": {"name": "signal-blue", "type": "virtual"},
                    "comparator": "=",
                    "second_signal": {"name": "signal-blue", "type": "virtual"},
                },
                "connect_to_logistic_network": True,
                "logistic_condition": {
                    "first_signal": {
                        "name": "fast-underground-belt",
                        "type": "item",
                    },
                    "comparator": ">=",
                    "constant": 0,
                },
                "circuit_read_hand_contents": False,
                "circuit_contents_read_mode": ReadMode.HOLD,
            },
        )

        assert fast_belt.to_dict() == {
            "name": "fast-transport-belt",
            "direction": Direction.EAST,
            "position": {"x": 0.5, "y": 0.5},
            "connections": {"1": {"green": [{"entity_id": 1}]}},
            "control_behavior": {
                "circuit_enable_disable": True,
                "circuit_condition": {
                    "first_signal": {"name": "signal-blue", "type": "virtual"},
                    "comparator": "=",
                    "second_signal": {"name": "signal-blue", "type": "virtual"},
                },
                "connect_to_logistic_network": True,
                "logistic_condition": {
                    "first_signal": {
                        "name": "fast-underground-belt",
                        "type": "item",
                    },
                    "comparator": "≥",
                    # "constant": 0, # Default
                },
                "circuit_read_hand_contents": False,
                "circuit_contents_read_mode": ReadMode.HOLD,
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            temp = TransportBelt("fast-transport-belt", invalid_param=100)

        with pytest.warns(UnknownEntityWarning):
            TransportBelt("this is not a storage tank")

        # Errors
        with pytest.raises(TypeError):
            TransportBelt("transport-belt", id=25)

        with pytest.raises(TypeError):
            TransportBelt("transport-belt", position=TypeError)

        with pytest.raises(DataFormatError):
            TransportBelt("transport-belt", direction="incorrect")

        with pytest.raises(DataFormatError):
            TransportBelt("transport-belt", connections=["very", "wrong"])

        with pytest.raises(DataFormatError):
            TransportBelt(
                "transport-belt",
                control_behavior=["also", "very", "wrong"],
            )

    def test_power_and_circuit_flags(self):
        for transport_belt in transport_belts:
            belt = TransportBelt(transport_belt)
            assert belt.power_connectable == False
            assert belt.dual_power_connectable == False
            assert belt.circuit_connectable == True
            assert belt.dual_circuit_connectable == False

    def test_mergable_with(self):
        belt1 = TransportBelt("fast-transport-belt")
        belt2 = TransportBelt(
            "fast-transport-belt",
            control_behavior={
                "circuit_enable_disable": True,
                "circuit_condition": {
                    "first_signal": "signal-blue",
                    "comparator": "=",
                    "second_signal": "signal-blue",
                },
                "connect_to_logistic_network": True,
                "logistic_condition": {
                    "first_signal": "fast-underground-belt",
                    "comparator": ">=",
                    "constant": 0,
                },
                "circuit_read_hand_contents": False,
                "circuit_contents_read_mode": ReadMode.HOLD,
            },
            tags={"some": "stuff"},
        )

        assert belt1.mergable_with(belt1)

        assert belt1.mergable_with(belt2)
        assert belt2.mergable_with(belt1)

        belt2.tile_position = (1, 1)
        assert not belt1.mergable_with(belt2)

    def test_merge(self):
        belt1 = TransportBelt("fast-transport-belt")
        belt2 = TransportBelt(
            "fast-transport-belt",
            control_behavior={
                "circuit_enable_disable": True,
                "circuit_condition": {
                    "first_signal": {"name": "signal-blue", "type": "virtual"},
                    "comparator": "=",
                    "second_signal": {"name": "signal-blue", "type": "virtual"},
                },
                "connect_to_logistic_network": True,
                "logistic_condition": {
                    "first_signal": {
                        "name": "fast-underground-belt",
                        "type": "item",
                    },
                    "comparator": ">=",
                    "constant": 0,
                },
                "circuit_read_hand_contents": False,
                "circuit_contents_read_mode": ReadMode.HOLD,
            },
            tags={"some": "stuff"},
        )

        belt1.merge(belt2)
        del belt2

        assert belt1.to_dict()["control_behavior"] == {
            "circuit_enable_disable": True,
            "circuit_condition": {
                "first_signal": {"name": "signal-blue", "type": "virtual"},
                "comparator": "=",
                "second_signal": {"name": "signal-blue", "type": "virtual"},
            },
            "connect_to_logistic_network": True,
            "logistic_condition": {
                "first_signal": {
                    "name": "fast-underground-belt",
                    "type": "item",
                },
                "comparator": "≥",
                # "constant": 0, # Default
            },
            "circuit_read_hand_contents": False,
            "circuit_contents_read_mode": ReadMode.HOLD,
        }
        assert belt1.tags == {"some": "stuff"}

    def test_eq(self):
        belt1 = TransportBelt("transport-belt")
        belt2 = TransportBelt("transport-belt")

        assert belt1 == belt2

        belt1.tags = {"some": "stuff"}

        assert belt1 != belt2

        container = Container()

        assert belt1 != container
        assert belt2 != container

        # hashable
        assert isinstance(belt1, Hashable)
