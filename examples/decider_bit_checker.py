# decider_bit_checker.py

"""
Creates a set of combinators that check if a particular bit is flipped on or off
without the need for an additional arithmetic combinator. Only the uppermost 
bits can be checked using this technique before running into the maximum number
of conditions per combinator.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.entity import DeciderCombinator
from draftsman.signatures import SignalID


def determine_bit_conditions(bit_number, on: bool, signal=SignalID(name="cut-paste-tool")):
    def split_current_range(minimum, maximum, current_depth):
        midpoint = ((maximum - minimum) // 2) + minimum
        if current_depth == bit_number:
            if on:
                return DeciderCombinator.Condition(
                        first_signal="signal-each",
                        first_signal_networks={"red"},
                        comparator="=",
                        second_signal=signal
                    ) & DeciderCombinator.Condition(
                        first_signal=signal,
                        comparator="<" if current_depth == 0 else ">=",
                        constant=midpoint
                    ) & DeciderCombinator.Condition(
                        first_signal=signal,
                        comparator=">=" if current_depth == 0 else "<",
                        constant=minimum if current_depth == 0 else min(2**31-1, maximum)
                    )
            else:
                return DeciderCombinator.Condition(
                        first_signal=signal,
                        comparator=">=",
                        constant=midpoint if current_depth == 0 else minimum
                    ) & DeciderCombinator.Condition(
                        first_signal=signal,
                        comparator="<=" if current_depth == 0 else "<",
                        constant=min(2**31-1, maximum) if current_depth == 0 else midpoint
                    )
        else:
            return split_current_range(
                minimum, midpoint, current_depth + 1
            ) + split_current_range(
                midpoint, maximum, current_depth + 1
            )

    return split_current_range(-2**31, 2**31, 0)

def main():
    blueprint = Blueprint()

    # We'll output 2 columns of deciders, where each one represents the on/off
    # configuration for each bit
    decider = DeciderCombinator("decider-combinator", direction=Direction.EAST)
    for y in range(2, 5):
        for x in range(2):
            decider.conditions = determine_bit_conditions(y, x)
            print(len(decider.conditions))
            decider.outputs = [
                DeciderCombinator.Output(
                    signal="signal-check" if x else "signal-deny", 
                    copy_count_from_input=False
                )
            ]
            decider.tile_position = (x * 2, y)
            blueprint.entities.append(decider)

    # print(blueprint.to_string())
    import pyperclip
    pyperclip.copy(blueprint.to_string())

if __name__ == "__main__":
    main()