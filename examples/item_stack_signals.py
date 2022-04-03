# item_stack_signals.py

"""
Iterates over every item in the game and adds it to an (N x 5) cell of constant 
combinators with each value being that item's stack size. Commonly used when 
trying to figure out exactly how many slots need to be allocated in order to
transport x number of items. A tedious process normally is made exceptionally 
simple via script, and because of the dynamic nature of draftsman, this works 
with any set of mods as well as vanilla.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.data import items
from draftsman.entity import ConstantCombinator


def main():
    blueprint = Blueprint()

    count = 0   # Total number of signals
    index = 0   # Signal index in the current combinator
    i = 0       # How many combinators we've added
    x = 0
    y = 0
    combinator = ConstantCombinator(direction = Direction.SOUTH)

    # Iterate over every item in order:
    for item in items.raw:
        # Ignore hidden items/entities
        if "flags" in items.raw[item]:
            if "hidden" in items.raw[item]["flags"]:
                continue
        # Keep track of how many signals we've gone through
        count += 1
        # Write the stack size signal
        stack_size = items.raw[item]["stack_size"]
        combinator.set_signal(index, item, stack_size)
        index += 1
        # Once we exceed the current combinator, place it and reset
        if index == 20:
            combinator.id = str(x) + "_" + str(y)
            blueprint.entities.append(combinator)
            i += 1
            y = i % 5
            x = int(i / 5)
            combinator.set_signals(None) # Clear signals
            combinator.tile_position = (x, y)
            index = 0

    # Add the last combinator if partially full
    combinator.id = str(x) + "_" + str(y)
    blueprint.entities.append(combinator)

    # Add connections
    for cx in range(x):
        for cy in range(5):
            here = str(cx) + "_" + str(cy)
            right = str(cx+1) + "_" + str(cy)
            below = str(cx) + "_" + str(cy+1)
            try:
                blueprint.add_circuit_connection("red", here, right)
            except KeyError:
                pass
            try:
                blueprint.add_circuit_connection("red", here, below)
            except KeyError:
                pass

    print(count) # This is mostly for debugging
    #print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":
    main()