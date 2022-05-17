from draftsman.blueprintable import Blueprint
from draftsman.entity import *
from draftsman.data import modules, entities

import json


blueprint = Blueprint()

# turret = Turret("gun-turret")
# turret.set_item_requests({"piercing-rounds-magazine": 200})
# blueprint.entities.append(turret)

# turret.tile_position = (2, 0)
# turret.set_item_requests({"piercing-rounds-magazine": 200})
# blueprint.entities.append(turret)

# turret.tile_position = (4, 0)
# turret.set_item_requests({"uranium-rounds-magazine": 200})
# blueprint.entities.append(turret)

# artillery_turret = Turret("artillery-turret", tile_position = (6, 0))
# artillery_turret.set_item_requests({"artillery-shell": 1})
# blueprint.entities.append(artillery_turret)

# blueprint.label = "Turrets: Ammo item request"
# blueprint.description = "Each turret that requires ammo preloaded with a full stack of ammo when placed."

# machine = AssemblingMachine("assembling-machine-3")
# machine.recipe = "electronic-circuit"
# machine.set_item_requests({"copper-cable": 200})
# blueprint.entities.append(machine)

# blueprint.label = "Preloaded Gun Turret"
# blueprint.description = "A gun turret set to request 200 red-ammo when its placed, automatically filling it from the logistics network. Good for turret creep and offensive efforts."
print(len(entities.raw["chemical-plant"]["fluid_boxes"]))
print(len(entities.raw["oil-refinery"]["fluid_boxes"]))
# print(entities.raw["industrial-furnace"].keys())
# print(json.dumps(entities.raw["industrial-furnace"]["fluid_boxes"], indent=4))
# print(entities.flippable["industrial-furnace"])
print(entities.flippable["chemical-plant"])
print(entities.flippable["oil-refinery"])
print(entities.flippable["pumpjack"])
print(entities.flippable["electric-mining-drill"])
print(entities.flippable["rail-signal"])
print(entities.flippable["rail-chain-signal"])
print(entities.flippable["train-stop"])
print(entities.flippable["boiler"])
# print(entities.raw["chemical-plant"]["fluid_boxes"])

for fluid_box in entities.raw["pumpjack"]["output_fluid_box"]["pipe_connections"]:
    print(fluid_box)

print(entities.raw["rail-signal"]["default_orange_output_signal"])