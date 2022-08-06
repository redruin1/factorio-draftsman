# view.py

"""
View a blueprint string's contents. Used for development; useful for
determining the exact contents of a blueprint string as exported by Factorio.
"""

import json

from draftsman import utils


if __name__ == "__main__":
    bpstring = input()
    # Either
    # json_dict = blueprint.string_2_JSON(bpstring)
    # print(json.dumps(json_dict, indent=4))
    # Or
    # blueprintable = blueprint.get_blueprintable_from_string(bpstring)
    # print(blueprintable)
    blueprint_dict = utils.string_to_JSON(bpstring)
    print(json.dumps(blueprint_dict, indent=2))
