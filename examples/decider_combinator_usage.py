# decider_combinator_usage.py
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

    # Conditions are specified an expression of Inputs with operators:
    # (Note that due to order of operations the parenthesis must be respected!)
    dc.conditions = (
          (Input("signal-A") > Input("signal-B", {"red"}))
        & (Input("signal-C", {"green"}) == Input("signal-D"))
        | (Input("signal-each", {"green"}) <= Input("signal-each", {"red", "green"}))
    )

    # The result is a list of DeciderCondition objects:
    assert isinstance(dc.conditions, list)
    assert type(dc.conditions[0]) is DeciderCombinator.Condition

    # Conditions can be appended by using "|=" or "&=", and integers can be used
    # as valid operands as long as they exist on the right side of the equation:
    dc.conditions |= (Input("transport-belt", networks={"green"}) != -2**31)

    # Outputs are specified as a list of Output objects. By modifying their 
    # parameters you can control what wires they consider for value, whether or
    # not they output constant values, or even what that constant value should
    # be:
    dc.outputs = [
        Output("signal-A", copy_count_from_input=False),
        Output("signal-each", networks={"green"}),
        Output("signal-B", copy_count_from_input=False, constant=101)
    ]

    blueprint.entities.append(dc)

    # Decider parameters can also be specified in their raw form if desired:
    dc.conditions = [
        {
            "first_signal": {
                "name": "signal-A",
                "type": "virtual"
            },
            "comparator": "<",
            "second_signal": {
                "name": "signal-B",
                "type": "virtual"
            },
            "second_signal_networks": {
                "green": False
            }
        }
    ]
    dc.outputs = [
        {
            "signal": {
                "name": "signal-B",
                "type": "virtual"
            },
            "copy_count_from_input": False,
            "constant": 123
        }
    ]
    blueprint.entities.append(dc, tile_position=(3, 0))

    print(blueprint.to_string())


if __name__ == "__main__":
    main()