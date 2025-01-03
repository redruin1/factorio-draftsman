# factorio-draftsman

![A logo generated with 'examples/draftsman_logo.py'](https://github.com/redruin1/factorio-draftsman/raw/main/docs/img/logo.png)

[![PyPI version](https://badge.fury.io/py/factorio-draftsman.svg)](https://badge.fury.io/py/factorio-draftsman)
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
print(blueprint_book.to_string())  # Blueprint string to import into Factorio
```
--------------------------------------------------------------------------------

## Overview
Simply put, Draftsman attempts to provide a universal solution to the task of creating and manipulating Factorio blueprint strings, which are compressed text strings used by players to share their constructions easily with others.
Draftsman allows users to programmatically create these strings via script, allowing for designs that would normally be too tedious to design by hand, such as combinator computer compilers, image-to-blueprint converters, pumpjack placers, as well as any other complex or repetitive design better suited for a computer's touch.

For a user-friendly timeline of how this project came about, as well as some pretty illustrations of it's capabilities, [you can read an article](https://alt-f4.blog/ALTF4-61/) written for the amazing fan-run community spotlight website [Alt-F4](https://alt-f4.blog/).

For more information on what exactly Draftsman is and does, as well as its intended purpose and philosophy, [you can read the documentation here](https://factorio-draftsman.readthedocs.io/en/latest/index.html).

For more examples on what exactly you can do with Draftsman, take a look at the [examples folder](https://github.com/redruin1/factorio-draftsman/tree/main/examples).

### Features
* Compatible with all versions of Python >= 3.7
* Compatible with the latest versions of Factorio (1.0.0+)
* Compatible with Factorio mods(!)
* Well documented
* Intuitive and flexible API
* Useful constructs for ease-of-use:
    * Give entities unique string IDs to make association between entities easier
    * Filter entities from blueprints by type, region and other parameters [just like Factorio's own API](https://lua-api.factorio.com/latest/LuaSurface.html#LuaSurface.find_entities_filtered)
    * Entities are categorized and organized within `draftsman.data` for easy and flexible iteration
    * Group entities together and manipulate them all as one unit
* Verbose Errors and Warnings (["Factorio-safety"](TODO) and ["Factorio-correctness"](TODO))
* Expansive and rigorous test suite

--------------------------------------------------------------------------------

## Usage

### Installation:
```
pip install factorio-draftsman
```

This will install the latest version of Draftsman with a set of pre-generated data from the latest version of vanilla Factorio.

If you want to have the same data validation that Draftsman provides for vanilla data with mods as well, you can re-generate this data with the command line tool `draftsman-update`, which is described in detail [here](TODO).

### Testing with [unittest](https://docs.python.org/3/library/unittest.html):
```
python -m unittest discover
```

Note that testing currently is only *guaranteed* to work with a vanilla install.

### Coverage with [coverage](https://coverage.readthedocs.io/en/6.3.2/):
```
coverage run
```

--------------------------------------------------------------------------------

### How to use mods with Draftsman:

Determine where your mods are installed; you can either copy the mods you want into the local `site-packages/draftsman/factorio-mods` folder where Draftsman is installed (which it looks in by default), or you can specify an external path with the `-p` or `--path` argument which can point to your Factorio mods folder or anywhere else convenient.
Then, simply call `draftsman-update` or `draftsman-update --path some/path/to/mods` to automatically update the data associated with that Draftsman installation.

`draftsman-update` can also be called in script via the method `draftsman.env:update()` if you want to change the mod list on the fly:
```python
# my_update_script.py
from draftsman.env import update
update(verbose=True, path="some/path") # equivalent to 'draftsman-update -v -p some/path'
```

Both `mod-info.json` and `mod-settings.dat` are recognized by `draftsman-update`, so you can change the settings in either of those and the loading process will adjust as well.

--------------------------------------------------------------------------------

## Contributing

Draftsman is a large and expansive project, intended to be used by as many people as possible. As such, it is a difficult project to maintain by myself. All support is welcome, whether it be finding/fixing bugs, improving mod compatibility, adding features, improving documentation, adding examples, or anything in-between. I maintain a [`TODO.md`](TODO.md) list which contains all the features that I'm currently planning on implementing (eventually, at least).

Bugs are tracked on the issue page; If you have an issue that's affecting you, search here for your issue and create a new one if it's not there.

If you have a feature request that is on the TODO list, or that you firmly believe belongs in Draftsman and you have a working prototype, then the issues page is also the place for that.

If you have a feature request that isn't currently on the TODO list and you believe it might be a good fit for the project, but you're not absolutely sure if it belongs or how it should be implemented into Draftsman, start a [discussion thread here](https://github.com/redruin1/factorio-draftsman/discussions/categories/ideas). If a discussed feature is accepted, it will get added to the TODO list and tracked on the issues page. 

If you want to contribute, read [CONTRIBUTING.md] first, fork the project, and dive in. When you're ready, submit a PR with the changes towards the intended branch, describing what exactly the changes intend to do (linking against any relevant issues if necessary). If all checks pass, you can expect the PR to merged in a (relatively) timely manner and pushed to the next minor or major version.