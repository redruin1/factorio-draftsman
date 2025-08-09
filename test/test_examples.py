# test_examples.py
"""
Run all examples in order to ensure they're all up-to-date with any new breaking/
syntax changes.
"""

from draftsman.data import mods

import pytest

import importlib


@pytest.mark.skipif(mods.versions["base"] < (2, 0), reason="1.0 test")
@pytest.mark.parametrize(
    "example,given_input,expected_output",
    [
        (
            (importlib.import_module(t), None, None)
            if isinstance(t, str)
            else (importlib.import_module(t[0]), t[1], t[2])
        )
        for t in (
            "examples.blueprint_operands",
            "examples.combinator_text",
            # "examples.draftsman_logo", # TODO
            "examples.filtered_train",
            "examples.find_trains_filtered",
            "examples.item_stack_signals",
            # "examples.lamp_picture.py", # TODO
            # "examples.pumpjack_placer", # TODO
            # "examples.legacy_rail_planner_usage", # TODO
            "examples.read_prototype",
            "examples.recipe_types",
            # "examples.reverse_belts", # TODO
            "examples.signal_id",
            # "examples.signal_index", # TODO
            "examples.train_configuration_usage",
            "examples.train_schedule_usage",
            "examples.entities.decider_combinator",
            # "examples.entities.display_panel", # TODO
        )
    ],
)
def test_example_1_0(example, given_input, expected_output):
    # if given_input:
    #     pass

    result = example.main()

    # if expected_output:
    #     assert result == expected_output
