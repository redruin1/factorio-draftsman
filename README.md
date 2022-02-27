# factorio-draftsman

image

A draftsman is a kind of artist that specializes in creating technical drawings across many engineering disciplines, including architectural, mechanical, and electrical.
Similarly, `factorio-draftsman` is a Python module for creating and editing blueprints for the game [Factorio](https://factorio.com/).

```python
import draftsman as factorio

blueprint = factorio.Blueprint()
blueprint.set_label("Example")
blueprint.set_description("A blueprint for the readme.")
blueprint.set_version(1, 0) # 1.0

# Create a alt-mode combinator string
test_string = "testing"
for i, c in enumerate(test_string):
    constant_combinator = factorio.ConstantCombinator()
    constant_combinator.set_grid_position(i, 0)
    letter_signal = "signal-{}".format(c.upper())
    constant_combinator.set_signal(0, letter_signal, 0)
    blueprint.add_entity(constant_combinator)

# Create a simple clock and blinking light
constant = factorio.ConstantCombinator()
constant.set_grid_position(-1, 3)
constant.set_direction(factorio.EAST)
constant.set_signal(0, "signal-red", 1)
blueprint.add_entity(constant, id = "constant")

# Flexible ways to specify entities
blueprint.add_entity(
    "decider-combinator", id = "clock",
    position = [0, 3],
    direction = factorio.EAST,
    control_behavior = {
        "decider_conditions": {
            "first_signal": "signal-red",
            "comparator": "<=",
            "second_constant": 60,
            "output_signal": "signal-red",
            "copy_count_from_input": True
        }
    }
)

# Use IDs to keep track of complex blueprints
blueprint.add_entity(lamp, id = "blinker")
blinker = blueprint.find_entity_by_id("blinker")
blinker.set_grid_position(2, 3)
blinker.set_enabled_condition("signal-red", "=", 60)
blinker.set_use_colors(True)

blueprint.add_circuit_connection(color="green", id1="constant", id2="clock", side1=1, side2=1)
blueprint.add_circuit_connection("red", "clock", "clock", 1, 2)
blueprint.add_circuit_connection("green", "clock", "blinker", 2, 1)

# Iterables in the way you'd expect
for entity in blueprint.entities:
    print(entity)

# Factorio API filter capabilities
ccs = blueprint.find_entities_filtered(type = "constant-combinator")
assert len(ccs) == len(test_string) + 1

blueprint_book = factorio.BlueprintBook(blueprints = [blueprint])

print(blueprint_book)               # Pretty printing using `json`
print(blueprint_book.to_string())   # Blueprint string
```
For more examples, see the [examples folder](https://github.com/redruin1/factorio-draftsman/tree/main/examples).

--------------------------------------------------------------------------------
## Table of Contents

 * [Overview](#overview)
    * [Features](#features)
 * [Usage](#usage)
    * [Installation](#installation)
    * [Testing](#testing-with-unittesthttpsdocspythonorg3libraryunittesthtml)
    * [Coverage](#coverage-with-coveragehttpscoveragereadthedocsioen632)

## Overview
### Features
* Compatable with the latest version of Factorio (1.1.53+)
* Well documented
* Intuitive API
* Useful constructs for ease-of-use:
    * Give entities unique string IDs
    * Filter entities from blueprints [just like Factorio's own API](https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_entities_filtered)
    * Collect entities into Groups and move them all at once
    * and more!
* Compatable with mods
* Verbose Errors and Warnings
* Rigorous test suite

--------------------------------------------------------------------------------
## Usage

### Installation:
```
pip install factorio-draftsman
```

### Testing with [unittest](https://docs.python.org/3/library/unittest.html):
```
python -m unittest discover
```

### Coverage with [coverage](https://coverage.readthedocs.io/en/6.3.2/):
```
coverage run
```

Note that testing currently is only *guaranteed* to work with a vanilla install
(no mods).

### How to use mods:

1. Drop the mods you want into the `factorio-mods` folder
2. Run `update_module.py` to reflect any changes made

Both `mod-info.json` and `mod-settings.dat` are recognized by the script, so you
can also just change the settings in either of those and the loading process 
will adjust.

## TODO
* Finish `entity.py`
    * Make sure the Entity classes themselves don't need to be split
    * Extract Instrument data (according to the programmable speaker)
    * Handle 8-way rotation placement a lot better
    * Properly handle defaults to prioritize space a little better
    * Test with mods
    * Errors + Warnings
* Finish `blueprint.py`
    * Big cleaning/refactoring
    * Finish `BlueprintBook`
    * Test with mods
    * Errors + Warnings
* Add extra features
    * **COMPLETE TESTING SUITE**
    * Think about the best way to handle generated data 
    * (Re)Add entity groups and their functionality (EntityLike class)
    * Specify Rails via nodes/beziers instead of manually placing *every* rail
    * Maybe add a `CombinatorCell` EntityLike?
    * Backport / make sure it works with python 2.7 and previous versions of Python 3
* Look into lua binding
    * Some script to convert the Python code, or backport to C and compile 2 libraries?