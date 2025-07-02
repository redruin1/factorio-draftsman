# pumpjack_placer.py

"""
Creates a copy of the massive overlapping pumpjack blueprint found here:
https://factorioprints.com/view/-LbygJLCDgaBJqsMPqUJ
Can be expanded as much as you dare.
"""

from draftsman.blueprintable import Blueprint
from draftsman.constants import ValidationMode
import draftsman.validators


def main():
    blueprint = Blueprint()
    blueprint.label = "Huge Pumpjacks"
    blueprint.icons = ["pumpjack"]

    # We turn off validation since we know we're creating an "invalid" blueprint
    with draftsman.validators.set_mode(ValidationMode.DISABLED):
        dimension = 64
        for y in range(dimension):
            for x in range(dimension):
                blueprint.entities.append("pumpjack", tile_position=(x, y))

    print(blueprint.to_string())


if __name__ == "__main__":
    main()
