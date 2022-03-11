
from draftsman.entity import *
from draftsman.data import entities
from draftsman.constants import *
from draftsman.blueprint import Blueprint
from draftsman.warning import ModuleLimitationWarning
import draftsman.data.tiles as tiles
import draftsman.data.recipes as recipes

#import pyperclip
import json
import enum
import warnings

def main():
    #print(json.dumps(entities.raw["constant-combinator"], indent=2))
    # print(entities.raw["medium-electric-pole"])
    # for k in entities.raw["medium-electric-pole"]:
    #     print(k)
    
    blueprint = Blueprint()

    # machine = AssemblingMachine("assembling-machine-3")
    # machine.set_recipe("accumulator")
    # machine.set_item_request("productivity-module-3", 1)

    # blueprint.add_entity(machine)

    # print(machine)
    # print(blueprint.to_string())

    # for tile in tiles.raw:
    #     print()
    #     for key in tiles.raw[tile]:
    #         print(key)

    # speaker = ProgrammableSpeaker()
    # speaker.set_instrument("alarms")

    # speaker.set_note("siren")

    # blueprint.add_entity(speaker)

    # test_dict = {
    #     "position": [1, 1],
    #     "name": "wooden-chest",
    # }

    # entity = new_entity(**test_dict)

    # print(entity)
    # print(type(entity))

    # blueprint.add_entity(entity)

    # print(blueprint.to_string())

    # print(entities.programmable_speakers)

    speaker= ProgrammableSpeaker("programmable-speaker")
    speaker.set_instrument(0)

    #print(speaker.instruments)

    pass


if __name__ == "__main__":
    main()