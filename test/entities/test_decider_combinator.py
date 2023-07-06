# test_arithmetic_combinator.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction
from draftsman.entity import DeciderCombinator, decider_combinators
from draftsman.error import (
    InvalidEntityError,
    DataFormatError,
    DraftsmanError,
)
from draftsman.warning import DraftsmanWarning
from draftsman.data import signals

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class DeciderCombinatorTesting(unittest.TestCase):
    def test_constructor_init(self):
        combinator = DeciderCombinator(
            "decider-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "decider_conditions": {"first_constant": 10, "second_constant": 10}
            },
        )
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "direction": 2,
            "control_behavior": {
                "decider_conditions": {"first_constant": 10, "second_constant": 10}
            },
        }

        combinator = DeciderCombinator(
            "decider-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "decider_conditions": {
                    "first_signal": "signal-A",
                    "comparator": ">=",
                    "second_signal": "signal-B",
                }
            },
        )
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "direction": Direction.EAST,
            "control_behavior": {
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≥",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        }

        combinator = DeciderCombinator(
            "decider-combinator",
            tile_position=[3, 3],
            direction=Direction.EAST,
            control_behavior={
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "<=",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        )
        self.maxDiff = None
        assert combinator.to_dict() == {
            "name": "decider-combinator",
            "position": {"x": 4.0, "y": 3.5},
            "direction": 2,
            "control_behavior": {
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "≤",
                    "second_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
        }

        # Warnings
        with pytest.warns(DraftsmanWarning):
            DeciderCombinator(unused_keyword="whatever")

        # Errors
        with pytest.raises(InvalidEntityError):
            DeciderCombinator("this is not an arithmetic combinator")
        with pytest.raises(DataFormatError):
            DeciderCombinator(control_behavior={"unused_key": "something"})

    def test_flags(self):
        for name in decider_combinators:
            combinator = DeciderCombinator(name)
            assert combinator.power_connectable == False
            assert combinator.dual_power_connectable == False
            assert combinator.circuit_connectable == True
            assert combinator.dual_circuit_connectable == True

    def test_set_first_operand(self):
        combinator = DeciderCombinator("decider-combinator")
        assert combinator.first_operand == None
        combinator.first_operand = "signal-A"
        assert combinator.first_operand == {"name": "signal-A", "type": "virtual"}
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"}
            }
        }

        combinator.first_operand = {"name": "signal-B", "type": "virtual"}
        assert combinator.first_operand == {"name": "signal-B", "type": "virtual"}
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-B", "type": "virtual"}
            }
        }

        combinator.first_operand = None
        assert combinator.first_operand == None
        assert combinator.control_behavior == {"decider_conditions": {}}

        with pytest.raises(TypeError):
            combinator.first_operand = TypeError
        with pytest.raises(TypeError):
            combinator.first_operand = "incorrect"
        with pytest.raises(TypeError):
            combinator.first_operand = 10

        combinator.remove_decider_conditions()
        combinator.output_signal = "signal-everything"
        combinator.first_operand = "signal-everything"
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-everything", "type": "virtual"},
                "output_signal": {"name": "signal-everything", "type": "virtual"},
            }
        }
        with pytest.warns(DraftsmanWarning):
            combinator.first_operand = "signal-each"
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-each", "type": "virtual"}
            }
        }

    def test_set_operation(self):
        combinator = DeciderCombinator("decider-combinator")
        assert combinator.operation == None
        combinator.operation = "="
        assert combinator.operation == "="
        assert combinator.control_behavior == {
            "decider_conditions": {"comparator": "="}
        }

        combinator.operation = ">="
        assert combinator.operation == "≥"
        assert combinator.control_behavior == {
            "decider_conditions": {"comparator": "≥"}
        }

        combinator.operation = None
        assert combinator.operation == None
        assert combinator.control_behavior == {"decider_conditions": {}}

        with pytest.raises(TypeError):
            combinator.operation = TypeError
        with pytest.raises(TypeError):
            combinator.operation = "incorrect"

    def test_set_second_operand(self):
        combinator = DeciderCombinator("decider-combinator")
        assert combinator.second_operand == None
        combinator.second_operand = "signal-A"
        assert combinator.second_operand == {"name": "signal-A", "type": "virtual"}
        assert combinator.control_behavior == {
            "decider_conditions": {
                "second_signal": {"name": "signal-A", "type": "virtual"}
            }
        }

        combinator.second_operand = {"name": "signal-B", "type": "virtual"}
        assert combinator.second_operand == {"name": "signal-B", "type": "virtual"}
        assert combinator.control_behavior == {
            "decider_conditions": {
                "second_signal": {"name": "signal-B", "type": "virtual"}
            }
        }

        combinator.second_operand = 100
        assert combinator.second_operand == 100
        assert combinator.control_behavior == {"decider_conditions": {"constant": 100}}

        combinator.first_operand = "signal-A"
        combinator.second_operand = None
        assert combinator.second_operand == None
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"}
            }
        }

        with pytest.raises(TypeError):
            combinator.second_operand = TypeError
        with pytest.raises(TypeError):
            combinator.second_operand = "incorrect"
        for pure_virtual_signal in signals.pure_virtual:
            with pytest.raises(DraftsmanError):
                combinator.second_operand = pure_virtual_signal

    def test_set_output_signal(self):
        combinator = DeciderCombinator("decider-combinator")
        assert combinator.output_signal == None
        combinator.output_signal = "signal-A"
        assert combinator.output_signal == {"name": "signal-A", "type": "virtual"}
        assert combinator.control_behavior == {
            "decider_conditions": {
                "output_signal": {"name": "signal-A", "type": "virtual"}
            }
        }

        combinator.output_signal = {"name": "signal-B", "type": "virtual"}
        assert combinator.output_signal == {"name": "signal-B", "type": "virtual"}
        assert combinator.control_behavior == {
            "decider_conditions": {
                "output_signal": {"name": "signal-B", "type": "virtual"}
            }
        }

        combinator.output_signal = None
        assert combinator.output_signal == None
        assert combinator.control_behavior == {"decider_conditions": {}}

        with pytest.raises(TypeError):
            combinator.output_signal = TypeError
        with pytest.raises(TypeError):
            combinator.output_signal = "incorrect"

        combinator.remove_decider_conditions()
        combinator.output_signal = "signal-everything"
        assert combinator.control_behavior == {
            "decider_conditions": {
                "output_signal": {"name": "signal-everything", "type": "virtual"}
            }
        }
        with pytest.raises(DraftsmanError):
            combinator.output_signal = "signal-anything"
        with pytest.raises(DraftsmanError):
            combinator.output_signal = "signal-each"

        combinator.first_operand = "signal-everything"
        combinator.output_signal = "signal-everything"
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-everything", "type": "virtual"},
                "output_signal": {"name": "signal-everything", "type": "virtual"},
            }
        }
        with pytest.raises(DraftsmanError):
            combinator.output_signal = "signal-anything"
        with pytest.raises(DraftsmanError):
            combinator.output_signal = "signal-each"

        combinator.first_operand = "signal-anything"
        combinator.output_signal = "signal-everything"
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-anything", "type": "virtual"},
                "output_signal": {"name": "signal-everything", "type": "virtual"},
            }
        }
        combinator.output_signal = "signal-anything"
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-anything", "type": "virtual"},
                "output_signal": {"name": "signal-anything", "type": "virtual"},
            }
        }

        with pytest.raises(DraftsmanError):
            combinator.output_signal = "signal-each"

        combinator.remove_decider_conditions()
        combinator.first_operand = "signal-each"
        combinator.output_signal = "signal-each"
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-each", "type": "virtual"},
                "output_signal": {"name": "signal-each", "type": "virtual"},
            }
        }
        with pytest.raises(DraftsmanError):
            combinator.output_signal = "signal-everything"
        with pytest.raises(DraftsmanError):
            combinator.output_signal = "signal-anything"

    def test_set_decider_conditions(self):
        combinator = DeciderCombinator()
        combinator.set_decider_conditions("signal-A", ">", "iron-ore")
        self.maxDiff = None
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "comparator": ">",
                "second_signal": {"name": "iron-ore", "type": "item"},
            }
        }
        combinator.set_decider_conditions("signal-A", "=", "copper-ore", "signal-B")
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-A", "type": "virtual"},
                "comparator": "=",
                "second_signal": {"name": "copper-ore", "type": "item"},
                "output_signal": {"name": "signal-B", "type": "virtual"},
            }
        }

        combinator.set_decider_conditions("signal-D", "<", 10, "signal-E")
        assert combinator.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-D", "type": "virtual"},
                "comparator": "<",
                "constant": 10,
                "output_signal": {"name": "signal-E", "type": "virtual"},
            }
        }

        combinator.set_decider_conditions(None, ">", 10)
        assert combinator.control_behavior == {
            "decider_conditions": {"constant": 10, "comparator": ">"}
        }

        combinator.set_decider_conditions(None, None, None, None)
        assert combinator.control_behavior == {"decider_conditions": {}}

        combinator.set_decider_conditions()
        assert combinator.control_behavior == {
            "decider_conditions": {"comparator": "<", "constant": 0}
        }

        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions(TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("incorrect")
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "incorrect", "signal-D")
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "incorrect")
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "signal-D", TypeError)
        with pytest.raises(DataFormatError):
            combinator.set_decider_conditions("signal-A", "<", "signal-D", "incorrect")

        # TODO:
        assert combinator.control_behavior == {
            "decider_conditions": {"comparator": "<", "constant": 0}
        }

        # Test Remove conditions
        combinator.remove_decider_conditions()
        assert combinator.control_behavior == {}

        # Test set_copy_count
        assert combinator.copy_count_from_input == None
        combinator.copy_count_from_input = True
        assert combinator.copy_count_from_input == True
        assert combinator.control_behavior == {
            "decider_conditions": {"copy_count_from_input": True}
        }
        combinator.copy_count_from_input = False
        assert combinator.control_behavior == {
            "decider_conditions": {"copy_count_from_input": False}
        }
        combinator.copy_count_from_input = None
        assert combinator.control_behavior == {"decider_conditions": {}}

        # Error
        with pytest.raises(TypeError):
            combinator.copy_count_from_input = "incorrect"

    def test_mergable_with(self):
        comb1 = DeciderCombinator("decider-combinator", direction=Direction.SOUTH)
        comb2 = DeciderCombinator(
            "decider-combinator",
            direction=Direction.SOUTH,
            control_behavior={
                "decider_conditions": {
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "<",
                    "constant": 10,
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                    "copy_count_from_input": False,
                }
            },
            tags={"some": "stuff"},
        )

        assert comb1.mergable_with(comb2)
        assert comb2.mergable_with(comb1)

        comb2.first_operand = "signal-A"
        comb2.operation = ">="
        assert comb1.mergable_with(comb2)

        comb2.direction = Direction.NORTH
        assert not comb1.mergable_with(comb2)

    def test_merge(self):
        comb1 = DeciderCombinator(
            "decider-combinator",
            direction=Direction.SOUTH,
            control_behavior={
                "decider_conditions": {
                    "first_signal": {"name": "signal-A", "type": "virtual"},
                    "comparator": "=",
                    "second_signal": {"name": "copper-ore", "type": "item"},
                    "output_signal": {"name": "signal-B", "type": "virtual"},
                }
            },
            tags={"original": "tags"},
        )
        comb2 = DeciderCombinator(
            "decider-combinator",
            direction=Direction.SOUTH,
            control_behavior={
                "decider_conditions": {
                    "first_signal": {"name": "signal-D", "type": "virtual"},
                    "comparator": "<",
                    "constant": 10,
                    "output_signal": {"name": "signal-E", "type": "virtual"},
                    "copy_count_from_input": False,
                }
            },
        )

        comb1.merge(comb2)
        del comb2

        assert comb1.control_behavior == {
            "decider_conditions": {
                "first_signal": {"name": "signal-D", "type": "virtual"},
                "comparator": "<",
                "constant": 10,
                "output_signal": {"name": "signal-E", "type": "virtual"},
                "copy_count_from_input": False,
            }
        }
        assert comb1.tags == {}  # Overwritten by comb2
