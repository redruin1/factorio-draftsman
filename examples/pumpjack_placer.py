# pumpjack_placer.py

"""
Creates a copy of the massive overlapping pumpjack blueprint found here:
https://factorioprints.com/view/-LbygJLCDgaBJqsMPqUJ
Can be expanded as much as you dare.
"""

# TODO: speed this thing up, shouldn't take 10+ seconds

from draftsman.blueprintable import Blueprint
from draftsman.constants import ValidationMode
from draftsman.warning import OverlappingObjectsWarning
import warnings


def main():
    blueprint = Blueprint(validate_assignment=ValidationMode.NONE)
    blueprint.label = "Huge Pumpjacks"
    blueprint.set_icons("pumpjack")

    # We intentionally create a blueprint which has overlapping entities, so we
    # suppress this warning here
    warnings.simplefilter("ignore", OverlappingObjectsWarning)

    dimension = 64
    for y in range(dimension):
        for x in range(dimension):
            blueprint.entities.append("pumpjack", position=[x, y])

    # If you want to see all the OverlappingObjectsWarning, do this:
    # for warning in blueprint.inspect():
    #    warning.show()

    print(blueprint.to_string())


if __name__ == "__main__":
    main()
