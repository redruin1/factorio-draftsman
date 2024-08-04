# signal_index.py

"""
Creates a blueprint to convert the numeric value from 1-256 into a unique signal
with a value of 1. The input signal is reserved and specified with the variable
`input_signal`. You can also specify any number of signals to blacklist as well
if you want those signals to be reserved, though using more than 2 (with no 
mods) will result in fewer than 256 signals.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import Direction
from draftsman.entity import (
    ConstantCombinator,
    ArithmeticCombinator,
    DeciderCombinator,
    ElectricPole,
)
from draftsman.data import signals


def main():
    blueprint = Blueprint()

    # Specify the input signal:
    input_signal = "red-wire"

    # Some metadata
    blueprint.label = "Signal Index ({})".format(input_signal)
    blueprint.label_color = (1.0, 0.0, 1.0, 1.0)
    blueprint.icons = ["signal-I", "signal-D"]
    blueprint.description = (
        "Converts the value of {} into a unique unit signal.".format(input_signal)
    )

    # Blacklist desired signals:
    blacklist = []
    # There are 262 valid vanilla signals in the game
    # We can't use the special signals in constant combinators
    blacklist += ["signal-anything", "signal-everything", "signal-each"]
    # And the input signal has to be different by nature of this blueprint
    blacklist += [input_signal]
    # Which leaves us with 2 spare signals that we can choose to avoid
    # (unless you're using mods)
    blacklist += ["green-wire", "signal-info"]

    assert len(blacklist) <= 6

    # First we generate the signal mapping set
    mapping = []

    def add_signals_to_mapping(signals):
        for signal in signals:
            if signal not in blacklist:
                mapping.append(signal)

    add_signals_to_mapping(signals.virtual)  # This maps nicely to the lower nums
    add_signals_to_mapping(signals.item)
    add_signals_to_mapping(signals.fluid)

    # print(mapping)

    # Then we generate the grid of constant combinators
    signal_index = 0
    for y in range(7):
        for x in range(2):
            combinator = ConstantCombinator("constant-combinator")
            combinator.direction = Direction.SOUTH
            combinator.tile_position = (x, -y)
            for i in range(20):
                # Last few signals might not exist
                try:
                    signal_name = mapping[signal_index + i]
                    combinator.set_signal(i, signal_name, signal_index + i + 1)
                except:
                    pass
            combinator.id = str(x) + "_" + str(y)
            blueprint.entities.append(combinator)
            signal_index += 20

    # Connect all the combinators together
    for y in range(7):
        for x in range(2):
            current = str(x) + "_" + str(y)
            target_above = str(x) + "_" + str(y + 1)
            try:
                blueprint.add_circuit_connection("red", current, target_above)
            except KeyError:  # TODO: maybe make a more descriptive error?
                pass
            target_across = str(x + 1) + "_" + str(y)
            try:
                blueprint.add_circuit_connection("red", current, target_across)
            except KeyError:  # Maybe 'MissingEntityWithID'?
                pass

    # Decider
    decider = DeciderCombinator("decider-combinator", tile_position=[0, 1])
    decider.direction = Direction.EAST
    print(decider.collision_set)
    print(decider.tile_width, decider.tile_height)
    decider.set_decider_conditions("signal-each", "=", input_signal, "signal-each")
    decider.copy_count_from_input = False
    decider.id = "decider"
    blueprint.entities.append(decider)

    # Output stabilizer
    stabilizer = ArithmeticCombinator("arithmetic-combinator", tile_position=[0, 2])
    stabilizer.direction = Direction.EAST
    print(stabilizer.collision_set)
    print(stabilizer.tile_width, stabilizer.tile_height)
    stabilizer.set_arithmetic_conditions(-1, "%", input_signal, input_signal)
    stabilizer.id = "stabilizer"
    blueprint.entities.append(stabilizer)

    # Stabilizer offset
    offset = ConstantCombinator("constant-combinator", position=[-1, 2])
    offset.direction = Direction.EAST
    offset.set_signal(0, input_signal, 1)
    offset.id = "offset"
    blueprint.entities.append(offset)

    # (Example) Input combinator
    input = ConstantCombinator("constant-combinator", position=[-4, 1])
    input.direction = Direction.EAST
    input.set_signal(0, input_signal, 15)
    input.id = "input"
    blueprint.entities.append(input)

    # Input pole
    pole = ElectricPole("medium-electric-pole", position=[-3, 1])
    pole.id = "input_pole"
    blueprint.entities.append(pole)
    # Output pole
    pole.tile_position = (4, 1)
    pole.id = "output_pole"
    blueprint.entities.append(pole)
    blueprint.add_power_connection("input_pole", "output_pole")

    # Rest of the circuit connections
    blueprint.add_circuit_connection("red", "0_0", "decider")
    blueprint.add_circuit_connection("red", "offset", "stabilizer")

    blueprint.add_circuit_connection("green", "input", "input_pole")
    blueprint.add_circuit_connection("green", "input_pole", "decider")
    blueprint.add_circuit_connection("green", "decider", "stabilizer")

    blueprint.add_circuit_connection("red", "stabilizer", "decider", 2, 2)
    blueprint.add_circuit_connection("red", "decider", "output_pole", 2, 1)

    # print(blueprint)
    print(blueprint.to_string())


if __name__ == "__main__":  # pragma: no coverage
    main()
