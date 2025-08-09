# decider_bit_checker.py

"""
Creates a set of combinators that check if a particular bit is flipped on or off
without the need for an additional arithmetic combinator. Only the uppermost
bits can be checked using this technique before the total condition count
becomes prohibitively large.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.entity import DeciderCombinator
from draftsman.signatures import SignalID

from typing import Optional


def determine_bit_conditions(
    bit_number: int,
    on: bool,
    signal=SignalID(name="cut-paste-tool"),
    additional_condition: Optional[DeciderCombinator.Condition] = None,
):
    def split_current_range(minimum, maximum, current_depth):
        midpoint = ((maximum - minimum) // 2) + minimum
        if current_depth == bit_number:
            if on:
                res = DeciderCombinator.Condition(
                    first_signal=signal,
                    comparator="<" if current_depth == 0 else ">=",
                    constant=midpoint,
                ) & DeciderCombinator.Condition(
                    first_signal=signal,
                    comparator=">=" if current_depth == 0 else "<",
                    constant=minimum if current_depth == 0 else min(2**31 - 1, maximum),
                )
                if additional_condition:
                    res &= additional_condition
                return res
            else:
                res = DeciderCombinator.Condition(
                    first_signal=signal,
                    comparator=">=",
                    constant=midpoint if current_depth == 0 else minimum,
                ) & DeciderCombinator.Condition(
                    first_signal=signal,
                    comparator="<=" if current_depth == 0 else "<",
                    constant=(
                        min(2**31 - 1, maximum) if current_depth == 0 else midpoint
                    ),
                )
                if additional_condition:
                    res &= additional_condition
                return res
        else:
            return split_current_range(
                minimum, midpoint, current_depth + 1
            ) + split_current_range(midpoint, maximum, current_depth + 1)

    return split_current_range(-(2**31), 2**31, 0)


def main():
    blueprint = Blueprint()

    minimum_bit = 0
    maximum_bit = 5

    # We'll output 2 columns of deciders, where each one represents the on/off
    # configuration for each bit
    decider = DeciderCombinator("decider-combinator", direction=Direction.EAST)
    for bit in range(minimum_bit, maximum_bit):
        for x in range(2):
            decider.conditions = determine_bit_conditions(bit, on=bool(x))
            print(len(decider.conditions))
            decider.outputs = [
                DeciderCombinator.Output(
                    signal="signal-check" if x else "signal-deny",
                    copy_count_from_input=False,
                )
            ]
            decider.tile_position = (x * decider.tile_width, bit)
            blueprint.entities.append(decider)

    print(blueprint.to_string())
    # For large outputs, use the following instead
    # import pyperclip
    # pyperclip.copy(blueprint.to_string())


if __name__ == "__main__":
    main()
