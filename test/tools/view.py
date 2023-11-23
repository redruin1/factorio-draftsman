# view.py

"""
View a blueprint string's contents. Used for development; useful for
determining the exact contents of a blueprint string as exported by Factorio.
"""

import json

from draftsman import utils


if __name__ == "__main__":
    bpstring = input()
    blueprint_dict = utils.string_to_JSON(bpstring)
    print(json.dumps(blueprint_dict, indent=2))
