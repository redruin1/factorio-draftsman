# signal_index.py

"""
Creates a blueprint to convert the numeric value from 1-256 into a unique signal
with a value of 1.
"""

# TODO: change the constant combinator bit to a Cell

import factoriotools
from factoriotools.blueprint import Blueprint
from factoriotools.entity import (
    ConstantCombinator, ArithmeticCombinator, DeciderCombinator, ElectricPole
)
from factoriotools.signal_data import *


def main():
    blueprint = Blueprint()

    # Specify the input signal:
    input_signal = "red-wire"

    # Blacklist desired signals:
    blacklist = []
    # There are 262 valid vanilla signals in the game
    # We can't use the special signals in constant combinators
    blacklist += ["signal-anything", "signal-everything", "signal-each"]
    # And the input signal has to be different by nature of this blueprint
    blacklist += [input_signal]
    # Which leaves us with 2 spare signals that we can choose to avoid
    blacklist += ["green-wire", "signal-info"]

    assert len(blacklist) <= 6

    # First we generate the signal mapping set
    mapping = []
    def add_signals_to_mapping(signals):
        for signal in signals:
            if signal not in blacklist:
                mapping.append(signal)

    add_signals_to_mapping(virtual_signals) # This maps nicely to the lower nums
    add_signals_to_mapping(item_signals)
    add_signals_to_mapping(fluid_signals)

    print(mapping)

    # Then we generate the grid of constant combinators
    signal_index = 0
    for y in range(1):
        for x in range(1):
            print("signal_index", signal_index)
            combinator = ConstantCombinator("constant-combinator")
            combinator.set_direction(factoriotools.SOUTH)
            combinator.set_grid_position(x, -y)
            for i in range(20):
                # Last few signals might not exist
                #print("i", i)
                #print(i + signal_index)
                try: 
                    print(signal_index + i)
                    print(mapping[signal_index + i])
                    signal_name = mapping[signal_index + i]
                    combinator.set_signal(i, signal_name, signal_index + i)
                except:
                    #print("error")
                    pass
            
            blueprint.add_entity(combinator, id = str(x) + "_" + str(y))
            signal_index += 20
        pass

    # Create the combinator cell
    #constant_combinator
    
    print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":
    main()