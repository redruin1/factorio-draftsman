"""
Example code from the readme, encoded as a file and integrated into CI so it
continues to work across versions.
"""

from draftsman.blueprintable import *
from draftsman.constants import Direction
from draftsman.entity import *

# Create new Blueprints from scratch
blueprint = Blueprint()
blueprint.label = "Example"
blueprint.description = "A blueprint for the readme."
blueprint.version = (2, 0)  # Factorio version 2.0

# Add new entities and configure them procedurally
test_string = "readme"
for i, char in enumerate(test_string):
    signal_string = "signal-{}".format(char.upper())

    constant_combinator = ConstantCombinator(tile_position=(i - 2, 0))
    section = constant_combinator.add_section()
    section.set_signal(
        index=0,
        name=signal_string,
        count=0,
    )
    blueprint.entities.append(constant_combinator)

    display_panel = DisplayPanel(tile_position=(i - 2, 1))
    display_panel.icon = signal_string
    display_panel.always_show_in_alt_mode = True
    blueprint.entities.append(display_panel)

# Flexible ways to specify entities
blueprint.entities.append(
    "constant-combinator",
    id="constant",
    tile_position=(-1, 3),
    direction=Direction.EAST,
)
blueprint.entities.append(
    "decider-combinator",
    id="clock",
    tile_position=(0, 3),
    direction=Direction.EAST,
)
blueprint.entities.append("small-lamp", id="blinker", tile_position=(2, 3))

# Use IDs for ease of access on complex blueprints
constant: ConstantCombinator = blueprint.entities["constant"]
constant.add_section().set_signal(index=0, name="signal-red", count=1)

clock: DeciderCombinator = blueprint.entities["clock"]
clock.conditions = [
    DeciderCombinator.Condition(first_signal="signal-red", comparator="<=", constant=60)
]
clock.outputs = [DeciderCombinator.Output(signal="signal-red")]

blinker: Lamp = blueprint.entities["blinker"]
blinker.circuit_enabled = True
blinker.set_circuit_condition("signal-red", "=", 60)
blinker.use_colors = True

# Sophisticated relationship handling with Associations
blueprint.add_circuit_connection(  # Constant to input of decider
    color="green", entity_1="constant", entity_2="clock"
)
blueprint.add_circuit_connection(  # Input of decider to output of decider
    color="red", entity_1="clock", side_1="input", entity_2="clock", side_2="output"
)
blueprint.add_circuit_connection(  # Output of decider to lamp
    color="green", entity_1="clock", side_1="output", entity_2="blinker", side_2="input"
)

# Import compressed blueprints
bp_string = """0eNqllGFrwyAQhv/LfdZhkmUl+SujDJNc2wO9FLVjXfC/z2TZBisrLH4S9d7n3pdDJ+jMBc+OOEA7AfUje2ifJ/B0ZG3mM9YWoQXtPdrOEB+l1f2JGGUFUQDxgG/QFnEvADlQIPwkLJvrC19shy4ViLskAefRJ/HIc88EVA+1gOuyxpkdyKzgX4WyWOpkEb87ODwk6iBP+l27QaZQvcOA0uAhJM83CJVNyPewxlC5KVRuCJWdIXsS2YPIn0N5S/iS/u37n6JNnVZ/1RZ/1RZ/d0XpYVJAm+5+/hEBr+j8gqmfyuaxaeqdKutdU8b4AbwVejE="""

# Group entities together and treat them all as one unit
group = Group.from_string(bp_string)
for i in range(3):
    blueprint.groups.append(group, position=(i * 4 - 3, 7))

# Quickly query Blueprints by region or contents
ccs = blueprint.find_entities_filtered(name="constant-combinator")
assert len(ccs) == len(test_string) + 1
asm_machines: list[AssemblingMachine] = blueprint.find_entities_filtered(
    type="assembling-machine"
)
assert len(asm_machines) == 3
for asm_machine in asm_machines:
    asm_machine.recipe = "low-density-structure"

# Every blueprintable type is supported
blueprint_book = BlueprintBook()
blueprint_book.blueprints = [blueprint, UpgradePlanner(), DeconstructionPlanner()]

print(
    blueprint_book.to_string(version=(2, 0))
)  # Blueprint string to import into Factorio
