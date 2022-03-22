
from draftsman.entity import *
from draftsman.data import entities
from draftsman.constants import *
from draftsman.blueprint import Blueprint, IDList
from draftsman.tile import Tile
from draftsman.warning import OverlappingTilesWarning, DraftsmanWarning
from draftsman import utils
import draftsman.data.tiles as tiles
import draftsman.data.recipes as recipes
from draftsman.data import items
from draftsman.classes import Group

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

    #warnings.simplefilter("ignore", DraftsmanWarning)
    #print(warning_not_filtered(OverlappingTilesWarning))

    # size = 128
    # for j in range(size):
    #     for i in range(size):
    #         blueprint.add_tile("refined-concrete", i, j)
    #         blueprint.add_tile("landfill", i, j)

    # blueprint.add_tile("refined-concrete", 0, 0)
    # blueprint.add_tile("landfill", 0, 0)

    # blueprint.add_tile("refined-concrete", 0, 0)
    # blueprint.add_tile("landfill", -1, -1)
    # #blueprint.remove_tile("refined-concrete", 0, 0)
    # #blueprint.add_tile("landfill", 100, 100)
    # print(blueprint.tile_hashmap.map)
    # print(blueprint.tile_hashmap.get_on_point((-0.5, -0.5)))

    # blueprint.add_entity("decider-combinator", position = [-1, 0], direction = Direction.EAST)
    # results = blueprint.find_entities_filtered(name = "decider-combinator",
    #     area = [[-8, -8], [8, 8]])
    # print(results)

    # aabb1 = [[-1, -1], [1, 1]]
    # aabb2 = [[-0.5, -0.5], [0.5, 0.5]]
    # print(utils.aabb_overlaps_aabb(aabb1, aabb2))

    id_list = IDList()

    id_list.append(Furnace("stone-furnace", position = [1, 1], id = "test"))

    print(id_list[0].id)
    print(id_list["test"])
    id_list[0].id = "something_else"
    print(id_list[0].id)
    print(id_list["something_else"])

    # Checkerboard grid
    
    # furnace = Furnace("electric-furnace")
    # furnace.set_item_request("iron-ore", 100)
    # blueprint.add_entity(furnace)

    # machine = AssemblingMachine("assembling-machine-3")
    # machine.set_recipe("copper-cable")
    # machine.set_item_request("iron-plate", 100)
    # blueprint.add_entity(machine)

    # beacon = Beacon()
    # beacon.set_item_request("steel-plate", 2)
    # blueprint.add_entity(beacon)

    # print(entities.raw["electric-furnace"]["crafting_categories"])
    # print(recipes.categories["smelting"])
    # print(recipes.raw["iron-plate"])
    # for k in entities.raw["electric-furnace"]:
    #     print(k)

    # group = Group(name = "groupname1", position = [10, 10])
    # group.add_entity(Furnace())
    # print(group)
    # print(Furnace())

    # combinator = ArithmeticCombinator()
    # combinator.set_arithmetic_conditions(10, "or")
    # combinator.control_behavior = {
    #     "arithmetic_conditions": {
    #         "first_constant": 10,
    #         "operation": "OR",
    #         "second_constant": 0
    #     }
    # }
    # blueprint.add_entity(combinator)

    print(blueprint)
    print(blueprint.to_string())

    pass


if __name__ == "__main__":
    main()