# readme.py

"""
Example program used in the readme. Used to make sure the example provided 
actually works.
"""

import draftsman as factorio

blueprint = factorio.Blueprint()
blueprint.label = "Example"
blueprint.description = "A blueprint for the readme."
blueprint.version = (1, 0) # 1.0

# Create a alt-mode combinator string
test_string = "testing"
for i, c in enumerate(test_string):
    constant_combinator = factorio.ConstantCombinator()
    constant_combinator.tile_position = (i, 0)
    letter_signal = "signal-{}".format(c.upper())
    constant_combinator.set_signal(index = 0, signal = letter_signal, count = 0)
    blueprint.entities.append(constant_combinator)

# Create a simple clock and blinking light
constant = factorio.ConstantCombinator()
constant.tile_position = (-1, 3)
constant.direction = factorio.Direction.EAST
constant.set_signal(0, "signal-red", 1)
constant.id = "constant"
blueprint.entities.append(constant)

# Flexible ways to specify entities
blueprint.entities.append(
    "decider-combinator", id = "clock",
    tile_position = [0, 3],
    direction = factorio.Direction.EAST,
    control_behavior = {
        "decider_conditions": {
            "first_signal": "signal-red",
            "comparator": "<=",
            "constant": 60,
            "output_signal": "signal-red",
            "copy_count_from_input": True
        }
    }
)

# Use IDs to keep track of complex blueprints
blueprint.entities.append("small-lamp", id = "blinker", tile_position = (2, 3))
blinker = blueprint.entities["blinker"]
blinker.set_enabled_condition("signal-red", "=", 60)
blinker.use_colors = True

blueprint.add_circuit_connection("green", "constant", "clock")
blueprint.add_circuit_connection("red", "clock", "clock", 1, 2)
blueprint.add_circuit_connection("green", "clock", "blinker", 2, 1)

# Factorio API filter capabilities
ccs = blueprint.find_entities_filtered(name = "constant-combinator")
assert len(ccs) == len(test_string) + 1

blueprint_book = factorio.BlueprintBook()
blueprint_book.blueprints = [blueprint]

print(blueprint_book)               # Pretty printing using json
print(blueprint_book.to_string())   # Blueprint string