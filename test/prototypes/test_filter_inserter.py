# test_filter_inserter.py
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

from draftsman.constants import Direction, ReadMode
from draftsman.entity import FilterInserter, filter_inserters, Container
from draftsman.error import InvalidEntityError, DataFormatError
from draftsman.warning import DraftsmanWarning

from collections.abc import Hashable
import sys
import pytest

if sys.version_info >= (3, 3):  # pragma: no coverage
    import unittest
else:  # pragma: no coverage
    import unittest2 as unittest


class FilterInserterTesting(unittest.TestCase):
    def test_constructor_init(self):
        # Valid
        inserter = FilterInserter(
            "filter-inserter",
            direction=Direction.EAST,
            tile_position=[1, 1],
            override_stack_size=1,
            filter_mode="blacklist",
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
            filters=["wooden-chest", "iron-chest", "steel-chest"],
        )
        assert inserter.to_dict() == {
            "name": "filter-inserter",
            "position": {"x": 1.5, "y": 1.5},
            "direction": Direction.EAST,
            "override_stack_size": 1,
            "filter_mode": "blacklist",
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
                "circuit_hand_read_mode": ReadMode.PULSE,
            },
            "connections": {"1": {"green": [{"entity_id": 2, "circuit_id": 1}]}},
            "filters": [
                {"index": 1, "name": "wooden-chest"},
                {"index": 2, "name": "iron-chest"},
                {"index": 3, "name": "steel-chest"},
            ],
        }

        inserter = FilterInserter(
            "filter-inserter",
            control_behavior={
                "stack_control_input_signal": {"name": "signal-A", "type": "virtual"}
            },
        )
        assert inserter.to_dict() == {
            "name": "filter-inserter",
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
            FilterInserter(position=[0, 0], direction=Direction.WEST, invalid_keyword=5)

        # Errors
        # Raises InvalidEntityID when not in containers
        with pytest.raises(InvalidEntityError):
            FilterInserter("this is not a filter inserter")

        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            FilterInserter("filter-inserter", id=25)

        with pytest.raises(TypeError):
            FilterInserter("filter-inserter", position=TypeError)

        with pytest.raises(ValueError):
            FilterInserter("filter-inserter", direction="incorrect")

        # TODO: move to validate
        # with pytest.raises(TypeError):
        #     FilterInserter("filter-inserter", override_stack_size="incorrect")

        # with pytest.raises(DataFormatError):
        #     FilterInserter(
        #         "filter-inserter", connections={"this is": ["very", "wrong"]}
        #     )

        # with pytest.raises(DataFormatError):
        #     FilterInserter(
        #         "filter-inserter",
        #         control_behavior={"this is": ["also", "very", "wrong"]},
        #     )

        with pytest.raises(ValueError):
            FilterInserter(filter_mode=TypeError)
        with pytest.raises(ValueError):
            FilterInserter("filter-inserter", filter_mode="wrong")

    def test_power_and_circuit_flags(self):
        for name in filter_inserters:
            inserter = FilterInserter(name)
            assert inserter.power_connectable == False
            assert inserter.dual_power_connectable == False
            assert inserter.circuit_connectable == True
            assert inserter.dual_circuit_connectable == False

    def test_set_filter_mode(self):
        inserter = FilterInserter()
        inserter.filter_mode = "blacklist"
        assert inserter.filter_mode == "blacklist"
        inserter.filter_mode = None
        assert inserter.filter_mode == None
        with pytest.raises(ValueError):
            inserter.filter_mode = "incorrect"

    def test_mergable_with(self):
        inserter1 = FilterInserter("filter-inserter")
        inserter2 = FilterInserter(
            "filter-inserter",
            filter_mode="whitelist",
            override_stack_size=1,
            filters=[{"name": "coal", "index": 1}],
        )
        assert inserter1.mergable_with(inserter1)

        assert inserter1.mergable_with(inserter2)
        assert inserter2.mergable_with(inserter1)

        inserter2.tile_position = (1, 1)
        assert not inserter1.mergable_with(inserter2)

        inserter2.tile_position = (0, 0)
        inserter2.direction = Direction.EAST
        assert not inserter1.mergable_with(inserter2)

        inserter2 = FilterInserter("stack-filter-inserter")
        assert not inserter1.mergable_with(inserter2)

    def test_merge(self):
        inserter1 = FilterInserter("filter-inserter")
        inserter2 = FilterInserter(
            "filter-inserter",
            filter_mode="whitelist",
            override_stack_size=1,
            filters=[{"name": "coal", "index": 1}],
            tags={"some": "stuff"},
        )

        inserter1.merge(inserter2)
        del inserter2

        assert inserter1.filter_mode == "whitelist"
        assert inserter1.override_stack_size == 1
        assert inserter1.filters == [{"name": "coal", "index": 1}]
        assert inserter1.tags == {"some": "stuff"}

    def test_eq(self):
        inserter1 = FilterInserter("filter-inserter")
        inserter2 = FilterInserter("filter-inserter")

        assert inserter1 == inserter2

        inserter1.tags = {"some": "stuff"}

        assert inserter1 != inserter2

        container = Container()

        assert inserter1 != container
        assert inserter2 != container

        # hashable
        assert isinstance(inserter1, Hashable)
