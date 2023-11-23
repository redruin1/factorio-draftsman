# test_filter_inserter.py

from draftsman.constants import Direction, ReadMode
from draftsman.entity import FilterInserter, filter_inserters, Container
from draftsman.error import DataFormatError, InvalidItemError
from draftsman.signatures import FilterEntry
from draftsman.warning import (
    UnknownEntityWarning,
    UnknownItemWarning,
    UnknownKeywordWarning,
)

from collections.abc import Hashable
import pytest


class TestFilterInserter:
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
                # "circuit_condition": {}, # Default
                "connect_to_logistic_network": True,
                # "logistic_condition": {}, # Default
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
        with pytest.warns(UnknownKeywordWarning):
            FilterInserter(position=[0, 0], direction=Direction.WEST, invalid_keyword=5)
        with pytest.warns(UnknownKeywordWarning):
            FilterInserter(control_behavior={"unused": "keyword"})
        with pytest.warns(UnknownKeywordWarning):
            FilterInserter(
                "filter-inserter", connections={"this is": ["very", "wrong"]}
            )
        with pytest.warns(UnknownEntityWarning):
            FilterInserter("this is not a filter inserter")

        # Errors
        # Raises schema errors when any of the associated data is incorrect
        with pytest.raises(TypeError):
            FilterInserter("filter-inserter", id=25)

        with pytest.raises(TypeError):
            FilterInserter("filter-inserter", position=TypeError)

        with pytest.raises(DataFormatError):
            FilterInserter("filter-inserter", direction="incorrect")
        with pytest.raises(DataFormatError):
            FilterInserter("filter-inserter", override_stack_size="incorrect")
        with pytest.raises(DataFormatError):
            FilterInserter("filter-inserter", connections="incorrect")
        with pytest.raises(DataFormatError):
            FilterInserter(
                "filter-inserter",
                control_behavior="incorrect",
            )
        with pytest.raises(DataFormatError):
            FilterInserter(filter_mode=TypeError)
        with pytest.raises(DataFormatError):
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

        with pytest.raises(DataFormatError):
            inserter.filter_mode = "incorrect"

    def test_set_item_filter(self):
        inserter = FilterInserter("filter-inserter")
        inserter.set_item_filter(0, "wooden-chest")
        assert inserter.filters == [FilterEntry(**{"index": 1, "name": "wooden-chest"})]

        # Modify in place
        inserter.set_item_filter(0, "iron-chest")
        assert inserter.filters == [FilterEntry(**{"index": 1, "name": "iron-chest"})]

        inserter.filters = None
        assert inserter.filters == None
        with pytest.raises(DataFormatError):
            inserter.set_item_filter(100, "wooden-chest")

        with pytest.warns(UnknownItemWarning):
            inserter.set_item_filter(0, "unknown-item")
        assert inserter.filters == [FilterEntry(**{"index": 1, "name": "unknown-item"})]

        # Init if None
        inserter.set_item_filter(0, "wooden-chest")
        inserter.set_item_filter(1, "iron-chest")
        assert inserter.filters == [
            FilterEntry(**{"index": 1, "name": "wooden-chest"}),
            FilterEntry(**{"index": 2, "name": "iron-chest"}),
        ]

        # Delete if set to None
        inserter.set_item_filter(1, None)
        assert inserter.filters == [FilterEntry(**{"index": 1, "name": "wooden-chest"})]

        with pytest.raises(DataFormatError):
            inserter.set_item_filter("incorrect", "incorrect")

    def test_set_item_filters(self):
        inserter = FilterInserter("filter-inserter")

        # Shorthand
        inserter.set_item_filters("iron-plate", "copper-plate", "steel-plate")
        assert inserter.filters == [
            FilterEntry(index=1, name="iron-plate"),
            FilterEntry(index=2, name="copper-plate"),
            FilterEntry(index=3, name="steel-plate"),
        ]

        # Longhand
        longhand = [
            {"index": 1, "name": "iron-plate"},
            {"index": 2, "name": "copper-plate"},
            {"index": 3, "name": "steel-plate"},
        ]
        inserter.set_item_filters(*longhand)
        assert inserter.filters == [
            FilterEntry(index=1, name="iron-plate"),
            FilterEntry(index=2, name="copper-plate"),
            FilterEntry(index=3, name="steel-plate"),
        ]

        # None case
        inserter.set_item_filters(None)
        assert inserter.filters == None

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
        assert inserter1.filters == [FilterEntry(**{"name": "coal", "index": 1})]
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
