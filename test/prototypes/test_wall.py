# test_wall.py

from draftsman.entity import Wall, Container
from draftsman.error import DataFormatError
from draftsman.signatures import SignalID
from draftsman.warning import MalformedSignalWarning, UnknownEntityWarning, UnknownKeywordWarning, UnknownSignalWarning
from draftsman.constants import ValidationMode as vm

from collections.abc import Hashable
import pytest


class TestWall:
    def test_constructor_init(self):
        # ========================
        # No assignment validation
        # ========================

        # Known entity
        wall = Wall("stone-wall", validate=vm.NONE)
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5}
        }

        # Unkown entity
        wall = Wall("unknown-wall", validate=vm.NONE)
        assert wall.to_dict() == {
            "name": "unknown-wall",
            "position": {"x": 0.0, "y": 0.0}
        }

        # Unknown keyword
        wall = Wall("stone-wall", unused_keyword="whatever", validate=vm.NONE)
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "unused_keyword": "whatever"
        }

        # Import from correct dictionary
        wall = Wall(
            "stone-wall",
            connections={
                "1": {
                    "red": [{"entity_id": 2, "circuit_id": 1}]
                }
            },
            control_behavior={
                "circuit_open_gate": True,
                "circuit_condition": {
                    "first_signal": "signal-A",
                    "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": "signal-B"
            },
            tags={"some": "stuff"},
            validate=vm.NONE
        )
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {
                "1": {
                    "red": [{"entity_id": 2, "circuit_id": 1}]
                }
            },
            "control_behavior": {
                "circuit_open_gate": True, # Default included because not a known internal type
                "circuit_condition": {
                    "first_signal": "signal-A",
                    "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": "signal-B"
            },
            "tags": {"some": "stuff"},
        }

        # Import from incorrect dictionary
        wall = Wall(
            "stone-wall",
            connections="incorrect",
            control_behavior="incorrect",
            validate=vm.NONE,
        )
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": "incorrect",
            "control_behavior": "incorrect"
        }

        # ===================
        # Miniumum validation
        # ===================

        # Known entity
        wall = Wall("stone-wall", validate=vm.MINIMUM)
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5}
        }

        # Unkown entity
        wall = Wall("unknown-wall", validate=vm.MINIMUM)
        assert wall.to_dict() == {
            "name": "unknown-wall",
            "position": {"x": 0.0, "y": 0.0}
        }

        # Unknown keyword
        wall = Wall("stone-wall", unused_keyword="whatever", validate=vm.MINIMUM)
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "unused_keyword": "whatever"
        }

        # Import from correct dictionary
        wall = Wall(
            "stone-wall",
            connections={
                "1": {
                    "red": [{"entity_id": 2, "circuit_id": 1}]
                }
            },
            control_behavior={
                "circuit_open_gate": True,
                "circuit_condition": {
                    "first_signal": "signal-A",
                    "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": "signal-B"
            },
            tags={"some": "stuff"},
            validate=vm.MINIMUM
        )
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {
                "1": {
                    "red": [{"entity_id": 2, "circuit_id": 1}]
                }
            },
            "control_behavior": {
                # "circuit_open_gate": True, # Default excluded because stripped
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    # "comparator": "<", # Default
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
            "tags": {"some": "stuff"},
        }

        # Import from incorrect dictionary
        with pytest.raises(DataFormatError):
            wall = Wall(
                "stone-wall",
                connections="incorrect",
                control_behavior="incorrect",
                validate=vm.MINIMUM,
            )

        # =================
        # Strict validation
        # =================

        # Known entity
        wall = Wall("stone-wall", validate=vm.STRICT)
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5}
        }

        # Unkown entity
        with pytest.warns(UnknownEntityWarning):
            wall = Wall("unknown-wall", validate=vm.STRICT)
        assert wall.to_dict() == {
            "name": "unknown-wall",
            "position": {"x": 0.0, "y": 0.0}
        }

        # Unknown keyword
        with pytest.warns(UnknownKeywordWarning):
            wall = Wall("stone-wall", unused_keyword="whatever", validate=vm.STRICT)
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "unused_keyword": "whatever"
        }

        # Import from correct dictionary
        wall = Wall(
            "stone-wall",
            connections={
                "1": {
                    "red": [{"entity_id": 2, "circuit_id": 1}]
                }
            },
            control_behavior={
                "circuit_open_gate": True,
                "circuit_condition": {
                    "first_signal": "signal-A",
                    "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": "signal-B"
            },
            tags={"some": "stuff"},
            validate=vm.STRICT
        )
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {
                "1": {
                    "red": [{"entity_id": 2, "circuit_id": 1}]
                }
            },
            "control_behavior": {
                # "circuit_open_gate": True, # Default
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    # "comparator": "<", # Default
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
            "tags": {"some": "stuff"},
        }

        # Import from incorrect dictionary
        with pytest.raises(DataFormatError):
            wall = Wall(
                "stone-wall",
                connections="incorrect",
                control_behavior="incorrect",
                validate=vm.STRICT,
            )

        # ===================
        # Pedantic validation
        # ===================

        # Known entity
        wall = Wall("stone-wall", validate=vm.PEDANTIC)
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5}
        }

        # Unkown entity
        with pytest.raises(DataFormatError):
            wall = Wall("unknown-wall", validate=vm.PEDANTIC)

        # Unknown keyword
        with pytest.raises(DataFormatError):
            wall = Wall("stone-wall", unused_keyword="whatever", validate=vm.PEDANTIC)

        # Import from correct dictionary
        wall = Wall(
            "stone-wall",
            connections={
                "1": {
                    "red": [{"entity_id": 2, "circuit_id": 1}]
                }
            },
            control_behavior={
                "circuit_open_gate": True,
                "circuit_condition": {
                    "first_signal": "signal-A",
                    "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": "signal-B"
            },
            tags={"some": "stuff"},
            validate=vm.PEDANTIC
        )
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {
                "1": {
                    "red": [{"entity_id": 2, "circuit_id": 1}]
                }
            },
            "control_behavior": {
                # "circuit_open_gate": True, # Default
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    # "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"}
            },
            "tags": {"some": "stuff"},
        }

        # Import from incorrect dictionary
        with pytest.raises(DataFormatError):
            wall = Wall(
                "stone-wall",
                connections="incorrect",
                control_behavior="incorrect",
                validate=vm.PEDANTIC,
            )

    def test_set_enable_disable(self):
        # ========================
        # No assignment validation
        # ========================
        wall = Wall("stone-wall", validate_assignment="none")

        # None
        wall.enable_disable = None
        assert wall.enable_disable == None
        assert wall.control_behavior.circuit_open_gate == None

        # bool
        wall.enable_disable = True
        assert wall.enable_disable == True
        assert wall.control_behavior.circuit_open_gate == True
        
        # Incorrect type
        wall.enable_disable = "incorrect"
        assert wall.enable_disable == "incorrect"
        assert wall.control_behavior.circuit_open_gate == "incorrect"

        # ===================
        # Miniumum validation
        # ===================
        wall.validate_assignment = "minimum"

        # None
        wall.enable_disable = None
        assert wall.enable_disable == None
        assert wall.control_behavior.circuit_open_gate == None

        # bool
        wall.enable_disable = True
        assert wall.enable_disable == True
        assert wall.control_behavior.circuit_open_gate == True
        
        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.enable_disable = "incorrect"

        # =================
        # Strict validation
        # =================
        wall.validate_assignment = "strict"

        # None
        wall.enable_disable = None
        assert wall.enable_disable == None
        assert wall.control_behavior.circuit_open_gate == None

        # bool
        wall.enable_disable = True
        assert wall.enable_disable == True
        assert wall.control_behavior.circuit_open_gate == True
        
        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.enable_disable = "incorrect"

        # ===================
        # Pedantic validation
        # ===================
        wall.validate_assignment = "pedantic"

        # None
        wall.enable_disable = None
        assert wall.enable_disable == None
        assert wall.control_behavior.circuit_open_gate == None

        # bool
        wall.enable_disable = True
        assert wall.enable_disable == True
        assert wall.control_behavior.circuit_open_gate == True
        
        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.enable_disable = "incorrect"


    def test_set_read_gate(self):
        # ========================
        # No assignment validation
        # ========================
        wall = Wall("stone-wall", validate_assignment="none")
        assert wall.read_gate is wall.control_behavior.circuit_read_sensor

        # None
        wall.read_gate = None
        assert wall.read_gate == None

        # bool
        wall.read_gate = True
        assert wall.read_gate == True
        
        # Incorrect type
        wall.read_gate = "incorrect"
        assert wall.read_gate == "incorrect"

        # ===================
        # Miniumum validation
        # ===================
        wall.validate_assignment = "minimum"

        # None
        wall.read_gate = None
        assert wall.read_gate == None

        # bool
        wall.read_gate = True
        assert wall.read_gate == True

        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.read_gate = "incorrect"

        # =================
        # Strict validation
        # =================
        wall.validate_assignment = "strict"

        # None
        wall.read_gate = None
        assert wall.read_gate == None

        # bool
        wall.read_gate = True
        assert wall.read_gate == True

        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.read_gate = "incorrect"

        # ===================
        # Pedantic validation
        # ===================
        wall.validate_assignment = "pedantic"

        # None
        wall.read_gate = None
        assert wall.read_gate == None

        # bool
        wall.read_gate = True
        assert wall.read_gate == True

        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.read_gate = "incorrect"



    def test_set_output_signal(self):
        # ========================
        # No assignment validation
        # ========================
        wall = Wall("stone-wall", validate_assignment="none")

        # None
        wall.output_signal = None
        assert wall.output_signal == None

        # Known string
        wall.output_signal = "signal-A"
        assert wall.output_signal == "signal-A"
        assert wall.to_dict()["control_behavior"] == {
            "output_signal": "signal-A"
        }
        
        # Known dict
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.output_signal == {"name": "signal-A", "type": "virtual"}

        # Known dict but malformed
        wall.output_signal = {"name": "signal-A", "type": "fluid"}
        assert wall.output_signal == {"name": "signal-A", "type": "fluid"}

        # Unknown string
        wall.output_signal = "unknown-signal"
        assert wall.output_signal == "unknown-signal"

        # Unknown dict
        wall.output_signal = {"name": "unknown-signal", "type": "virtual"}
        assert wall.output_signal == {"name": "unknown-signal", "type": "virtual"}

        # Incorrect Type
        wall.output_signal = DataFormatError
        assert wall.output_signal == DataFormatError

        # ===================
        # Miniumum validation
        # ===================
        wall.validate_assignment = "minimum"

        # None
        wall.output_signal = None
        assert wall.output_signal == None

        # Known string
        wall.output_signal = "signal-A"
        assert wall.output_signal == SignalID(name="signal-A", type="virtual")

        # Known dict
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.output_signal == SignalID(name="signal-A", type="virtual")

        # Known dict but malformed
        wall.output_signal = {"name": "signal-A", "type": "fluid"}
        assert wall.output_signal == SignalID(name="signal-A", type="fluid")

        # Unknown string
        with pytest.raises(DataFormatError):
            wall.output_signal = "unknown-signal"
        
        # Unknown dict
        wall.output_signal = {"name": "unknown-signal", "type": "virtual"}
        assert wall.output_signal == SignalID(name="unknown-signal", type="virtual")

        # Incorrect Type
        with pytest.raises(DataFormatError):
            wall.output_signal = DataFormatError

        # =================
        # Strict validation
        # =================
        wall.validate_assignment = "strict"

        # None
        wall.output_signal = None
        assert wall.output_signal == None

        # Known string
        wall.output_signal = "signal-A"
        assert wall.output_signal == SignalID(name="signal-A", type="virtual")

        # Known dict
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.output_signal == SignalID(name="signal-A", type="virtual")

        # Known dict but malformed
        with pytest.warns(MalformedSignalWarning):
            wall.output_signal = {"name": "signal-A", "type": "fluid"}
        assert wall.output_signal == SignalID(name="signal-A", type="fluid")

        # Unknown string
        with pytest.raises(DataFormatError):
            wall.output_signal = "unknown-signal"

        # Unknown dict
        with pytest.warns(UnknownSignalWarning):
            wall.output_signal = {"name": "unknown-signal", "type": "virtual"}
        assert wall.output_signal == SignalID(name="unknown-signal", type="virtual")

        # Incorrect Type
        with pytest.raises(DataFormatError):
            wall.output_signal = DataFormatError

        # ===================
        # Pedantic validation
        # ===================
        wall.validate_assignment = "pedantic"

        # None
        wall.output_signal = None
        assert wall.output_signal == None

        # Known string
        wall.output_signal = "signal-A"
        assert wall.output_signal == SignalID(name="signal-A", type="virtual")

        # Known dict
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.output_signal == SignalID(name="signal-A", type="virtual")

        # Known dict but malformed
        with pytest.raises(DataFormatError):
            wall.output_signal = {"name": "signal-A", "type": "fluid"}

        # Unknown string
        with pytest.raises(DataFormatError):
            wall.output_signal = "unknown-signal"

        # Unknown dict
        with pytest.raises(DataFormatError):
            wall.output_signal = {"name": "unknown-signal", "type": "virtual"}

        # Incorrect Type
        with pytest.raises(DataFormatError):
            wall.output_signal = DataFormatError        

    def test_mergable_with(self):
        wall1 = Wall("stone-wall")
        wall2 = Wall("stone-wall", tags={"some": "stuff"})

        assert wall1.mergable_with(wall1)

        assert wall1.mergable_with(wall2)
        assert wall2.mergable_with(wall1)

        wall2.tile_position = (1, 1)
        assert not wall1.mergable_with(wall2)

    def test_merge(self):
        wall1 = Wall("stone-wall")
        wall2 = Wall("stone-wall", tags={"some": "stuff"})

        wall1.merge(wall2)
        del wall2

        assert wall1.tags == {"some": "stuff"}

    def test_eq(self):
        wall1 = Wall("stone-wall")
        wall2 = Wall("stone-wall")

        assert wall1 == wall2

        wall1.tags = {"some": "stuff"}

        assert wall1 != wall2

        container = Container()

        assert wall1 != container
        assert wall2 != container

        # hashable
        assert isinstance(wall1, Hashable)
