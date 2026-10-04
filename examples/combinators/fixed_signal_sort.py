# fixed_signal_sort.py

"""
Creates a single decider that sorts a fixed number of signals, using an array
of conditions. Outputs either the minimum or maximum signal depending on the
given configuration. In case of a tie, the output signal is the first one as
specified in the given signal list.

If inputs are guaranteed to be unique (no two input signals ever have the same
value) then you can use the `SIMPLE` mode which only includes the decider. If this
cannot be guaranteed, an additional constant combinator is provided and wired
up to the green input to compare against.

The reason why you would use this instead of a selector combinator set to
ascending/descending is because this can sort the signal and then immediately
swap it's value to a fixed signal in one tick, wheras with a selector you'd
need an additional combinator afterwards to coerce the signal type. This is
useful in some golfing situations.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.entity import ConstantCombinator, DeciderCombinator

from typing import Literal

ORDER: Literal["ascending", "descending"] = "ascending"
SIGNAL_NAMES: list[str] = [
    "signal-0",
    "signal-1",
    "signal-2",
    "signal-3",
    "signal-4",
    "signal-5",
    "signal-6",
    "signal-7",
    "signal-8",
    "signal-9",
    "signal-A",
    "signal-B",
    "signal-C",
    "signal-D",
    "signal-E",
    "signal-F",
]
SIMPLE: bool = True

ADDITIONAL_CONDITIONS: list[DeciderCombinator.Condition] = [
    DeciderCombinator.Input("signal-check", {"green"}) > 0
]


def main():
    bp = Blueprint()

    decider = DeciderCombinator("decider-combinator", direction=Direction.EAST)
    for i, current_signal in enumerate(SIGNAL_NAMES):
        other_signals = SIGNAL_NAMES[:i] + SIGNAL_NAMES[i + 1 :]
        lhs = DeciderCombinator.Input(current_signal, {"red"})
        for n, other_signal in enumerate(other_signals):
            rhs = DeciderCombinator.Input(other_signal, {"red"})
            condition = lhs < rhs if ORDER == "ascending" else lhs > rhs
            if n == 0:
                # Make sure the first condition is OR-ed with the previous set
                decider.conditions |= condition
            else:
                decider.conditions &= condition
        # Add each condition (so we can actually output the value)
        decider.conditions &= DeciderCombinator.Input("signal-each", {"red"}) == lhs
        # add additional constraints
        for additional_condition in ADDITIONAL_CONDITIONS:
            decider.conditions &= additional_condition

    # We leave the output of the decider empty so that the user can define
    # whether the output should be `each` or some specific signal
    bp.entities.append(decider)

    if not SIMPLE:
        cc = ConstantCombinator(
            "constant-combinator", tile_position=(-1, 0), direction=Direction.EAST
        )
        for i, signal_name in enumerate(SIGNAL_NAMES):
            cc.set_signal(i, signal_name, count=i)
        bp.entities.append(cc)
        bp.add_circuit_connection("green", 0, 1)

    print(bp.to_string())


if __name__ == "__main__":
    main()
