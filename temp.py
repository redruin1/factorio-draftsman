
from logging import Filter
from draftsman.classes.group import Group
from draftsman.blueprintable import Blueprint, BlueprintBook
from draftsman.entity import *
from draftsman.data import entities, items
import copy
import weakref
import draftsman

import six
import os

blueprint = Blueprint()

# blueprint.entities.append("wooden-chest", tile_position = (-2, 0), id = "wood")

# group = Group()

# a = Container("steel-chest", id = "A")
# b = Container("steel-chest", tile_position = (1, 0), id = "B")
# #a.add_circuit_connection("red", b)

# group.id = "1"
# group.position = (0, 0)
# group.entities.append(a)
# group.entities.append(b)
# group.add_circuit_connection("red", "A", "B")

# blueprint.entities.append(group)

# group.id = "2"
# group.position = (2, 0)
# blueprint.entities.append(group)

# blueprint.add_circuit_connection("red", "wood", ("1", "A"))
# blueprint.add_circuit_connection("green", ("1", "B"), ("2", "A"))
# assert blueprint.entities["1"].entities["A"] is blueprint.entities[("1", "A")]

# print(len(blueprint.entities))

# print(blueprint.entities[("2", "A")])
# print(blueprint.entities[("2", "A")].id)

# group1 = Group("A")
# group2 = Group("B")
# group3 = Group("A")
# c = Container("wooden-chest", id = "C")
# base = Container("wooden-chest", id = "base", tile_position = (3, 0))

# group3.entities.append(c)
# group2.entities.append(group3)
# group1.entities.append(group2)
# blueprint.entities.append(group1)
# blueprint.entities.append(base)

# blueprint.add_circuit_connection("red", ("A", "B", "A", "C"), "base")

# blueprint.entities[("A", "B", "A")].id = "D"

# blueprint.add_circuit_connection("green", ("A", "B", "D", "C"), "base")

# print(blueprint.to_dict())
# print(blueprint)
# print(blueprint.to_string())

# silo = RocketSilo()
# silo.auto_launch = True
# silo.set_item_request("productivity-module-3", 4)
# silo.set_item_request("low-density-structure", 720)

# blueprint.entities.append(silo)

# print(blueprint.to_string())

blueprint.entities.append(Group("A"))
blueprint.entities.append(Group("B", type="different_type"))

diff = blueprint.find_entities_filtered(type="different_type")
assert diff[0] is blueprint.entities["B"]