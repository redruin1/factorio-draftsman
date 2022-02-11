# view.py

import json

from factoriotools import blueprint
from factoriotools import utils

if __name__ == "__main__":
    bpstring = input()
    # Either
    #json_dict = blueprint.string_2_JSON(bpstring)
    #print(json.dumps(json_dict, indent=4))
    # Or
    #blueprintable = blueprint.get_blueprintable_from_string(bpstring)
    #print(blueprintable)
    blueprint_dict = utils.string_2_JSON(bpstring)
    print(json.dumps(blueprint_dict, indent=2))