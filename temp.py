from opcode import hasconst
from draftsman import Blueprint, Container, new_entity, BlueprintBook
from draftsman.classes import Group
from draftsman.data import signals
# from draftsman.classes.blueprint import KeyList
from draftsman import utils
from draftsman.data import entities

import json

# bp_string = "0eNqd0ttqwzAMBuB30bVTloOT1q9SxshBHYJECbYyFoLffU4GYWPuNnop+/dn2WiFpp9xssQCZgVqR3Zgris4euW639ZkmRAMkOAACrgetgp7bMVSm9xmy3WL4BUQd/gOJvXPCpCFhPDT2ovlheehQRsChyK2ZjeNVpIGewn6NLpwbOTt3o2q8pNWsIBJLsVJe69+YNn9liJceXB5nMsPbsCO5iE51Gns/yB1nCweeu6d/vRDWBbHygO71U4SYodWwkbEKr41pqAjG/5lT5QRufq/fP5NDpO0z535MqYK3tC6PZCd06K6ZJVOdZqXT95/AMv66Tw="

# blueprint = Blueprint(bp_string)
# blueprint.label = "Hello, draftsman!"

# # Determine where the electric furnace is
# furnace = blueprint.find_entities_filtered(type = "furnace")[0]
# pos = [furnace.tile_position["x"] + 1, furnace.tile_position["y"] + 1]
# print(furnace)
# blueprint.translate(-pos[0], -pos[1])
# print(furnace.tile_position)

# container = Container("steel-chest")
# # Set the inventory bar
# container.bar = int(container.inventory_size / 2)
# # Lets change the position of our entity in tile coordinates as well
# container.tile_position = (3, 0)
# blueprint.add_entity(container)

# print(blueprint)
# print(blueprint.to_string())

# blueprint.entities[0].id = "something"

# blueprint.add_entity("wooden-chest", id = "something")

# blueprint.entities["something"].id = "something else"
# blueprint.entities["something"] -> KeyError
# blueprint.entities["something else"] -> {...}

# test_list = KeyList()

# test_list.append("wooden-chest", position = (1, 2), id = "something")

# print(test_list.data)
# print(test_list.key_map)
# print(test_list.key_to_idx)
# print(test_list.idx_to_key)

# test_list.clear()

# print(test_list.data)
# print(test_list.key_map)
# print(test_list.key_to_idx)
# print(test_list.idx_to_key)

# source = utils.string_to_JSON("0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c=")
# print(utils.decode_version(source["blueprint"]["version"]))

# blueprint = Blueprint("0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c=")
# print(blueprint.version_tuple())
# assert blueprint.to_dict() == utils.string_to_JSON("0eNqrVkrKKU0tKMrMK1GyqlbKLEnNVbJCEtNRKkstKs7Mz1OyMrIwNDG3NDI3NTI0s7A0q60FAHmRE1c=")

#print(json.dumps(entities.raw["pumpjack"]["output_fluid_box"], indent = 2))
#print(json.dumps(entities.raw["oil-refinery"]["fluid_boxes"], indent = 2))
#print(json.dumps(entities.raw["chemical-plant"]["fluid_boxes"], indent = 2))

blueprint = Blueprint()
blueprint.entities.append(Container())

group = Group(id = "chests")
group.entities.append(Container("iron-chest"))

blueprint.entities.append(group)

print(blueprint)
print(blueprint.to_string())