# decider_combinator.py
"""
Shows various ways to manipulate the conditions and outputs of decider
combinators.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.entity import DeciderCombinator


def main():
    blueprint = Blueprint()

    dc = DeciderCombinator("decider-combinator", direction=Direction.EAST)

    # I would alias these as it's a bit clunky to type otherwise
    Input = DeciderCombinator.Input
    Output = DeciderCombinator.Output

    # An Input is defined with a SignalID followed by a `CircuitNetworkSelection`
    # (which wire colors to read from). If no network specification is given,
    # an Input defaults to both red and green wire colors:
    assert Input("signal-A") == Input("signal-A", {"red", "green"})

    # Conditions objects are easiest to specify using equality operators:
    condition_1 = Input("signal-A") > Input("signal-B", {"red"})
    condition_2 = Input("signal-C", {"green"}) == Input("signal-D")
    condition_3 = Input("signal-each", {"green"}) <= Input("signal-each", set())
    # (Alternatively, use the `DeciderCombinator.Condition()` constructor)

    # These conditions can then be combined with the bitwise `&` and `|`
    # operators to perform conditional AND and OR operations, respectively:
    dc.conditions = condition_1 & condition_2 | condition_3

    # Or, if you wanted to define the same conditions above all in one go:
    # (Note that due to order of operations the parenthesis must be respected!)
    dc.conditions = (Input("signal-A") > Input("signal-B", {"red"})) & (
        Input("signal-C", {"green"}) == Input("signal-D")
    ) | (Input("signal-each", {"green"}) <= Input("signal-each", set()))

    # The result is a list of Condition objects:
    assert isinstance(dc.conditions, list)
    assert type(dc.conditions[0]) is DeciderCombinator.Condition

    # Conditions can be appended to the existing conditions list by using "|="
    # or "&=", and integers can be used as valid operands as long as they exist
    # on the *right* side of the equation:
    dc.conditions |= Input("transport-belt", networks={"green"}) != -(2**31)

    # Outputs are specified as a list of Output objects. By modifying their
    # parameters you can control what wires they consider for value, whether or
    # not they output constant values, or even what that constant value should
    # be:
    dc.outputs = [
        # Ouput signal-A with constant value 1
        Output("signal-A", copy_count_from_input=False),
        # Output each passing signal with their values from green wire
        Output("signal-each", networks={"green"}),
        # Ouput signal-B with constant value 101
        Output("signal-B", copy_count_from_input=False, constant=101),
    ]

    blueprint.entities.append(dc)

    print(blueprint.to_string())


if __name__ == "__main__":
    main()
