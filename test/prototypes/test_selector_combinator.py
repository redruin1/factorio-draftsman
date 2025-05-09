# test_selector_combinator.py

from draftsman.prototypes.selector_combinator import (
    SelectorCombinator,
    selector_combinators,
)
from draftsman.signatures import AttrsSignalID, QualityFilter
from draftsman.warning import UnknownEntityWarning

import pytest


def test_constructor():
    selector = SelectorCombinator("selector-combinator")

    with pytest.warns(UnknownEntityWarning):
        SelectorCombinator("unknown selector combinator")


def test_flags():
    for selector_name in selector_combinators:
        selector = SelectorCombinator(selector_name)
        assert selector.power_connectable == False
        assert selector.dual_power_connectable == False
        assert selector.circuit_connectable == True
        assert selector.dual_circuit_connectable == True


def test_set_mode():
    selector = SelectorCombinator("selector-combinator")

    selector.set_mode_select(select_max=False, index_constant=100)
    assert selector.operation == "select"
    assert selector.select_max is False
    assert selector.index_constant == 100
    assert selector.index_signal is None
    assert selector.to_dict() == {
        "name": "selector-combinator",
        "position": {"x": 0.5, "y": 1.0},
        "control_behavior": {
            "operation": "select",
            "select_max": False,
            "index_constant": 100,
        },
    }

    selector.wipe_settings()
    selector.set_mode_count(count_signal="signal-C")
    assert selector.operation == "count"
    assert selector.count_signal == AttrsSignalID(name="signal-C", type="virtual")
    assert selector.to_dict() == {
        "name": "selector-combinator",
        "position": {"x": 0.5, "y": 1.0},
        "control_behavior": {
            "operation": "count",
            "count_inputs_signal": {"name": "signal-C", "type": "virtual"},
        },
    }

    selector.wipe_settings()
    selector.set_mode_random(interval=100)
    assert selector.operation == "random"
    assert selector.random_update_interval == 100
    assert selector.to_dict() == {
        "name": "selector-combinator",
        "position": {"x": 0.5, "y": 1.0},
        "control_behavior": {"operation": "random", "random_update_interval": 100},
    }

    selector.wipe_settings()
    selector.set_mode_stack_size()
    assert selector.operation == "stack-size"
    assert selector.to_dict() == {
        "name": "selector-combinator",
        "position": {"x": 0.5, "y": 1.0},
        "control_behavior": {
            "operation": "stack-size",
        },
    }

    selector.wipe_settings()
    selector.set_mode_rocket_capacity()
    assert selector.operation == "rocket-capacity"
    assert selector.to_dict() == {
        "name": "selector-combinator",
        "position": {"x": 0.5, "y": 1.0},
        "control_behavior": {
            "operation": "rocket-capacity",
        },
    }

    selector.wipe_settings()
    selector.set_mode_quality_filter("normal", ">")
    assert selector.operation == "quality-filter"
    assert selector.quality_filter == QualityFilter(quality="normal", comparator=">")
    assert selector.to_dict() == {
        "name": "selector-combinator",
        "position": {"x": 0.5, "y": 1.0},
        "control_behavior": {
            "operation": "quality-filter",
            "quality_filter": {"quality": "normal", "comparator": ">"},
        },
    }

    selector.wipe_settings()
    selector.set_mode_quality_transfer(
        source_static="legendary", destination_signal="signal-each"
    )
    assert selector.operation == "quality-transfer"
    assert selector.select_quality_from_signal is False
    assert selector.quality_source_static == "legendary"
    assert selector.quality_source_signal is None
    assert selector.quality_destination_signal == AttrsSignalID(
        name="signal-each", type="virtual"
    )
    assert selector.to_dict() == {
        "name": "selector-combinator",
        "position": {"x": 0.5, "y": 1.0},
        "control_behavior": {
            "operation": "quality-transfer",
            "quality_source_static": "legendary",
            "quality_destination_signal": {"name": "signal-each", "type": "virtual"},
        },
    }
