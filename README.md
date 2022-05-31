# factorio-draftsman

![A logo generated with 'examples/draftsman_logo.py'](https://github.com/redruin1/factorio-draftsman/blob/main/docs/img/logo.png)

[![Documentation Status](https://readthedocs.org/projects/factorio-draftsman/badge/?version=latest)](https://factorio-draftsman.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/redruin1/factorio-draftsman/branch/main/graph/badge.svg?token=UERAOXVTO1)](https://codecov.io/gh/redruin1/factorio-draftsman)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A 'draftsman' is a kind of artist that specializes in creating technical drawings across many engineering disciplines, including architectural, mechanical, and electrical.
Similarly, `factorio-draftsman` is a Python module for creating and editing blueprints for the game [Factorio](https://factorio.com/).

```python
from draftsman.blueprintable import Blueprint, BlueprintBook
from draftsman.constants import Direction
from draftsman.entity import ConstantCombinator

blueprint = Blueprint()
blueprint.label = "Example"
blueprint.description = "A blueprint for the readme."
blueprint.version = (1, 0)  # 1.0

# Create a alt-mode combinator string
test_string = "testing"
for i, c in enumerate(test_string):
    constant_combinator = ConstantCombinator()
    constant_combinator.tile_position = (i, 0)
    letter_signal = "signal-{}".format(c.upper())
    constant_combinator.set_signal(index=0, signal=letter_signal, count=0)
    blueprint.entities.append(constant_combinator)

# Create a simple clock and blinking light
constant = ConstantCombinator()
constant.tile_position = (-1, 3)
constant.direction = Direction.EAST
constant.set_signal(0, "signal-red", 1)
constant.id = "constant"
blueprint.entities.append(constant)

# Flexible ways to specify entities
blueprint.entities.append(
    "decider-combinator",
    id="clock",
    tile_position=[0, 3],
    direction=Direction.EAST,
    control_behavior={
        "decider_conditions": {
            "first_signal": "signal-red",
            "comparator": "<=",
            "constant": 60,
            "output_signal": "signal-red",
            "copy_count_from_input": True,
        }
    },
)

# Use IDs to keep track of complex blueprints
blueprint.entities.append("small-lamp", id="blinker", tile_position=(2, 3))
blinker = blueprint.entities["blinker"]
blinker.set_circuit_condition("signal-red", "=", 60)
blinker.use_colors = True

blueprint.add_circuit_connection("green", "constant", "clock")
blueprint.add_circuit_connection("red", "clock", "clock", 1, 2)
blueprint.add_circuit_connection("green", "clock", "blinker", 2, 1)

# Factorio API filter capabilities
ccs = blueprint.find_entities_filtered(name="constant-combinator")
assert len(ccs) == len(test_string) + 1

blueprint_book = BlueprintBook()
blueprint_book.blueprints = [blueprint]

print(blueprint_book)  # Pretty printing using json
print(blueprint_book.to_string())  # Blueprint string
```
--------------------------------------------------------------------------------

## Overview
Simply put, Draftsman attempts to provide a universal solution to the task of creating and manipulating Factorio blueprint strings, which are compressed text strings used by players to share their constructions easily with others.
Draftsman allows users to programmatically create these strings via script, allowing for designs that would normally be too tedious to design by hand, such as combinator computer compilers, image-to-blueprint converters, pumpjack placers, as well as any other complex or repetitive design better suited for a computer's touch.

For a user-friendly timeline of how this project came about, as well as some pretty illustrations of it's capabilities, [you can read an article](https://alt-f4.blog/ALTF4-61/) written for the amazing fan-run community spotlight website [Alt-F4](https://alt-f4.blog/).

For more information on what exactly Draftsman is and does, as well as its intended purpose and philosophy, [you can read the documentation here](https://factorio-draftsman.readthedocs.io/en/latest/index.html).

For more examples on what exactly you can do with draftsman, take a look at the [examples folder](https://github.com/redruin1/factorio-draftsman/tree/main/examples).

### Features
* Compatible with the latest versions of Python 2 and 3
* Compatible with the latest versions of Factorio (1.0+)
* Compatible with Factorio mods(!)
* Well documented
* Intuitive and flexible API
* Useful constructs for ease-of-use:
    * Give entities unique string IDs to make association between entities easier
    * Filter entities from blueprints by type, region and other parameters [just like Factorio's own API](https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_entities_filtered)
    * Entities are categorized and organized within `draftsman.data` for easy and flexible iteration
    * Group entities together and manipulate them all as one unit
* Verbose Errors and Warnings ("Factorio-safety" and "Factorio-correctness")
* Expansive and rigorous test suite

--------------------------------------------------------------------------------
## Usage

### Installation:
To install the module from PyPI:
```
pip install factorio-draftsman
```
Then, to perform first time setup run
```
draftsman-update
```
Note that the `draftsman-update` command must be run at least once before use to ensure the module is properly setup.
Currently I'm looking into solutions to have this command automatically run on install, but for now it must be manually run.

--------------------------------------------------------------------------------
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

--------------------------------------------------------------------------------
### How to use mods:

1. Navigate to the package's installation location
2. Drop the mods you want into the `factorio-mods` folder
3. Run `draftsman-update` to reflect any changes made

`draftsman-update` can also be called in script via the method `draftsman.env:update()` if you want to change the mod list on the fly:
```python
# my_update_script.py
from draftsman.env import update
update() # equivalent to calling 'draftsman-update' from the command line
```

Both `mod-info.json` and `mod-settings.dat` are recognized by the script, so you
can also just change the settings in either of those and the loading process 
will adjust as well.

## TODO
* Maybe switch to `setup.cfg` instead of `setup.py`?
* Figure out exactly what determines if an `Entity` is flip-able or not
* Split documentation from docstrings so that each function has a more readable example
* RailPlanner (specify rail paths via turtle-like commands)
* Custom `data.raw` extraction and formatting?
* Maybe integrate defaults for more succinct blueprint strings?
* Look into Lua bindings via backport to C