# test_wall.py

from draftsman.entity import Wall, Container, walls
from draftsman.error import DataFormatError, IncompleteSignalError
from draftsman.signatures import AttrsSignalID
from draftsman.warning import (
    MalformedSignalWarning,
    UnknownEntityWarning,
    UnknownKeywordWarning,
    UnknownSignalWarning,
)
from draftsman.constants import ValidationMode as vm

from collections.abc import Hashable
import pytest


class TestWall:
    def test_constructor_init(self):
        # ========================
        # No assignment validation
        # ========================

        # Known entity
        wall = Wall("stone-wall")
        wall.validate(mode=vm.NONE).reissue_all()
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
        }

        # Unkown entity
        wall = Wall("unknown-wall", validate_assignment=vm.NONE)
        wall.validate(mode=vm.NONE).reissue_all()
        assert wall.to_dict() == {
            "name": "unknown-wall",
            "position": {"x": 0.0, "y": 0.0},
        }

        # Unknown keyword
        wall = Wall("stone-wall")
        with pytest.warns(UnknownKeywordWarning):
            wall.extra_keys = {"unused_keyword": "whatever"}
        wall.validate(mode=vm.NONE).reissue_all()
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "unused_keyword": "whatever",
        }

        # Import from correct dictionary
        d = {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
            "control_behavior": {
                "circuit_open_gate": True,
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"},
            },
            "tags": {"some": "stuff"},
        }
        wall = Wall.from_dict(d)
        wall.validate(mode=vm.NONE).reissue_all()
        assert wall.to_dict(version=(1, 0)) == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
            "control_behavior": {
                # "circuit_open_gate": True, # Default
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    # "comparator": "<", # Default
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"},
            },
            "tags": {"some": "stuff"},
        }

        # Import from incorrect dictionary
        # TODO: handle properly
        # wall = Wall.from_dict({
        #     "name": "stone-wall",
        #     "connections": "incorrect",
        #     "control_behavior": "incorrect",
        # })
        # wall.validate(mode=vm.NONE).reissue_all()
        # assert wall.to_dict(version=(1, 0)) == {
        #     "name": "stone-wall",
        #     "position": {"x": 0.5, "y": 0.5},
        #     "connections": "incorrect",
        #     "control_behavior": "incorrect",
        # }

        # ===================
        # Miniumum validation
        # ===================

        # Known entity
        wall = Wall("stone-wall")
        wall.validate(mode=vm.MINIMUM).reissue_all()
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
        }

        # Unkown entity
        wall = Wall("unknown-wall", validate_assignment=vm.MINIMUM)
        wall.validate(mode=vm.MINIMUM).reissue_all()
        assert wall.to_dict() == {
            "name": "unknown-wall",
            "position": {"x": 0.0, "y": 0.0},
        }

        # Unknown keyword
        wall = Wall.from_dict({"name": "stone-wall", "unused_keyword": "whatever"})
        wall.validate(mode=vm.MINIMUM).reissue_all()
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "unused_keyword": "whatever",
        }

        # Import from correct dictionary
        wall = Wall.from_dict(
            {
                "name": "stone-wall",
                "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
                "control_behavior": {
                    "circuit_open_gate": True,
                    "circuit_condition": {
                        "first_signal": {"name": "signal-A", "type": "virtual"},
                        "comparator": "<",
                        "constant": 100,
                    },
                    "circuit_read_sensor": True,
                    "output_signal": {"name": "signal-B", "type": "virtual"},
                },
                "tags": {"some": "stuff"},
            }
        )
        wall.validate(mode=vm.MINIMUM).reissue_all()
        assert wall.to_dict(version=(1, 0)) == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
            "control_behavior": {
                # "circuit_open_gate": True, # Default excluded because stripped
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    # "comparator": "<", # Default
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"},
            },
            "tags": {"some": "stuff"},
        }

        # Import from incorrect dictionary
        with pytest.raises(DataFormatError):
            wall = Wall.from_dict(
                {
                    "name": "stone-wall",
                    "tags": "incorrect"
                }
            )

        # =================
        # Strict validation
        # =================

        # Known entity
        wall = Wall("stone-wall")
        wall.validate(mode=vm.STRICT).reissue_all()
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
        }

        # Unkown entity
        with pytest.warns(UnknownEntityWarning):
            wall = Wall("unknown-wall")
            wall.validate(mode=vm.STRICT).reissue_all()
        assert wall.to_dict() == {
            "name": "unknown-wall",
            "position": {"x": 0.0, "y": 0.0},
        }

        # Unknown keyword
        with pytest.warns(UnknownKeywordWarning):
            wall = Wall.from_dict({"name": "stone-wall", "unused_keyword": "whatever"})
            wall.validate(mode=vm.STRICT).reissue_all()
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "unused_keyword": "whatever",
        }

        # Import from correct dictionary
        wall = Wall.from_dict(
            {
                "name": "stone-wall",
                "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
                "control_behavior": {
                    "circuit_open_gate": True,
                    "circuit_condition": {
                        "first_signal": {"name": "signal-A", "type": "virtual"},
                        "comparator": "<",
                        "constant": 100,
                    },
                    "circuit_read_sensor": True,
                    "output_signal": {"name": "signal-B", "type": "virtual"},
                },
                "tags": {"some": "stuff"},
            }
        )
        with pytest.warns(UnknownKeywordWarning):
            wall.validate(mode=vm.STRICT).reissue_all()
        assert wall.to_dict(version=(1, 0)) == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
            "control_behavior": {
                # "circuit_open_gate": True, # Default
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    # "comparator": "<", # Default
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"},
            },
            "tags": {"some": "stuff"},
        }

        # Import from incorrect dictionary
        with pytest.raises(DataFormatError):
            wall = Wall.from_dict(
                {
                    "name": "stone-wall",
                    "tags": "incorrect"
                }
            )

        # ===================
        # Pedantic validation
        # ===================

        # Known entity
        wall = Wall("stone-wall")
        wall.validate(mode=vm.PEDANTIC).reissue_all()
        assert wall.to_dict() == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
        }

        # Unkown entity
        with pytest.warns(UnknownEntityWarning):
            wall = Wall("unknown-wall")
            wall.validate(mode=vm.PEDANTIC).reissue_all()

        # Unknown keyword
        with pytest.warns(UnknownKeywordWarning):
            wall = Wall.from_dict({"name": "stone-wall", "unused_keyword": "whatever"})
            wall.validate(mode=vm.PEDANTIC).reissue_all()

        # Import from correct dictionary
        wall = Wall.from_dict(
            {
                "name": "stone-wall",
                "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
                "control_behavior": {
                    "circuit_open_gate": True,
                    "circuit_condition": {
                        "first_signal": {"name": "signal-A", "type": "virtual"},
                        "comparator": "<",
                        "constant": 100,
                    },
                    "circuit_read_sensor": True,
                    "output_signal": {"name": "signal-B", "type": "virtual"},
                },
                "tags": {"some": "stuff"},
            }
        )
        with pytest.warns(UnknownKeywordWarning):
            wall.validate(mode=vm.PEDANTIC).reissue_all()
        assert wall.to_dict(version=(1, 0)) == {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
            "control_behavior": {
                # "circuit_open_gate": True, # Default
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    # "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"},
            },
            "tags": {"some": "stuff"},
        }

        # Import from incorrect dictionary
        with pytest.raises(DataFormatError):
            wall = Wall.from_dict(
                {
                    "name": "stone-wall",
                    "tags": "incorrect"
                }
            )

    def test_versioning(self):
        d_1_0 = {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "connections": {"1": {"red": [{"entity_id": 2, "circuit_id": 1}]}},
            "control_behavior": {
                "circuit_open_gate": True,
                "circuit_condition": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_sensor": True,
                "output_signal": {"name": "signal-B", "type": "virtual"},
            },
            "tags": {"some": "stuff"},
        }
        d_2_0 = {
            "name": "stone-wall",
            "position": {"x": 0.5, "y": 0.5},
            "quality": "normal",
            "control_behavior": {
                "circuit_open_gate": True,
                "circuit_condition": {
                    "first_signal": {
                        "name": "signal-A",
                        "quality": "normal",
                        "type": "virtual",
                    },
                    "comparator": "<",
                    "constant": 100,
                },
                "circuit_read_gate": True,
                "output_signal": {
                    "name": "signal-B",
                    "quality": "normal", 
                    "type": "virtual",
                },
            },
            "tags": {"some": "stuff"},
        }
        # Load 1.0 dict
        wall = Wall.from_dict(d_1_0, version=(1, 0))
        assert wall.extra_keys is None
        # Output should be equivalent
        assert wall.to_dict(version=(1, 0), exclude_defaults=False) == d_1_0
        # Should be able to output a 2.0 dict
        assert wall.to_dict(version=(2, 0), exclude_defaults=False) == d_2_0

        # Load 2.0 dict
        wall = Wall.from_dict(d_2_0, version=(2, 0))
        assert wall.extra_keys is None
        # Output should be equivalent
        assert wall.to_dict(version=(2, 0), exclude_defaults=False) == d_2_0
        # Should be able to output a 1.0 dict
        # (though we have to set "connections" to an empty dict because it was
        # never present the input 2.0 dict and exclude_defaults is False)
        d_1_0["connections"] = {}
        assert wall.to_dict(version=(1, 0), exclude_defaults=False) == d_1_0

    def test_set_enable_disable(self):
        # ========================
        # No assignment validation
        # ========================
        wall = Wall("stone-wall", validate_assignment="none")

        # bool
        wall.enable_disable = True
        assert wall.enable_disable == True

        # Incorrect type
        wall.enable_disable = "incorrect"
        assert wall.enable_disable == "incorrect"

        # ===================
        # Miniumum validation
        # ===================
        wall.validate_assignment = "minimum"

        # bool
        wall.enable_disable = True
        assert wall.enable_disable == True

        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.enable_disable = "incorrect"

        # =================
        # Strict validation
        # =================
        wall.validate_assignment = "strict"

        # bool
        wall.enable_disable = True
        assert wall.enable_disable == True

        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.enable_disable = "incorrect"

        # ===================
        # Pedantic validation
        # ===================
        wall.validate_assignment = "pedantic"

        # bool
        wall.enable_disable = True
        assert wall.enable_disable == True

        # Incorrect type
        with pytest.raises(DataFormatError):
            wall.enable_disable = "incorrect"

    def test_set_read_gate(self):
        # ========================
        # No assignment validation
        # ========================
        wall = Wall("stone-wall", validate_assignment="none")

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
        assert wall.output_signal == AttrsSignalID(name="signal-A", type="virtual")
        assert wall.to_dict()["control_behavior"] == {
            "output_signal": {"name": "signal-A", "type": "virtual"}
        }

        # Known dict
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.output_signal == AttrsSignalID(name="signal-A", type="virtual")

        # Known dict but malformed
        with pytest.warns(MalformedSignalWarning):
            wall.output_signal = {"name": "signal-A", "type": "fluid"}
            assert wall.output_signal == AttrsSignalID(name="signal-A", type="fluid")

        # Unknown string
        with pytest.raises(IncompleteSignalError):
            wall.output_signal = "unknown-signal"
        # assert wall.output_signal == AttrsSignalID(name="signal-A", type="fluid")

        # Unknown dict
        with pytest.warns(UnknownSignalWarning):
            wall.output_signal = {"name": "unknown-signal", "type": "virtual"}
            assert wall.output_signal == AttrsSignalID(name="unknown-signal", type="virtual")

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
        assert wall.output_signal == AttrsSignalID(name="signal-A", type="virtual")

        # Known dict
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.output_signal == AttrsSignalID(name="signal-A", type="virtual")

        # Known dict but malformed
        with pytest.warns(MalformedSignalWarning):
            wall.output_signal = {"name": "signal-A", "type": "fluid"}
            assert wall.output_signal == AttrsSignalID(name="signal-A", type="fluid")

        # Unknown string
        with pytest.raises(IncompleteSignalError):
            wall.output_signal = "unknown-signal"

        # Unknown dict
        with pytest.warns(UnknownSignalWarning):
            wall.output_signal = {"name": "unknown-signal", "type": "virtual"}
            assert wall.output_signal == AttrsSignalID(name="unknown-signal", type="virtual")

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
        assert wall.output_signal == AttrsSignalID(name="signal-A", type="virtual")

        # Known dict
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.output_signal == AttrsSignalID(name="signal-A", type="virtual")

        # Known dict but malformed
        with pytest.warns(MalformedSignalWarning):
            wall.output_signal = {"name": "signal-A", "type": "fluid"}
            assert wall.output_signal == AttrsSignalID(name="signal-A", type="fluid")

        # Unknown string
        with pytest.raises(IncompleteSignalError):
            wall.output_signal = "unknown-signal"

        # Unknown dict
        with pytest.warns(UnknownSignalWarning):
            wall.output_signal = {"name": "unknown-signal", "type": "virtual"}
            assert wall.output_signal == AttrsSignalID(name="unknown-signal", type="virtual")

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
        assert wall.output_signal == AttrsSignalID(name="signal-A", type="virtual")

        # Known dict
        wall.output_signal = {"name": "signal-A", "type": "virtual"}
        assert wall.output_signal == AttrsSignalID(name="signal-A", type="virtual")

        # Known dict but malformed
        with pytest.warns(MalformedSignalWarning):
            wall.output_signal = {"name": "signal-A", "type": "fluid"}
            assert wall.output_signal == AttrsSignalID(name="signal-A", type="fluid")

        # Unknown string
        with pytest.raises(IncompleteSignalError):
            wall.output_signal = "unknown-signal"

        # Unknown dict
        with pytest.warns(UnknownSignalWarning):
            wall.output_signal = {"name": "unknown-signal", "type": "virtual"}
            assert wall.output_signal == AttrsSignalID(name="unknown-signal", type="virtual")

        # Incorrect Type
        with pytest.raises(DataFormatError):
            wall.output_signal = DataFormatError

    def test_power_and_circuit_flags(self):
        for name in walls:
            wall = Wall(name)
            assert wall.power_connectable == False
            assert wall.dual_power_connectable == False
            assert wall.circuit_connectable == True
            assert wall.dual_circuit_connectable == False

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

        wall3 = Wall("stone-wall", enable_disable=True, output_signal="signal-A")
        wall1.merge(wall3)

        assert wall1.tags == {} # Overwritten by blank
        assert wall1.enable_disable == True
        assert wall1.output_signal == AttrsSignalID(name="signal-A", type="virtual")
        

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
