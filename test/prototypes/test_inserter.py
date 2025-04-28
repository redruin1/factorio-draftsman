# test_inserter.py

from draftsman.constants import (
    Direction,
    InserterReadMode,
    ValidationMode,
    InserterModeOfOperation,
)
from draftsman.entity import Inserter, inserters, Container
from draftsman.error import DataFormatError, IncompleteSignalError
from draftsman.signatures import AttrsSignalID
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownKeywordWarning,
    UnknownSignalWarning,
)

from collections.abc import Hashable
import pytest


class TestInserter:
    def test_constructor_init(self):
        # Valid
        inserter = Inserter(
            "inserter",
            direction=Direction.EAST,
            tile_position=[1, 1],
            override_stack_size=1,
            circuit_set_stack_size=True,
            stack_size_control_signal="signal-A",
            circuit_enabled=True,
            connect_to_logistic_network=True,
            read_hand_contents=True,
            read_mode=InserterReadMode.PULSE,
        )
        assert inserter.to_dict() == {
            "name": "inserter",
            "position": {"x": 1.5, "y": 1.5},
            "direction": Direction.EAST,
            "override_stack_size": 1,
            "control_behavior": {
                "circuit_set_stack_size": True,
                "stack_control_input_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                },
                "circuit_enabled": True,
                # "circuit_condition": {}, # Default
                "connect_to_logistic_network": True,
                # "logistic_condition": {}, # Default
                "circuit_read_hand_contents": True,
                # "circuit_hand_read_mode": InserterReadMode.PULSE,  # Default
            },
        }

        inserter = Inserter(
            "inserter",
            stack_size_control_signal={"name": "signal-A", "type": "virtual"}
        )
        assert inserter.to_dict() == {
            "name": "inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "stack_control_input_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                }
            },
        }

        # Warnings
        with pytest.warns(UnknownEntityWarning):
            Inserter("this is not an inserter").validate().reissue_all()

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            Inserter("inserter", id=25).validate().reissue_all()

        with pytest.raises(DataFormatError):
            Inserter("inserter", position=TypeError).validate().reissue_all()

        with pytest.raises(DataFormatError):
            Inserter("inserter", direction="incorrect").validate().reissue_all()

        with pytest.raises(DataFormatError):
            Inserter(
                "inserter", override_stack_size="incorrect"
            ).validate().reissue_all()

        with pytest.raises(DataFormatError):
            Inserter("inserter", tags="incorrect").validate().reissue_all()

    def test_set_spoil_priority(self):
        inserter = Inserter("stack-inserter")
        assert inserter.spoil_priority == None

        inserter.spoil_priority = "spoiled-first"
        assert inserter.spoil_priority == "spoiled-first"
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "spoil_priority": "spoiled-first",
        }

        inserter.spoil_priority = "fresh-first"
        assert inserter.spoil_priority == "fresh-first"
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "spoil_priority": "fresh-first",
        }

        with pytest.raises(DataFormatError):
            inserter.spoil_priority = "incorrect"

        inserter.validate_assignment = "none"
        assert inserter.validate_assignment == ValidationMode.NONE
        inserter.spoil_priority = "incorrect"
        assert inserter.spoil_priority == "incorrect"
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "spoil_priority": "incorrect",
        }

    def test_set_read_contents(self):
        inserter = Inserter("inserter")
        assert inserter.read_hand_contents == False
        assert inserter.to_dict() == {
            "name": "inserter",
            "position": {"x": 0.5, "y": 0.5},
        }

        inserter.read_hand_contents = True
        assert inserter.read_hand_contents == True
        assert inserter.to_dict() == {
            "name": "inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_read_hand_contents": True},
        }

        with pytest.raises(DataFormatError):
            inserter.read_hand_contents = "incorrect"
        assert inserter.read_hand_contents == True

        inserter.validate_assignment = "none"
        assert inserter.validate_assignment == ValidationMode.NONE

        inserter.read_hand_contents = "incorrect"
        assert inserter.read_hand_contents == "incorrect"
        assert inserter.to_dict() == {
            "name": "inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_read_hand_contents": "incorrect"},
        }

    def test_set_read_mode(self):
        inserter = Inserter("inserter")
        assert inserter.read_mode == InserterReadMode.PULSE
        assert inserter.to_dict() == {
            "name": "inserter",
            "position": {"x": 0.5, "y": 0.5},
        }

        inserter.read_mode = InserterReadMode.HOLD
        assert inserter.read_mode == InserterReadMode.HOLD
        assert inserter.to_dict() == {
            "name": "inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_hand_read_mode": InserterReadMode.HOLD},
        }

    # 1.0
    # def test_mode_of_operation(self):
    #     inserter = Inserter("inserter")
    #     assert inserter.mode_of_operation == None
    #     assert inserter.to_dict() == {
    #         "name": "inserter",
    #         "position": {"x": 0.5, "y": 0.5},
    #     }

    #     # Set int
    #     inserter.mode_of_operation = 0
    #     assert inserter.mode_of_operation == InserterModeOfOperation.ENABLE_DISABLE
    #     assert inserter.to_dict() == {
    #         "name": "inserter",
    #         "position": {"x": 0.5, "y": 0.5},
    #         "control_behavior": {"circuit_mode_of_operation": 0},
    #     }

    #     # Set enum
    #     inserter.mode_of_operation = InserterModeOfOperation.READ_HAND_CONTENTS
    #     assert inserter.mode_of_operation == InserterModeOfOperation.READ_HAND_CONTENTS
    #     assert inserter.to_dict() == {
    #         "name": "inserter",
    #         "position": {"x": 0.5, "y": 0.5},
    #         "control_behavior": {"circuit_mode_of_operation": 2},
    #     }

    #     # Set int out of enum range
    #     with pytest.raises(DataFormatError):
    #         inserter.mode_of_operation = 5

    #     # Turn off validation
    #     inserter.validate_assignment = "none"
    #     assert inserter.validate_assignment == ValidationMode.NONE
    #     inserter.mode_of_operation = 5
    #     assert inserter.mode_of_operation == 5
    #     assert inserter.to_dict() == {
    #         "name": "inserter",
    #         "position": {"x": 0.5, "y": 0.5},
    #         "control_behavior": {"circuit_mode_of_operation": 5},
    #     }

    def test_set_circuit_filters(self):
        inserter = Inserter("stack-inserter")
        assert inserter.circuit_set_filters == False
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
        }

        inserter.circuit_set_filters = True
        assert inserter.circuit_set_filters == True
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_set_filters": True},
        }

        with pytest.raises(DataFormatError):
            inserter.circuit_set_filters = "incorrect"

        inserter.validate_assignment = "none"
        assert inserter.validate_assignment == ValidationMode.NONE
        inserter.circuit_set_filters = "incorrect"
        assert inserter.circuit_set_filters == "incorrect"
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_set_filters": "incorrect"},
        }

    def test_set_circuit_set_stack_size(self):
        inserter = Inserter("stack-inserter")
        assert inserter.circuit_set_stack_size == False
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
        }

        inserter.circuit_set_stack_size = True
        assert inserter.circuit_set_stack_size == True
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_set_stack_size": True},
        }

        with pytest.raises(DataFormatError):
            inserter.circuit_set_stack_size = "incorrect"

        inserter.validate_assignment = "none"
        assert inserter.validate_assignment == ValidationMode.NONE
        inserter.circuit_set_stack_size = "incorrect"
        assert inserter.circuit_set_stack_size == "incorrect"
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"circuit_set_stack_size": "incorrect"},
        }

    def test_set_stack_size_control_signal(self):
        inserter = Inserter("stack-inserter")
        assert inserter.stack_size_control_signal == None

        # Shorthand
        inserter.stack_size_control_signal = "signal-S"
        assert inserter.stack_size_control_signal == AttrsSignalID(
            name="signal-S", type="virtual"
        )
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "stack_control_input_signal": {"name": "signal-S", "type": "virtual"}
            },
        }

        # Longhand
        inserter.stack_size_control_signal = {"name": "signal-S", "type": "virtual"}
        assert inserter.stack_size_control_signal == AttrsSignalID(
            name="signal-S", type="virtual"
        )
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {
                "stack_control_input_signal": {"name": "signal-S", "type": "virtual"}
            },
        }

        # Unrecognized shorthand
        with pytest.raises(IncompleteSignalError):
            inserter.stack_size_control_signal = "unknown"
        assert inserter.stack_size_control_signal == AttrsSignalID(
            name="signal-S", type="virtual"
        )

        # Unrecognized longhand
        with pytest.warns(UnknownSignalWarning):
            inserter.stack_size_control_signal = {"name": "unknown", "type": "item"}
            assert inserter.stack_size_control_signal == AttrsSignalID(
                name="unknown", type="item"
            )
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "control_behavior": {"stack_control_input_signal": {"name": "unknown", "type": "item"}},
        }

        with pytest.raises(DataFormatError):
            inserter.stack_size_control_signal = ["very", "wrong"]

    def test_custom_hand_positions(self):
        inserter = Inserter("stack-inserter")

        inserter.pickup_position = [0, -2]
        assert inserter.pickup_position == [0, -2]
        inserter.drop_position = [0, 2]
        assert inserter.drop_position == [0, 2]
        assert inserter.to_dict() == {
            "name": "stack-inserter",
            "position": {"x": 0.5, "y": 0.5},
            "pickup_position": [0.0, -2.0],
            "drop_position": [0.0, 2.0],
        }

    def test_power_and_circuit_flags(self):
        for name in inserters:
            inserter = Inserter(name)
            assert inserter.power_connectable == False
            assert inserter.dual_power_connectable == False
            assert inserter.circuit_connectable == True
            assert inserter.dual_circuit_connectable == False

    def test_mergable_with(self):
        inserter1 = Inserter("inserter")
        inserter2 = Inserter("inserter", override_stack_size=1, tags={"some": "stuff"})
        assert inserter1.mergable_with(inserter1)

        assert inserter1.mergable_with(inserter2)
        assert inserter2.mergable_with(inserter1)

        inserter2.tile_position = (1, 1)
        assert not inserter1.mergable_with(inserter2)

        inserter2.tile_position = (0, 0)
        inserter2.direction = Direction.EAST
        assert not inserter1.mergable_with(inserter2)

        inserter2 = Inserter("fast-inserter")
        assert not inserter1.mergable_with(inserter2)

    def test_merge(self):
        inserter1 = Inserter("inserter")
        inserter2 = Inserter("inserter", override_stack_size=1, tags={"some": "stuff"})

        inserter1.merge(inserter2)
        del inserter2

        assert inserter1.override_stack_size == 1
        assert inserter1.tags == {"some": "stuff"}

    def test_eq(self):
        inserter1 = Inserter("inserter")
        inserter2 = Inserter("inserter")

        assert inserter1 == inserter2

        inserter1.tags = {"some": "stuff"}

        assert inserter1 != inserter2

        container = Container()

        assert inserter1 != container
        assert inserter2 != container

        # hashable
        assert isinstance(inserter1, Hashable)
