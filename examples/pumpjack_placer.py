# pumpjack_placer.py

"""
Creates a copy of the massive overlapping pumpjack blueprint found here:
https://factorioprints.com/view/-LbygJLCDgaBJqsMPqUJ
Can be expanded as much as you dare.

TODO: speed this thing up, shouldn't take 10+ seconds
"""

import warnings
from draftsman.blueprintable import Blueprint
from draftsman.warning import OverlappingObjectsWarning


def main():
    blueprint = Blueprint()
    blueprint.label = "Huge Pumpjacks"
    blueprint.icons = ["pumpjack"]

    # Do this unless you want your stdout flooded with warnings
    warnings.simplefilter("ignore", OverlappingObjectsWarning)

    dim = 64
    for y in range(dim):
        for x in range(dim):
            blueprint.entities.append("pumpjack", position=[x, y])

    # If you want to see all the OverlappingObjectsWarning, do this:
    #for warning in blueprint.inspect():
    #    warning.show()

    print(blueprint.to_string())


if __name__ == "__main__":
    main()
