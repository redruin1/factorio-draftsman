# test_inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction, ReadMode
from draftsman.entity import Inserter, inserters
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class InserterTesting(unittest.TestCase):
    def test_constructor_init(self):
        # Valid
        inserter = Inserter(
            "inserter",
            direction=Direction.EAST,
            tile_position=[1, 1],
            override_stack_size=1,
            control_behavior={
                "circuit_set_stack_size": True,
                "stack_control_input_signal": "signal-A",
                "circuit_enable_disable": True,
                "circuit_condition": {},
                "connect_to_logistic_network": True,
                "logistic_condition": {},
                "circuit_read_hand_contents": True,
                "circuit_hand_read_mode": ReadMode.PULSE,
            },
            connections={"1": {"green": [{"entity_id": 2, "circuit_id": 1}]}},
        )
        assert inserter.to_dict() == {
            "name": "inserter",
            "position": {"x": 1.5, "y": 1.5},
            "direction": 2,
            "override_stack_size": 1,
            "control_behavior": {
                "circuit_set_stack_size": True,
                "stack_control_input_signal": {
                    "name": "signal-A",
                    "type": "virtual",
                },
                "circuit_enable_disable": True,
                "circuit_condition": {},
                "connect_to_logistic_network": True,
                "logistic_condition": {},
                "circuit_read_hand_contents": True,
                "circuit_hand_read_mode": 0,
            },
            "connections": {"1": {"green": [{"entity_id": 2, "circuit_id": 1}]}},
        }

        inserter = Inserter(
            "inserter",
            control_behavior={
                "stack_control_input_signal": {"name": "signal-A", "type": "virtual"}
            },
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
        with pytest.warns(DraftsmanWarning):
            Inserter(position=[0, 0], direction=Direction.WEST, invalid_keyword=5)

        # Errors
        # Raises InvalidEntityID when not in containers
        with pytest.raises(InvalidEntityError):
            Inserter("this is not an inserter")

        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            Inserter("inserter", id=25)

        with pytest.raises(TypeError):
            Inserter("inserter", position=TypeError)

        with pytest.raises(ValueError):
            Inserter("inserter", direction="incorrect")

        with pytest.raises(TypeError):
            Inserter("inserter", override_stack_size="incorrect")

        with pytest.raises(DataFormatError):
            Inserter("inserter", connections={"this is": ["very", "wrong"]})

        with pytest.raises(DataFormatError):
            Inserter(
                "inserter", control_behavior={"this is": ["also", "very", "wrong"]}
            )

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
