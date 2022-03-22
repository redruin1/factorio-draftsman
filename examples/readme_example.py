# readme.py

"""
Example program used in the readme. Used to make sure the example provided 
actually works.
"""

import draftsman as factorio

blueprint = factorio.Blueprint()
blueprint.set_label("Example")
blueprint.set_description("A blueprint for the readme.")
blueprint.set_version(1, 0) # 1.0

# Create a alt-mode combinator string
test_string = "testing"
for i, c in enumerate(test_string):
    constant_combinator = factorio.ConstantCombinator()
    constant_combinator.set_tile_position(i, 0)
    letter_signal = "signal-{}".format(c.upper())
    constant_combinator.set_signal(0, letter_signal, 0)
    blueprint.add_entity(constant_combinator)

# Create a simple clock and blinking light
constant = factorio.ConstantCombinator()
constant.set_tile_position(-1, 3)
constant.set_direction(factorio.Direction.EAST)
constant.set_signal(0, "signal-red", 1)
blueprint.add_entity(constant, id = "constant")

# Flexible ways to specify entities
blueprint.add_entity(
    "decider-combinator", id = "clock",
    position = [0, 3],
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
blueprint.add_entity("small-lamp", id = "blinker")
blinker = blueprint.find_entity_by_id("blinker")
blinker.set_tile_position(2, 3)
blinker.set_enabled_condition("signal-red", "=", 60)
blinker.set_use_colors(True)

blueprint.add_circuit_connection("green", "constant", "clock")
blueprint.add_circuit_connection("red", "clock", "clock", 1, 2)
blueprint.add_circuit_connection("green", "clock", "blinker", 2, 1)

# Iterables in the way you'd expect
for entity in blueprint.entities:
    print(entity)

# Factorio API filter capabilities
ccs = blueprint.find_entities_filtered(name = "constant-combinator")
assert len(ccs) == len(test_string) + 1

blueprint_book = factorio.BlueprintBook(blueprints = [blueprint])

print(blueprint_book)               # Pretty printing using json
print(blueprint_book.to_string())   # Blueprint string