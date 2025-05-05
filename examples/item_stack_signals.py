# item_stack_signals.py

"""
Iterates over every item in the game and adds it to an (N x 5) cell of constant 
combinators with each value being that item's stack size. Commonly used when 
trying to figure out exactly how many slots need to be allocated in order to
transport x number of items.

In Factorio 2.0, this script has essentially been superceeded by the selector
combinator, which can automatically pull the stack size of an item or items 
without any additional circuitry. However, this script may still be useful for
Factorio 1.0, so it is retained for posterity.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.data import items
from draftsman.entity import ConstantCombinator

COMBINATOR_HEIGHT = 5


def main():
    blueprint = Blueprint()

    signal_index = 0
    signals_added = 0
    combinators_added = 0
    x = 0
    y = 0
    combinator = ConstantCombinator(direction=Direction.SOUTH)
    current_signal_section = combinator.add_section()

    # Iterate over every item in order:
    for item in items.raw:
        # Ignore hidden items/entities
        if "flags" in items.raw[item]:
            if "hidden" in items.raw[item]["flags"]:
                continue
        # Write the stack size signal
        stack_size = items.raw[item]["stack_size"]
        current_signal_section.set_signal(signal_index, item, stack_size)
        signal_index += 1
        # Keep track of how many items we've added in total
        signals_added += 1
        # Once we exceed the number of signals a combinator can hold, place it and reset
        if signal_index == 1000:
            # Add the combinator to the blueprint
            combinator.id = "{}_{}".format(x, y)
            blueprint.entities.append(combinator)
            # Reset the combinator
            combinators_added += 1
            y = combinators_added % COMBINATOR_HEIGHT
            x = int(combinators_added / COMBINATOR_HEIGHT)
            combinator.signals = None  # Clear signals
            combinator.tile_position = (x, y)
            signal_index = 0

    # Add the last combinator
    combinator.id = "{}_{}".format(x, y)
    blueprint.entities.append(combinator)

    # Add connections to each neighbour
    for cx in range(x):
        for cy in range(COMBINATOR_HEIGHT):
            here = "{}_{}".format(cx, cy)
            right = "{}_{}".format(cx + 1, cy)
            below = "{}_{}".format(cx, cy + 1)

            try:
                blueprint.add_circuit_connection("red", here, right)
            except KeyError:
                pass
            try:
                blueprint.add_circuit_connection("red", here, below)
            except KeyError:
                pass

    print("Total number of item signals added:", signals_added)
    print(blueprint.to_string())


if __name__ == "__main__":  # pragma: no coverage
    main()
