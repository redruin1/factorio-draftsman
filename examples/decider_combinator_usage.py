# decider_combinator_usage.py

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.entity import DeciderCombinator
from draftsman.prototypes.decider_combinator import DeciderInput as Input
from draftsman.prototypes.decider_combinator import DeciderOutput as Output


def main():
    blueprint = Blueprint()

    dc = DeciderCombinator("decider-combinator", direction=Direction.EAST)

    # Conditions are specified an expression of Inputs with operators
    dc.conditions = (
          (Input("signal-A") > Input("signal-B", {"red"}))
        & (Input("signal-C", {"green"}) == Input("signal-D"))
        | (Input("signal-each", {"green"}) <= Input("signal-each", {"red", "green"}))
    )

    # Outputs are specified as a list of Output objects
    dc.outputs = [
        Output("signal-A", copy_count_from_input=False),
        Output("signal-each", networks={"green"})
    ]

    blueprint.entities.append(dc)
    print(blueprint.to_string())


if __name__ == "__main__":
    main()