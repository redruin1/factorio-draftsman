# test_transport_belt.py

from draftsman.constants import Direction, BeltReadMode, ValidationMode
from draftsman.entity import TransportBelt, transport_belts, Container
from draftsman.error import DataFormatError
from draftsman.signatures import Condition
import draftsman.validators
from draftsman.warning import UnknownEntityWarning, UnknownKeywordWarning

from collections.abc import Hashable
import pytest


@pytest.fixture
def valid_transport_belt():
    return TransportBelt(
        "transport-belt",
        id="test",
        quality="uncommon",
        tile_position=(1, 1),
        direction=Direction.EAST,
        circuit_enabled=True,
        circuit_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        connect_to_logistic_network=True,
        logistic_condition=Condition(
            first_signal="signal-A", comparator="<", second_signal="signal-B"
        ),
        read_contents=True,
        read_mode=BeltReadMode.HOLD,
        tags={"blah": "blah"},
    )


class TestTransportBelt:
    def test_constructor_init(self):
        # Valid
        fast_belt = TransportBelt.from_dict(
            {
                "name": "fast-transport-belt",
                "direction": Direction.EAST,
                "control_behavior": {
                    "circuit_enabled": True,
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
                    "circuit_read_hand_contents": True,
                    "circuit_contents_read_mode": BeltReadMode.HOLD,
                },
            }
        )

        assert fast_belt.to_dict() == {
            "name": "fast-transport-belt",
            "direction": Direction.EAST,
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "circuit_enabled": True,
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
                "circuit_read_hand_contents": True,
                "circuit_contents_read_mode": BeltReadMode.HOLD,
            },
        }

        # Warnings
        with pytest.warns(UnknownKeywordWarning):
            TransportBelt.from_dict(
                {"name": "fast-transport-belt", "invalid_param": 100}
            )

        with pytest.warns(UnknownEntityWarning):
            TransportBelt("this is not a storage tank")

        # Errors
        with pytest.raises(TypeError):
            TransportBelt("transport-belt", id=25)

        with pytest.raises(DataFormatError):
            TransportBelt("transport-belt", position=TypeError)

        with pytest.raises(DataFormatError):
            TransportBelt("transport-belt", direction="incorrect")

        with pytest.raises(DataFormatError):
            TransportBelt(
                "transport-belt",
                tags=["also", "very", "wrong"],
            )

    def test_power_and_circuit_flags(self):
        for transport_belt in transport_belts:
            belt = TransportBelt(transport_belt)
            assert belt.power_connectable == False
            assert belt.dual_power_connectable == False
            assert belt.circuit_connectable == True
            assert belt.dual_circuit_connectable == False

    def test_set_circuit_enabled(self):
        belt = TransportBelt("transport-belt")
        assert belt.circuit_enabled == False  # Default
        assert belt.to_dict() == {
            "name": "transport-belt",
            "position": {"x": 0.5, "y": 0.5},
        }

        belt.circuit_enabled = True
        assert belt.circuit_enabled == True
        assert belt.to_dict() == {
            "name": "transport-belt",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_enabled": True},
        }

        with pytest.raises(DataFormatError):
            belt.circuit_enabled = "incorrect"
        assert belt.circuit_enabled == True

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            belt.circuit_enabled = "incorrect"
            assert belt.circuit_enabled == "incorrect"
            assert belt.to_dict() == {
                "name": "transport-belt",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {"circuit_enabled": "incorrect"},
            }

    def test_set_read_contents(self):
        belt = TransportBelt("transport-belt")
        assert belt.read_contents == False
        assert belt.to_dict() == {
            "name": "transport-belt",
            "position": {"x": 0.5, "y": 0.5},
        }

        belt.read_contents = True
        assert belt.read_contents == True
        assert belt.to_dict() == {
            "name": "transport-belt",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_read_hand_contents": True},
        }

        with pytest.raises(DataFormatError):
            belt.read_contents = "incorrect"
        assert belt.read_contents == True

        with draftsman.validators.set_mode(ValidationMode.DISABLED):
            belt.read_contents = "incorrect"
            assert belt.read_contents == "incorrect"
            assert belt.to_dict() == {
                "name": "transport-belt",
                "position": {"x": 0.5, "y": 0.5},
                "control_behavior": {"circuit_read_hand_contents": "incorrect"},
            }

    def test_set_read_mode(self):
        belt = TransportBelt("transport-belt")
        assert belt.read_mode == BeltReadMode.PULSE
        assert belt.to_dict() == {
            "name": "transport-belt",
            "position": {"x": 0.5, "y": 0.5},
        }
        belt.read_mode = BeltReadMode.HOLD
        assert belt.read_mode == BeltReadMode.HOLD
        assert belt.to_dict() == {
            "name": "transport-belt",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_contents_read_mode": BeltReadMode.HOLD},
        }

        with pytest.raises(ValueError):
            belt.read_mode = "incorrect"
        assert belt.read_mode == BeltReadMode.HOLD

    def test_mergable_with(self):
        belt1 = TransportBelt("fast-transport-belt")
        belt2 = TransportBelt.from_dict(
            {
                "name": "fast-transport-belt",
                "control_behavior": {
                    "circuit_enabled": True,
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
                        "constant": 0,
                    },
                    "circuit_read_hand_contents": False,
                    "circuit_contents_read_mode": BeltReadMode.HOLD,
                },
                "tags": {"some": "stuff"},
            }
        )

        assert belt1.mergable_with(belt1)

        assert belt1.mergable_with(belt2)
        assert belt2.mergable_with(belt1)

        belt2.tile_position = (1, 1)
        assert not belt1.mergable_with(belt2)

    def test_merge(self):
        belt1 = TransportBelt("fast-transport-belt")
        belt2 = TransportBelt.from_dict(
            {
                "name": "fast-transport-belt",
                "control_behavior": {
                    "circuit_enabled": True,
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
                        "constant": 0,
                    },
                    "circuit_read_hand_contents": True,
                    "circuit_contents_read_mode": BeltReadMode.HOLD,
                },
                "tags": {"some": "stuff"},
            }
        )

        print(belt2)

        belt1.merge(belt2)
        del belt2

        print(belt1.to_dict(exclude_defaults=False))

        assert belt1.to_dict()["name"] == "fast-transport-belt"
        assert belt1.to_dict()["control_behavior"] == {
            "circuit_enabled": True,
            "circuit_condition": {
                "first_signal": {"name": "signal-blue", "type": "virtual"},
                "comparator": "=",
                "second_signal": {"name": "signal-blue", "type": "virtual"},
            },
            "connect_to_logistic_network": True,
            "logistic_condition": {
                "first_signal": {"name": "fast-underground-belt", "type": "item"},
                "comparator": "≥",
                # "constant": 0, # Default
            },
            "circuit_read_hand_contents": True,
            "circuit_contents_read_mode": BeltReadMode.HOLD,
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
