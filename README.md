# factorio-draftsman

![A logo generated with 'examples/draftsman_logo.py'](https://github.com/redruin1/factorio-draftsman/raw/main/docs/img/logo.png)

[![PyPI version](https://badge.fury.io/py/factorio-draftsman.svg)](https://badge.fury.io/py/factorio-draftsman)
[![Documentation Status](https://readthedocs.org/projects/factorio-draftsman/badge/?version=latest)](https://factorio-draftsman.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/redruin1/factorio-draftsman/branch/main/graph/badge.svg?token=UERAOXVTO1)](https://codecov.io/gh/redruin1/factorio-draftsman)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

`factorio-draftsman` is a Python module for creating and editing blueprints for the game [Factorio](https://factorio.com/).

```python
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
    direction=Direction.EAST
)
blueprint.entities.append(
    "decider-combinator",
    id="clock",
    tile_position=(0, 3),
    direction=Direction.EAST,
)    
blueprint.entities.append(
    "small-lamp", 
    id="blinker", 
    tile_position=(2, 3)
)

# Use IDs for ease of access on complex blueprints
constant: ConstantCombinator = blueprint.entities["constant"]
constant.add_section().set_signal(index=0, name="signal-red", count=1)

clock: DeciderCombinator = blueprint.entities["clock"]
clock.conditions = [
    DeciderCombinator.Condition(
        first_signal="signal-red",
        comparator="<=",
        constant=60
    )
]
clock.outputs = [
    DeciderCombinator.Output(
        signal="signal-red"
    )
]

blinker: Lamp = blueprint.entities["blinker"]
blinker.circuit_enabled = True
blinker.set_circuit_condition("signal-red", "=", 60)
blinker.use_colors = True

# Sophisticated relationship handling with Associations
blueprint.add_circuit_connection( # Constant to input of decider
    color="green", 
    entity_1="constant", 
    entity_2="clock"
)
blueprint.add_circuit_connection( # Input of decider to output of decider
    color="red", entity_1="clock", side_1="input", entity_2="clock", side_2="output"
)
blueprint.add_circuit_connection( # Output of decider to lamp
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
asm_machines: list[AssemblingMachine] = blueprint.find_entities_filtered(type="assembling-machine")
assert len(asm_machines) == 3
for asm_machine in asm_machines:
    asm_machine.recipe = "low-density-structure"

# Every blueprintable type is supported
blueprint_book = BlueprintBook()
blueprint_book.blueprints = [blueprint, UpgradePlanner(), DeconstructionPlanner()]

print(blueprint_book.to_string(version=(2, 0)))  # Blueprint string to import into Factorio
```

![The output from the above script.](examples/images/readme_output.PNG)

# Overview

Simply put, Draftsman attempts to provide a universal solution to the task of creating and manipulating Factorio blueprint strings, which are compressed text strings used by players to share their constructions easily with others.
Draftsman allows users to programmatically create these strings via script, allowing for designs that would normally be too tedious to design by hand, such as combinator computer compilers, image-to-blueprint converters, pumpjack placers, as well as any other complex or repetitive design better suited for a computer's touch.

For a user-friendly timeline of how this project came about, as well as some pretty illustrations of it's capabilities, [you can read an article](https://alt-f4.blog/ALTF4-61/) written for the amazing fan-run community spotlight website [Alt-F4](https://alt-f4.blog/).

For more information on what exactly Draftsman is and does, as well as its intended purpose and philosophy, [you can read the documentation here](https://factorio-draftsman.readthedocs.io/en/latest/index.html).

For more examples on what exactly you can do with Draftsman, take a look at the [examples folder](https://github.com/redruin1/factorio-draftsman/tree/main/examples), which is organized into different categories for ease of navigation.

## Features
* Compatible with Python >= 3.10
* Compatible with all versions of Factorio >= 1.0.0
* Compatible with Factorio mods(!)
* Well documented
* Intuitive and flexible API
* Useful constructs for ease-of-use:
    * Give entities unique string IDs to make association between entities easier
    * Filter entities from blueprints by type, region and other parameters [just like Factorio's own API](https://lua-api.factorio.com/latest/classes/LuaSurface.html#find_entities_filtered)
    * Entities are categorized and organized within `draftsman.data` for easy and flexible iteration
    * Group entities together and manipulate them all as one unit
* Verbose Errors and Warnings (["Factorio-safety" and "Factorio-correctness"](https://factorio-draftsman.readthedocs.io/en/latest/concepts/validation.html))
* Expansive and rigorous test suite

# Installation

## For Users:

```
pip install factorio-draftsman
```

This will install the latest version of Draftsman with a copy of pre-generated data from [`factorio-data`](https://github.com/wube/factorio-data) (typically the latest stable version). Having a copy of the game (installed or at all) is not necessary to use Draftsman, but Draftsman can also use data from your user-specific installation.

If Factorio updates in-between Draftsman releases, or if you want to update your environment to support mods, then you can modify your Draftsman installation by running the companion command-line tool `draftsman`:

```
draftsman factorio-version latest
draftsman --mods-path "path/to/mods/folder" update
```

For more information on how to use this tool, you can run `draftsman -h` or see it's documentation [here](https://factorio-draftsman.readthedocs.io/en/latest/reference/environment/script.html).

## For Developers

Clone the repository using your preferred method (making sure submodules are populated) and navigate to the root of the newly cloned repository:

```
git clone --recurse-submodules https://github.com/redruin1/factorio-draftsman.git
cd factorio-draftsman
```

Create a virtual environment of your personal flavor and enter inside of it. If you are looking to contribute to Draftsman however, it's recommended that you use [`uv`](https://github.com/astral-sh/uv) since most of the CI tools use it:

```perl
pip install uv # or via pipx or standalone script, see uv docs
uv venv
```

Install the package in editable mode, alongside the `dev` dependency group (requires modern pip):

```
pip install -e .
pip install --group dev
```

You should now be able to run the test suite with [`pytest`](https://docs.pytest.org/en/stable/#):

```
python -m pytest test -Werror -vv
```

Or - more succinctly - using [`coverage`](https://coverage.readthedocs.io/en/latest/):

```
coverage run
```

To run a mock CI against all supported Python versions, run [`tox`](https://tox.wiki/en/4.27.0/):

```
tox
```

However, Draftsman (>= 3.0) also provides a [`justfile`](https://github.com/casey/just) which has a number of recipes which make contributing much easier. 
Type `just` to see a list of all options:

```perl
Available recipes:
    ci              # Run 'lint + test + report-coverage'
    ci-all          # Run 'lint + test-all + report-coverage'
    lint *args      # Run black and ruff
    test            # Run test suite against {current Factorio version, all Python versions}
    test-all        # Run test suite against {all Factorio versions, latest Python version} (LONG)
    report-coverage # Combine all coverage files and create HTML report
    benchmark       # Run benchmark tests and save profiles for this Draftsman version
```

Note that testing currently is only guaranteed to pass with a vanilla [environment](https://factorio-draftsman.readthedocs.io/en/latest/concepts/environment.html).

A html-browsable coverage report can be generated with:

```
coverage html
```

To build + check documentation locally:

```
cd docs
make clean
make doctest
make html
```

and then navigate to `docs/build/index.html` to view.

--------------------------------------------------------------------------------

# Contributing

All support is welcome, whether it be finding/fixing bugs, improving mod compatibility, adding useful features, improving existing documentation, adding new examples, or anything in-between. Check [`TODO.md`](TODO.md) for a list of features which are (eventually) planned for a future version of Draftsman.

Bugs are tracked on the issue page; If you have an issue that's affecting you, search here for your issue and create a new one if it's not there. Feature requests also belong here if you can make a strong case for it's inclusion into the project.

If you have a feature request that isn't currently on the TODO list and you believe it might be a good fit for the project, but you're not absolutely sure if it belongs or how it should be implemented into Draftsman, start a [discussion thread here](https://github.com/redruin1/factorio-draftsman/discussions/categories/ideas). If a discussed feature is accepted, it should be added to the TODO list and tracked on the issues page. Questions on how to use Draftsman are also recommended to live in the discussions channel.

If you want to contribute, fork the project and dive in. When you're ready, submit a PR with the changes towards the intended branch, describing what exactly the changes intend to do (linking against any relevant issues if necessary). If all checks pass, you can expect the PR to merged in a (relatively) timely manner and pushed to the next minor or major version.

If Draftsman is useful to you or any of your projects (and you would like to grease it's continued development) then you can send me a dollar or two here:

<a href='https://ko-fi.com/L3L3XMUF' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi5.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>