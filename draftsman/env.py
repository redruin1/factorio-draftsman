# env.py

"""
Manages the Factorio environment. Primarily holds :py:func:`draftsman.env.update()`,
which runs through the Factorio data lifecycle and updates the data in
:py:mod:`draftsman.data`.


.. NOTE:: Deprecated as of Draftsman 2.0
"""

# TODO:
# * Treat `core` and `base` as mods to unify their loading
# * In a similar vein, `normalize_module_names()` could also be simplified if
#   they were in mods list

from draftsman.error import (
    MissingModError,
    IncompatableModError,
    IncorrectModVersionError,
    IncorrectModFormatError,
)
from draftsman.classes.collision_set import CollisionSet
from draftsman.utils import decode_version, version_string_to_tuple, AABB
from draftsman._factorio_version import __factorio_version_info__

from git import Repo
import lupa.lua52 as lupa  # Lupa 2.0 is now required (for simplicities sake)

import argparse
from collections import OrderedDict
import io
import json
import os
import pickle
import re
import struct
from typing import Optional, TypedDict, Union
import zipfile


mod_archive_pattern = "(([\\w\\D]+)_([\\d\\.]+))\\.zip"
mod_archive_regex = re.compile(mod_archive_pattern)

mod_folder_pattern = "([^\\s.]+)(?:_([\\d\\.]+))?$"
mod_folder_regex = re.compile(mod_folder_pattern)

dependency_string_pattern = (
    "[^\\w\\?\\!~]*([\\?\\!~])?[^\\w\\?\\!]*([\\w-]+)([><=]=?)?([\\d\\.]+)?"
)
dependency_regex = re.compile(dependency_string_pattern)

lua_module_pattern = "\\.\\/factorio-mods\\/(.+?)\\/.*"
lua_module_regex = re.compile(lua_module_pattern)


class Mod(object):
    """
    Mod object that stores metadata during the load process. Mostly used for
    structuring the data and determining the load order.
    """

    def __init__(
        self, name, internal_folder, version, archive, location, info, files, data
    ):
        self.name = name
        self.internal_folder = internal_folder
        self.version = version
        self.archive = archive
        self.location = location
        self.info = info
        self.files = files
        self.data = data
        self.dependencies = []

    def add_dependency(self, dependency):
        self.dependencies.append(dependency)

    def get_depth(self):
        depth = 1
        for dependency in self.dependencies:
            depth = max(depth, depth + dependency.get_depth())
        return depth

    def to_dict(self):
        return {
            "name": self.name,
            "version": self.version,
            "archive": self.archive,
            "location": self.location,
            "dependencies": self.dependencies,
        }

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return str(self.to_dict())


# =============================================================================


def file_to_string(filepath: str) -> str:
    """
    Simply grabs a file's contents and returns it as a string. Ensures that the
    returned string is stripped of special unicode characters that Lupa dislikes.
    """
    # "utf-8-sig" makes sure to strip BOM tokens if they exist
    with open(filepath, mode="r", encoding="utf-8-sig") as file:
        return file.read()


def archive_to_string(archive: zipfile.ZipFile, filepath: str) -> str:
    """
    Simply grabs a file with the specified name from an archive and returns it
    as a string. Ensures that the returned string is stripped of special
    unicode characters that Lupa dislikes.
    """
    with archive.open(filepath, mode="r") as file:
        # "utf-8-sig" makes sure to strip BOM tokens if they exist
        formatted_file = io.TextIOWrapper(file, encoding="utf-8-sig")
        return formatted_file.read()


ModSettings = TypedDict(
    "ModSettings", {"startup": dict, "runtime-global": dict, "runtime-per-user": dict}
)


def get_mod_settings(location: str) -> ModSettings:
    """
    Reads `mod_settings.dat` and stores it as an easy-to-read dict. Would be
    trivial to implement an editor with this function. (Well, assuming you write
    a function to export back to a ``.dat`` file)

    :param location: The path to the directory where 'mod-settings.dat' is
        located.

    :returns: A dictionary with 3 keys: ``"startup"``, ``"runtime-global"``, and
        ``"runtime-per-user"``, which contain all of their respective settings.
    """
    # Property Tree Enum
    PropertyTreeType = {
        "None": 0,
        "Bool": 1,
        "Number": 2,
        "String": 3,
        "List": 4,
        "Dictionary": 5,
    }

    def get_string(binary_stream):
        string_absent = bool(
            # int.from_bytes(binary_stream.read(1), "little", signed=False)
            struct.unpack("<?", binary_stream.read(1))[0]
        )
        if string_absent:
            return None
        # handle the Space Optimized length
        length = struct.unpack("<B", binary_stream.read(1))[0]
        if length == 255:  # length is actually longer
            length = struct.unpack("<I", binary_stream.read(4))[0]
        return binary_stream.read(length).decode()

    def get_data(binary_stream):
        data_type = struct.unpack("<B", binary_stream.read(1))[0]
        binary_stream.read(1)  # any type flag, largely internal, ignore
        if data_type == PropertyTreeType["None"]:
            return None
        elif data_type == PropertyTreeType["Bool"]:
            return bool(struct.unpack("<?", binary_stream.read(1))[0])
        elif data_type == PropertyTreeType["Number"]:
            value = struct.unpack("d", binary_stream.read(8))[0]
            return value
        elif data_type == PropertyTreeType["String"]:
            return get_string(binary_stream)
        elif data_type == PropertyTreeType["List"]:
            length = struct.unpack("<I", binary_stream.read(4))
            out = list()
            for i in range(length):
                out.append(get_data(binary_stream))
            return out
        elif data_type == PropertyTreeType["Dictionary"]:
            length = struct.unpack("<I", binary_stream.read(4))[0]
            out = dict()
            for i in range(length):
                name = get_string(binary_stream)
                value = get_data(binary_stream)
                out[name] = value
            return out

    mod_settings = {}
    with open(
        os.path.join(location, "mod-settings.dat"), mode="rb"
    ) as mod_settings_dat:
        # Header
        version_num = struct.unpack("<Q", mod_settings_dat.read(8))[0]
        version = decode_version(version_num)[::-1]  # Reversed, for some reason
        header_flag = bool(struct.unpack("<?", mod_settings_dat.read(1))[0])
        # It might be nice to print out the version for additional context, but
        # this doesn't seem to prohibit loading (as far as I know)
        # print(version)
        # However, we do ensure that the header flag is 0, as we are dealing
        # with a malformed input otherwise
        assert (
            not header_flag
        ), "mod-settings.dat header did not end with 0 byte, malformed input"
        mod_settings = get_data(mod_settings_dat)

    return mod_settings


def python_require(
    mod: Mod, mod_folder: str, module_name: str, package_path: str
) -> tuple[Optional[str], str]:
    """
    Function called from Lua that checks for a file in a ``zipfile`` archive,
    and returns the contents of the file if found.

    Used in the modified Lua ``require()`` function that handles special cases
    to model Factorio's load pattern. This function is called after
    `normalize_module_name`, and expects the name to be it's result.
    """

    # No sense searching the archive if the mod is not one to begin with; we
    # relay this information back to the Lua require function
    if not mod:
        return None, "\n\tNo mod specified"
    if not mod.archive:
        return None, "\n\tCurrent mod ({}) is not an archive".format(mod.name)

    # print("\t", mod.name)

    # We emulate lua filepath searching
    filepaths = package_path.split(";")
    for filepath in filepaths:
        # Replace the question mark with the module_name
        filepath = filepath.replace("?", module_name)
        # Normalize for Zipfile if there are backslashes
        filepath = filepath.replace("\\", "/")
        # Make it local to the archive, replacing the global path to the local
        # internal path
        # print("\tbefore filepath", filepath)
        # print("mod_folder + mod.name", mod_folder + "/" + mod.name)
        # print("mod.location", mod.location)
        filepath = filepath.replace(mod.location, mod.internal_folder)
        # print("\tafter filepath:", filepath)
        try:
            string_contents = archive_to_string(mod.files, filepath)
            fixed_filepath = os.path.dirname(filepath[filepath.find("/") :])
            return string_contents, fixed_filepath
        except KeyError:
            pass

    # Otherwise, we found squat
    return None, "no file '{}' found in '{}' archive".format(module_name, mod.name)


def load_stage(lua: lupa.LuaRuntime, mod_list: list[Mod], mod: Mod, stage: str) -> None:
    """
    Load a stage of the Factorio data lifecycle. Sets meta information and loads
    and executes the file string in the ``lua`` context.
    """
    # Set meta stuff
    lua.globals().MOD_LIST = mod_list
    # lua.globals().MOD = mod
    lua.globals().MOD_DIR = mod.location
    lua.globals().lua_push_mod(mod)
    lua.globals().CURRENT_FILE = mod.location + "/" + stage

    # Add the base mod folder as a base path (in addition to base and core)
    lua.globals().lua_add_path(mod.location + "/?.lua")

    lua.execute(mod.data[stage])


def convert_table_to_dict(table) -> Union[dict, list]:
    """
    Converts a Lua table to a Python dict. Correctly handles nesting, and
    interprets Lua arrays as lists.
    """
    out = dict(table)
    is_list = True
    for key in out:
        if not isinstance(key, int):
            is_list = False

        if lupa.lua_type(out[key]) == "table":
            out[key] = convert_table_to_dict(out[key])
            # check if its actually a dict and not a list

    if is_list:
        return list(out.values())

    return out


def get_order(objects_to_sort, sort_objects, sort_subgroups, sort_groups):
    """
    Sorts the list of objects according to their Factorio order. Attempts to
    sort by item order first, and defaults to entity order if not present.

    Item sort order:
    (https://forums.factorio.com/viewtopic.php?p=23818#p23818)

    1. object groups
    2. object subgroups
    3. object itself

    Across the previous categories, each is sorted by:

    1. the item order string (if present)
    2. the item name (lexographic)
    """

    def general_iterator(obj):
        if isinstance(obj, dict):
            return obj.values()
        else:
            return obj

    modified = []
    for object_to_sort in general_iterator(objects_to_sort):
        # Try to sort by item order if possible because thats more intuitive
        # Otherwise, fall back onto entity order

        associated_item = None
        try:
            # First, try to get the item that this object becomes when mined
            # Technically, "result" can also be "results", but I'm not sure we
            # need interpret those kinds of entities, so we ignore that case for
            # now
            associated_item = object_to_sort["minable"]["result"]
        except KeyError:
            # If not, check the list of items to see if our name is in there
            if object_to_sort["name"] in sort_objects:
                associated_item = object_to_sort["name"]

        if associated_item:
            # Get the name of the sorted item; we sort by this before we sort by
            # entity name
            sort_name = sort_objects[associated_item]["name"]
            # We also try to use the item sort order if available before we use
            # the entity sort order
            sort_order = sort_objects[associated_item].get(
                "order", object_to_sort.get("order", None)
            )

            # Subgroup is optional, and defaults to "other" if not specified
            if "subgroup" in sort_objects[associated_item]:
                subgroup_name = sort_objects[associated_item]["subgroup"]
                sort_subgroup = sort_subgroups[subgroup_name]
            else:
                sort_subgroup = sort_subgroups["other"]

            # Now that we know the subgroup, we can also determine the group
            # that this object belongs to
            group_name = sort_subgroup["group"]
            sort_group = sort_groups[group_name]
        else:  # the object is either an item or something non-placable
            # Pull the name and order from the object directly
            sort_name = object_to_sort["name"]
            sort_order = object_to_sort.get("order", None)

            # Subgroup is optional, and defaults to "other" if not specified
            if "subgroup" in object_to_sort:
                subgroup_name = object_to_sort["subgroup"]
                sort_subgroup = sort_subgroups[subgroup_name]
            else:
                # Set the subgroup to a default value
                # Maybe sort_subgroup defaults to type of sorted object?
                if object_to_sort["type"] == "fluid":
                    # Fluids default to the fluid category
                    sort_subgroup = sort_subgroups["fluid"]
                else:
                    sort_subgroup = sort_subgroups["other"]

            # Now that we know the subgroup, we can also determine the group
            # that this object belongs to
            group_name = sort_subgroup["group"]
            sort_group = sort_groups[group_name]

        # Sometimes we want to sort an item differently based off a 'parents'
        # name. Consider 'straight-rail' and 'se-straight-rail': name order
        # indicates that the order should be
        #    ['se-straight-rail', 'straight-rail']
        # but in-game, the rail-planners that you see are the other way around,
        # which is more intuitive.
        # However, if we sort by rail planners, we lose the original name of the
        # sorted target, straight-rail.
        # So we add a third param to "obj": first the item/entity order, then
        # the name we would like to sort the object with, and finally the actual
        # name that we want to preserve.
        modified.append(
            {
                "obj": (
                    sort_order is None,  # We want objects with no order last, not first
                    sort_order,
                    sort_name,
                    object_to_sort["name"],
                ),
                "subgroup": (sort_subgroup["order"], sort_subgroup["name"]),
                "group": (sort_group["order"], sort_group["name"]),
            }
        )

    order = sorted(modified, key=lambda x: (x["group"], x["subgroup"], x["obj"]))
    return [x["obj"][3] for x in order]


def get_items(lua):
    """
    Gets the loaded items, item subgroups, and item groups. Sorts them and
    returns them. Saves us the trouble of recalcualting this every time we sort
    something along item order, which we commonly do.
    """
    data = lua.globals().data

    groups = convert_table_to_dict(data.raw["item-group"])
    subgroups = convert_table_to_dict(data.raw["item-subgroup"])

    def to_ordered_dict(elem):
        sorted_elem = OrderedDict()
        for v in elem:
            sorted_elem[v["name"]] = v
        return sorted_elem

    # Apparently "order" is not required field, so we must sort by both order and name

    # Sort the groups and subgroups dictionaries
    test_values = sorted(
        list(groups.values()),
        key=lambda x: (x.get("order", None) is None, x.get("order", None), x["name"]),
    )
    sorted_groups = to_ordered_dict(test_values)

    test_values = sorted(
        list(subgroups.values()),
        key=lambda x: (x.get("order", None) is None, x.get("order", None), x["name"]),
    )
    sorted_subgroups = to_ordered_dict(test_values)

    group_index_dict = {}
    subgroup_index_dict = {}

    # Initialize item groups
    group_list = list(groups.values())
    for group in group_list:
        group["subgroups"] = []
        group_index_dict[group["name"]] = group

    # Initialize item subgroups
    subgroup_list = list(subgroups.values())
    for subgroup in subgroup_list:
        subgroup["items"] = []
        parent_group = group_index_dict[subgroup["group"]]
        parent_group["subgroups"].append(subgroup)
        subgroup_index_dict[subgroup["name"]] = subgroup

    def add_item(category, item_name):
        item = category[item_name]
        # if "flags" in item:
        #     if "hidden" in item["flags"].values():
        #         return
        if "subgroup" in item:
            subgroup = subgroup_index_dict[item["subgroup"]]
        else:
            subgroup = subgroup_index_dict["other"]
        if "order" not in item:
            item["order"] = ""
        subgroup["items"].append(item)

    def add_items(category):
        category = convert_table_to_dict(category)
        for item_name in category:
            add_item(category, item_name)

    # Iterate over every item
    add_items(data.raw["item"])
    add_items(data.raw["item-with-entity-data"])
    add_items(data.raw["tool"])
    add_items(data.raw["ammo"])
    add_items(data.raw["module"])
    add_items(data.raw["armor"])
    add_items(data.raw["gun"])
    add_items(data.raw["capsule"])
    # Extras
    add_items(data.raw["blueprint"])
    add_items(data.raw["blueprint-book"])
    add_items(data.raw["upgrade-item"])
    add_items(data.raw["deconstruction-item"])
    add_items(data.raw["spidertron-remote"])
    add_items(data.raw["repair-tool"])  # not an item somehow
    add_items(data.raw["rail-planner"])

    # Sort everything
    for i, _ in enumerate(group_list):
        for j, _ in enumerate(group_list[i]["subgroups"]):
            group_list[i]["subgroups"][j]["items"] = to_ordered_dict(
                sorted(
                    group_list[i]["subgroups"][j]["items"],
                    key=lambda x: (
                        x.get("order", None) is None,
                        x.get("order", None),
                        x["name"],
                    ),
                )
            )
        group_list[i]["subgroups"] = to_ordered_dict(
            sorted(
                group_list[i]["subgroups"],
                key=lambda x: (
                    x.get("order", None) is None,
                    x.get("order", None),
                    x["name"],
                ),
            )
        )
    group_list = sorted(
        group_list,
        key=lambda x: (x.get("order", None) is None, x.get("order", None), x["name"]),
    )

    # Flatten into all_items dictionary
    sorted_items = OrderedDict()
    for group in group_list:
        for subgroup_name in group["subgroups"]:
            subgroup = group["subgroups"][subgroup_name]
            for item_name in subgroup["items"]:
                item = subgroup["items"][item_name]
                sorted_items[item["name"]] = item

    return sorted_items, sorted_subgroups, sorted_groups


def get_default_collision_mask(entity_type):
    """
    Determine the default collision mask based on the string entity type.

    :param entity_type: A string containing what type of entity we're getting
        a collision mask for. (e.g. ``"container"``, ``"gate"``, ``"heat-pipe"``,
        etc.)

    :returns: A ``set()`` containing the default collision layers for that
        object.
    """
    if entity_type == "gate":
        return {
            "item-layer",
            "object-layer",
            "player-layer",
            "water-tile",
            "train-layer",
        }
    elif entity_type == "heat-pipe":
        return {"object-layer", "floor-layer", "water-tile"}
    elif entity_type == "land-mine":
        return {"object-layer", "water-tile"}
    elif entity_type == "linked-belt":
        return {
            "object-layer",
            "item-layer",
            "transport-belt-layer",
            "water-tile",
        }
    elif entity_type == "loader":
        return {
            "object-layer",
            "item-layer",
            "transport-belt-layer",
            "water-tile",
        }
    elif entity_type == "straight-rail" or entity_type == "curved-rail":
        return {
            "item-layer",
            "object-layer",
            "rail-layer",
            "floor-layer",
            "water-tile",
        }
    elif entity_type == "rail-signal" or entity_type == "rail-chain-signal":
        return {"floor-layer", "rail-layer", "item-layer"}
    elif (
        entity_type == "locomotive"
        or entity_type == "cargo-wagon"
        or entity_type == "fluid-wagon"
        or entity_type == "artillery-wagon"
    ):
        return {"train-layer"}
    elif entity_type == "splitter":
        return {
            "object-layer",
            "item-layer",
            "transport-belt-layer",
            "water-tile",
        }
    elif entity_type == "transport-belt":
        return {
            "object-layer",
            "floor-layer",
            "transport-belt-layer",
            "water-tile",
        }
    elif entity_type == "underground-belt":
        return {
            "object-layer",
            "item-layer",
            "transport-belt-layer",
            "water-tile",
        }
    else:  # true default
        return {
            "item-layer",
            "object-layer",
            "player-layer",
            "water-tile",
        }


# =============================================================================


def extract_mods(loaded_mods, data_location, verbose):
    """
    Extract all the mod versions to ``mods.pkl`` in :py:mod:`draftsman.data`.
    """
    out_mods = {}
    for mod in loaded_mods:
        if mod == "core":
            continue
        out_mods[mod] = version_string_to_tuple(loaded_mods[mod].version)

    with open(os.path.join(data_location, "mods.pkl"), "wb") as out:
        pickle.dump(out_mods, out, 2)

    if verbose:
        print("Extracted mods...")


def extract_entities(lua, data_location, verbose, sort_tuple):
    """
    Extracts the entities to ``entities.pkl`` in :py:mod:`draftsman.data`.
    """

    data = lua.globals().data

    entities = {}
    unordered_entities_raw = {}
    is_flippable = {}
    collision_sets = {}

    def is_entity_flippable(entity):
        """
        Determines whether or not the input entity can be flipped inside a
        Blueprint.
        """
        # if not entity.get("fluid_boxes", False):
        #     return True

        # https://forums.factorio.com/102294

        # Check if any entity has a fluid box
        # fluid_boxes = []
        # if "fluid_box" in entity:
        #     fluid_boxes.append(copy.deepcopy(entity["fluid_box"]))
        # elif "fluid_boxes" in entity:  # Check crafting machine fluid boxes
        #     boxes_copy = copy.deepcopy(entity["fluid_boxes"])
        #     if isinstance(boxes_copy, dict):  # Convert to a list if it's a dict
        #         boxes_copy.pop("off_when_no_fluid_recipe", None)
        #         boxes_copy = list(boxes_copy.values())
        #     fluid_boxes.extend(boxes_copy)
        # elif "output_fluid_box" in entity:  # Check mining-drill fluid boxes
        #     fluid_boxes.append(copy.deepcopy(entity["output_fluid_box"]))

        # if fluid_boxes:

        #     # Record the position of every fluid box along with their type
        #     box_locations = {}
        #     for fluid_box in fluid_boxes:
        #         for pipe_connection in fluid_box["pipe_connections"]:
        #             if "position" in pipe_connection:
        #                 pos = tuple(pipe_connection["position"])
        #                 box_locations[pos] = pipe_connection.get("type", "input-output")
        #             elif "positions" in pipe_connection:
        #                 for pos in pipe_connection["positions"]:
        #                     pos = tuple(pos)
        #                     box_locations[pos] = pipe_connection.get("type", "input-output")

        #     # Check the fluid box's mirrored position for conflicts
        #     for fluid_box in fluid_boxes:
        #         for pipe_connection in fluid_box["pipe_connections"]:
        #             if "position" in pipe_connection:
        #                 pos = tuple(pipe_connection["position"])
        #                 type = box_locations[pos]
        #                 if ((-pos[0], pos[1]) in box_locations and
        #                     type != box_locations[(-pos[0], pos[1])]):
        #                     return False
        #                 if ((pos[0], -pos[1]) in box_locations and
        #                     type != box_locations[(pos[0], -pos[1])]):
        #                     return False
        #                 # if pos[0] != 0 and pos[1] != 0:
        #                 #     return False
        #             elif "positions" in pipe_connection:
        #                 for pos in pipe_connection["positions"]:
        #                     pos = tuple(pos)
        #                     type = box_locations[pos]
        #                     if ((-pos[0], pos[1]) in box_locations and
        #                         type != box_locations[(-pos[0], pos[1])]):
        #                         return False
        #                     if ((pos[0], -pos[1]) in box_locations and
        #                         type != box_locations[(pos[0], -pos[1])]):
        #                         return False

        # Hardcoded entities: we do this because I have no idea what the
        # criteria is for unflippablility
        if entity["name"] in {"pumpjack", "chemical-plant", "oil-refinery"}:
            return False

        # Restricted types; due to the way rails work these have no flipping
        if entity["type"] in {"rail-signal", "rail-chain-signal", "train-stop"}:
            return False

        return True

    def categorize_entity(entity_name, entity):
        flags = entity.get("flags", set())
        if (
            "not-blueprintable" in flags or "not-deconstructable" in flags
        ):  # or "hidden" in flags
            return False

        collision_mask = entity.get("collision_mask", None)
        if not collision_mask:
            entity["collision_mask"] = get_default_collision_mask(entity["type"])
        else:
            entity["collision_mask"] = set(collision_mask)

        # Check if an entity is flippable or not
        is_flippable[entity_name] = is_entity_flippable(entity)

        # maybe move this to get_order?
        unordered_entities_raw[entity_name] = entity
        return True

    def categorize_entities(entity_table, target_list):
        entity_dict = convert_table_to_dict(entity_table)
        for entity_name, entity in entity_dict.items():
            if not categorize_entity(entity_name, entity):
                continue

            target_list.append(entity)
            entities["all"].append(entity)

    def sort(target_list):
        sorted_list = get_order(target_list, *sort_tuple)
        for i, x in enumerate(sorted_list):
            target_list[i] = x

    entities["all"] = []

    #  Chests
    entities["containers"] = []
    categorize_entities(data.raw["container"], entities["containers"])
    sort(entities["containers"])

    #  Storage tanks
    entities["storage_tanks"] = []
    categorize_entities(data.raw["storage-tank"], entities["storage_tanks"])
    sort(entities["storage_tanks"])

    #  Belts
    entities["transport_belts"] = []
    categorize_entities(data.raw["transport-belt"], entities["transport_belts"])
    sort(entities["transport_belts"])
    entities["underground_belts"] = []
    categorize_entities(data.raw["underground-belt"], entities["underground_belts"])
    sort(entities["underground_belts"])
    entities["splitters"] = []
    categorize_entities(data.raw["splitter"], entities["splitters"])
    sort(entities["splitters"])

    #  Inserters
    entities["inserters"] = []
    entities["filter_inserters"] = []
    # categorize_entities(data.raw["inserter"], inserters)
    temp_inserters = convert_table_to_dict(data.raw["inserter"])
    for inserter_name, inserter in temp_inserters.items():
        if not categorize_entity(inserter_name, inserter):
            continue
        unordered_entities_raw[inserter_name] = inserter
        if "filter_count" in inserter:
            entities["filter_inserters"].append(inserter)
        else:
            entities["inserters"].append(inserter)

        entities["all"].append(inserter)
    sort(entities["inserters"])
    sort(entities["filter_inserters"])

    #  Loaders
    entities["loaders"] = []
    categorize_entities(data.raw["loader"], entities["loaders"])
    sort(entities["loaders"])

    #  Electric poles
    entities["electric_poles"] = []
    categorize_entities(data.raw["electric-pole"], entities["electric_poles"])
    sort(entities["electric_poles"])

    #  Pipes
    entities["pipes"] = []
    categorize_entities(data.raw["pipe"], entities["pipes"])
    sort(entities["pipes"])
    entities["underground_pipes"] = []
    categorize_entities(data.raw["pipe-to-ground"], entities["underground_pipes"])
    sort(entities["underground_pipes"])

    #  Pumps
    entities["pumps"] = []
    categorize_entities(data.raw["pump"], entities["pumps"])
    sort(entities["pumps"])

    #  Rails
    entities["straight_rails"] = []
    categorize_entities(data.raw["straight-rail"], entities["straight_rails"])
    sort(entities["straight_rails"])
    # entities["curved_rails"] = []
    # categorize_entities(data.raw["curved-rail"], entities["curved_rails"])
    # sort(entities["curved_rails"])

    #  Train stops
    entities["train_stops"] = []
    categorize_entities(data.raw["train-stop"], entities["train_stops"])
    sort(entities["train_stops"])

    #  Rail signals
    entities["rail_signals"] = []
    categorize_entities(data.raw["rail-signal"], entities["rail_signals"])
    sort(entities["rail_signals"])
    entities["rail_chain_signals"] = []
    categorize_entities(data.raw["rail-chain-signal"], entities["rail_chain_signals"])
    sort(entities["rail_chain_signals"])

    #  Train cars
    entities["locomotives"] = []
    categorize_entities(data.raw["locomotive"], entities["locomotives"])
    sort(entities["locomotives"])
    entities["cargo_wagons"] = []
    categorize_entities(data.raw["cargo-wagon"], entities["cargo_wagons"])
    sort(entities["cargo_wagons"])
    entities["fluid_wagons"] = []
    categorize_entities(data.raw["fluid-wagon"], entities["fluid_wagons"])
    sort(entities["fluid_wagons"])
    entities["artillery_wagons"] = []
    categorize_entities(data.raw["artillery-wagon"], entities["artillery_wagons"])
    sort(entities["artillery_wagons"])

    #  Logistics containers (Special)
    entities["logistic_passive_containers"] = []
    entities["logistic_active_containers"] = []
    entities["logistic_storage_containers"] = []
    entities["logistic_buffer_containers"] = []
    entities["logistic_request_containers"] = []
    logi_containers = convert_table_to_dict(data.raw["logistic-container"])
    for container_name, container in logi_containers.items():
        if not categorize_entity(container_name, container):
            continue
        unordered_entities_raw[container_name] = container
        container_type = container["logistic_mode"]
        if container_type == "passive-provider":
            entities["logistic_passive_containers"].append(container)
        elif container_type == "active-provider":
            entities["logistic_active_containers"].append(container)
        elif container_type == "storage":
            entities["logistic_storage_containers"].append(container)
        elif container_type == "buffer":
            entities["logistic_buffer_containers"].append(container)
        elif container_type == "requester":
            entities["logistic_request_containers"].append(container)

        entities["all"].append(inserter)
    sort(entities["logistic_passive_containers"])
    sort(entities["logistic_active_containers"])
    sort(entities["logistic_storage_containers"])
    sort(entities["logistic_buffer_containers"])
    sort(entities["logistic_request_containers"])

    #  Roboports
    entities["roboports"] = []
    categorize_entities(data.raw["roboport"], entities["roboports"])
    sort(entities["roboports"])

    #  Lamps
    entities["lamps"] = []
    categorize_entities(data.raw["lamp"], entities["lamps"])
    sort(entities["lamps"])

    #  Combinators
    entities["arithmetic_combinators"] = []
    categorize_entities(
        data.raw["arithmetic-combinator"], entities["arithmetic_combinators"]
    )
    sort(entities["arithmetic_combinators"])
    entities["decider_combinators"] = []
    categorize_entities(data.raw["decider-combinator"], entities["decider_combinators"])
    sort(entities["decider_combinators"])
    entities["constant_combinators"] = []
    categorize_entities(
        data.raw["constant-combinator"], entities["constant_combinators"]
    )
    sort(entities["constant_combinators"])
    entities["power_switches"] = []
    categorize_entities(data.raw["power-switch"], entities["power_switches"])
    sort(entities["power_switches"])
    entities["programmable_speakers"] = []
    categorize_entities(
        data.raw["programmable-speaker"], entities["programmable_speakers"]
    )
    sort(entities["programmable_speakers"])

    #  Boilers / Heat exchangers
    entities["boilers"] = []
    categorize_entities(data.raw["boiler"], entities["boilers"])
    sort(entities["boilers"])

    #  Steam engines / turbines
    entities["generators"] = []
    categorize_entities(data.raw["generator"], entities["generators"])
    sort(entities["generators"])

    #  Solar panels
    entities["solar_panels"] = []
    categorize_entities(data.raw["solar-panel"], entities["solar_panels"])
    sort(entities["solar_panels"])

    #  Accumulators
    entities["accumulators"] = []
    categorize_entities(data.raw["accumulator"], entities["accumulators"])
    sort(entities["accumulators"])

    #  Reactors
    entities["reactors"] = []
    categorize_entities(data.raw["reactor"], entities["reactors"])
    sort(entities["reactors"])

    #  Heat pipes
    entities["heat_pipes"] = []
    categorize_entities(data.raw["heat-pipe"], entities["heat_pipes"])
    sort(entities["heat_pipes"])

    #  Mining drills (Burner, Electric, Pumpjack)
    entities["mining_drills"] = []
    categorize_entities(data.raw["mining-drill"], entities["mining_drills"])
    sort(entities["mining_drills"])

    #  Offshore pumps
    entities["offshore_pumps"] = []
    categorize_entities(data.raw["offshore-pump"], entities["offshore_pumps"])
    sort(entities["offshore_pumps"])

    #  Furnaces
    entities["furnaces"] = []
    categorize_entities(data.raw["furnace"], entities["furnaces"])
    sort(entities["furnaces"])

    #  Assembling machines (1-3 + chemical plant, refinery, and centrifuge)
    entities["assembling_machines"] = []
    categorize_entities(data.raw["assembling-machine"], entities["assembling_machines"])
    sort(entities["assembling_machines"])

    #  Labs
    entities["labs"] = []
    categorize_entities(data.raw["lab"], entities["labs"])
    sort(entities["labs"])

    #  Beacons
    entities["beacons"] = []
    categorize_entities(data.raw["beacon"], entities["beacons"])
    sort(entities["beacons"])

    #  Rocket silos
    entities["rocket_silos"] = []
    categorize_entities(data.raw["rocket-silo"], entities["rocket_silos"])
    sort(entities["rocket_silos"])

    #  Landmines
    entities["land_mines"] = []
    categorize_entities(data.raw["land-mine"], entities["land_mines"])
    sort(entities["land_mines"])

    #  Walls
    entities["walls"] = []
    categorize_entities(data.raw["wall"], entities["walls"])
    sort(entities["walls"])

    #  Gates
    entities["gates"] = []
    categorize_entities(data.raw["gate"], entities["gates"])
    sort(entities["gates"])

    #  Turrets
    entities["turrets"] = []
    categorize_entities(data.raw["ammo-turret"], entities["turrets"])
    categorize_entities(data.raw["electric-turret"], entities["turrets"])
    categorize_entities(data.raw["fluid-turret"], entities["turrets"])
    categorize_entities(data.raw["artillery-turret"], entities["turrets"])
    sort(entities["turrets"])

    #  Radars
    entities["radars"] = []
    categorize_entities(data.raw["radar"], entities["radars"])
    sort(entities["radars"])

    #  Simple Entities with Owner
    entities["simple_entities_with_owner"] = []
    categorize_entities(
        data.raw["simple-entity-with-owner"], entities["simple_entities_with_owner"]
    )
    sort(entities["simple_entities_with_owner"])

    #  Simple Entities with Force
    entities["simple_entities_with_force"] = []
    categorize_entities(
        data.raw["simple-entity-with-force"], entities["simple_entities_with_force"]
    )
    sort(entities["simple_entities_with_force"])

    #  Electric Energy Interfaces
    entities["electric_energy_interfaces"] = []
    categorize_entities(
        data.raw["electric-energy-interface"], entities["electric_energy_interfaces"]
    )
    sort(entities["electric_energy_interfaces"])

    #  Linked Containers
    entities["linked_containers"] = []
    try:
        # Early versions of Factorio 1.0 didn't have linked containers yet; this
        # checks for that outcome
        categorize_entities(data.raw["linked-container"], entities["linked_containers"])
        sort(entities["linked_containers"])
    except TypeError:
        pass

    #  Heat interfaces
    entities["heat_interfaces"] = []
    categorize_entities(data.raw["heat-interface"], entities["heat_interfaces"])
    sort(entities["heat_interfaces"])

    #  Linked belts
    entities["linked_belts"] = []
    try:  # Compatibility for Factorio 1.0
        categorize_entities(data.raw["linked-belt"], entities["linked_belts"])
        sort(entities["linked_belts"])
    except TypeError:
        pass

    #  Infinity containers
    entities["infinity_containers"] = []
    categorize_entities(data.raw["infinity-container"], entities["infinity_containers"])
    sort(entities["infinity_containers"])

    #  Infinity pipes
    entities["infinity_pipes"] = []
    categorize_entities(data.raw["infinity-pipe"], entities["infinity_pipes"])
    sort(entities["infinity_pipes"])

    #  Burner generators
    entities["burner_generators"] = []
    categorize_entities(data.raw["burner-generator"], entities["burner_generators"])
    sort(entities["burner_generators"])

    #  Player Ports
    # entities["player_ports"] = []
    # categorize_entities(data.raw["player-port"], entities["player_ports"])
    # sort(entities["player_ports"])

    #  List of all entities
    sort(entities["all"])

    raw_order = get_order(unordered_entities_raw, *sort_tuple)
    entities["raw"] = OrderedDict()
    for name in raw_order:
        entities["raw"][name] = unordered_entities_raw[name]

    for name in raw_order:
        collision_box = entities["raw"][name].get("collision_box", None)
        if collision_box:
            collision_sets[name] = CollisionSet(
                [
                    AABB(
                        collision_box[0][0],
                        collision_box[0][1],
                        collision_box[1][0],
                        collision_box[1][1],
                    )
                ]
            )
        else:
            collision_sets[name] = CollisionSet([])

    entities["flippable"] = is_flippable
    entities["collision_sets"] = collision_sets

    with open(os.path.join(data_location, "entities.pkl"), "wb") as out:
        pickle.dump(entities, out, 2)

    if verbose:
        print("Extracted entities...")


# =============================================================================


def extract_fluids(lua, data_location, verbose, sort_tuple):
    """
    Extracts the fluids to ``fluids.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    unordered_fluids_raw = convert_table_to_dict(data.raw["fluid"])
    raw_order = get_order(unordered_fluids_raw, *sort_tuple)

    fluids_raw = OrderedDict()
    for name in raw_order:
        fluids_raw[name] = unordered_fluids_raw[name]

    with open(os.path.join(data_location, "fluids.pkl"), "wb") as out:
        pickle.dump((fluids_raw,), out, 2)

    if verbose:
        print("Extracted fluids...")


# =============================================================================


def extract_instruments(lua, data_location, verbose):
    """
    Extracts the instruments to ``instruments.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    instrument_raw = OrderedDict()
    instrument_index = {}
    instrument_names = {}
    speakers = convert_table_to_dict(data.raw["programmable-speaker"])
    for speaker in speakers:
        instrument_list = speakers[speaker]["instruments"]
        instrument_raw[speaker] = instrument_list
        instrument_index[speaker] = {}
        instrument_names[speaker] = {}
        for i, instrument in enumerate(instrument_list):
            index_dict = {}
            index_dict["self"] = i
            name_dict = {}
            name_dict["self"] = instrument["name"]
            for j, note in enumerate(instrument["notes"]):
                index_dict[note["name"]] = j
                name_dict[j] = note["name"]
            instrument_index[speaker][instrument["name"]] = index_dict
            instrument_names[speaker][i] = name_dict

    with open(os.path.join(data_location, "instruments.pkl"), "wb") as out:
        instrument_data = [instrument_raw, instrument_index, instrument_names]
        pickle.dump(instrument_data, out, 2)

    if verbose:
        print("Extracted instruments...")


# =============================================================================


def extract_items(lua, data_location, verbose, sort_tuple):
    """
    Extracts the items to ``items.pkl`` in :py:mod:`draftsman.data`.
    """
    sorted_items, sorted_subgroups, sorted_groups = sort_tuple

    data = lua.globals().data

    # Grab fuel items
    fuel_categories = convert_table_to_dict(data.raw["fuel-category"])

    fuels = {category: set() for category in fuel_categories}

    for item_name, item in sorted_items.items():
        if "fuel_category" in item:
            fuels[item["fuel_category"]].add(item_name)

    with open(os.path.join(data_location, "items.pkl"), "wb") as out:
        items = [sorted_items, sorted_subgroups, sorted_groups, fuels]
        pickle.dump(items, out, 2)

    if verbose:
        print("Extracted items...")


# =============================================================================


def extract_modules(lua, data_location, verbose, sort_tuple):
    """
    Extracts the modules to ``modules.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    # Init categories
    categories = convert_table_to_dict(data.raw["module-category"])
    out_categories = OrderedDict()
    for category in categories:
        out_categories[category] = []

    modules = convert_table_to_dict(data.raw["module"])
    unsorted_modules_raw = {}
    for module in modules:
        unsorted_modules_raw[module] = modules[module]

    raw_order = get_order(unsorted_modules_raw, *sort_tuple)
    modules_raw = OrderedDict()
    for name in raw_order:
        modules_raw[name] = unsorted_modules_raw[name]
        # Create the categories using the (now sorted) modules
        module_type = unsorted_modules_raw[name]["category"]
        out_categories[module_type].append(name)

    with open(os.path.join(data_location, "modules.pkl"), "wb") as out:
        pickle.dump([modules_raw, out_categories], out, 2)

    if verbose:
        print("Extracted modules...")


# =============================================================================


def extract_recipes(lua, data_location, verbose, sort_tuple):
    """
    Extracts the recipes to ``recipes.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    out_categories = {}
    for_machine = {}

    categories = convert_table_to_dict(data.raw["recipe-category"])
    for category in categories:
        out_categories[category] = []

    unsorted_recipes = convert_table_to_dict(data.raw["recipe"])
    for recipe in unsorted_recipes:
        category = unsorted_recipes[recipe].get("category", "crafting")
        out_categories[category].append(unsorted_recipes[recipe]["name"])

    machines = convert_table_to_dict(data.raw["assembling-machine"])
    for machine_name in machines:
        for_machine[machine_name] = []
        machine = machines[machine_name]
        for category_name in machine["crafting_categories"]:
            category = out_categories[category_name]
            for recipe_name in category:
                for_machine[machine_name].append(recipe_name)

    # TODO: recipe sorting still needs to validated
    # It's mostly correct, though I think I need to do some analysis of subgroup
    recipe_order = get_order(unsorted_recipes, *sort_tuple)
    recipes = OrderedDict()
    for recipe in recipe_order:
        recipes[recipe] = unsorted_recipes[recipe]

    with open(os.path.join(data_location, "recipes.pkl"), "wb") as out:
        data = [recipes, out_categories, for_machine]
        pickle.dump(data, out, 2)

    if verbose:
        print("Extracted recipes...")


# =============================================================================


def extract_signals(lua, data_location, verbose, sort_tuple):
    """
    Extracts the signals to ``signals.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    unsorted_raw_signals = {}
    type_of_signals = {}
    item_signals = []
    fluid_signals = []
    virtual_signals = []

    def add_signals(signal_category, target_location, signal_type):
        signal_category = convert_table_to_dict(data.raw[signal_category])
        for signal_name in signal_category:
            if signal_name in {"item-unknown", "fluid-unknown", "signal-unknown"}:
                continue
            signal_obj = signal_category[signal_name]
            if "flags" in signal_obj and "hidden" in signal_obj["flags"]:
                continue
            unsorted_raw_signals[signal_name] = signal_obj
            type_of_signals[signal_name] = signal_type
            target_location.append(signal_category[signal_name])

    # Item Signals
    add_signals("item", item_signals, "item")
    add_signals("item-with-entity-data", item_signals, "item")
    add_signals("tool", item_signals, "item")
    add_signals("ammo", item_signals, "item")
    add_signals("module", item_signals, "item")
    add_signals("armor", item_signals, "item")
    add_signals("gun", item_signals, "item")
    add_signals("capsule", item_signals, "item")
    add_signals("blueprint", item_signals, "item")
    add_signals("blueprint-book", item_signals, "item")
    add_signals("upgrade-item", item_signals, "item")
    add_signals("deconstruction-item", item_signals, "item")
    add_signals("spidertron-remote", item_signals, "item")
    add_signals("repair-tool", item_signals, "item")  # not an item somehow
    add_signals("rail-planner", item_signals, "item")

    # Fluid Signals
    add_signals("fluid", fluid_signals, "fluid")
    # Virtual Signals
    add_signals("virtual-signal", virtual_signals, "virtual")

    item_signals = get_order(item_signals, *sort_tuple)
    fluid_signals = get_order(fluid_signals, *sort_tuple)
    virtual_signals = get_order(virtual_signals, *sort_tuple)
    all_signals_order = virtual_signals + fluid_signals + item_signals

    raw_signals = OrderedDict()
    for signal in all_signals_order:
        raw_signals[signal] = unsorted_raw_signals[signal]

    with open(os.path.join(data_location, "signals.pkl"), "wb") as out:
        data = [
            raw_signals,
            type_of_signals,
            item_signals,
            fluid_signals,
            virtual_signals,
        ]
        pickle.dump(data, out, 2)

    if verbose:
        print("Extracted signals...")


# =============================================================================


def extract_tiles(lua, data_location, verbose):
    """
    Extracts the tiles to ``tiles.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    tiles = convert_table_to_dict(data.raw["tile"])

    tile_list = []
    for tile in tiles:
        tiles[tile]["collision_mask"] = set(tiles[tile]["collision_mask"])
        tile_order = tiles[tile].get("order", None)
        tile_list.append((tile_order is None, tile_order, tile))

    # Sort
    result = sorted(tile_list)
    result = [x[2] for x in result]

    # Construct new output dict
    out_tiles = {}
    for tile in result:
        out_tiles[tile] = tiles[tile]

    with open(os.path.join(data_location, "tiles.pkl"), "wb") as out:
        pickle.dump(out_tiles, out, 2)

    if verbose:
        print("Extracted tiles...")


# =============================================================================


def register_mod(mod_name, mod_location, mods, factorio_version_info, verbose, report):
    external_mod_version = None  # Optional (the version indicated by filepath)

    if mod_name.lower().endswith(".zip"):
        # Zip file
        m = mod_archive_regex.match(mod_name)
        if not m:
            raise IncorrectModFormatError(
                "Mod archive '{}' does not fit the 'name_version' format".format(
                    mod_name
                )
            )
        folder_name = m.group(1)
        mod_name = m.group(2).replace(" ", "")
        external_mod_version = m.group(3)
        files = zipfile.ZipFile(mod_location, mode="r")

        # There is no restriction on the name of the internal folder, just
        # that there is only one at the root of the archive
        # All the mods I've seen use the same "mod-name_mod-version", but
        # the wiki says this is not enforced
        # Hence, we use this scuffed code to actually get a list of all the
        # root-most directories
        topdirs = set()
        for file in files.namelist():
            basename = None  # guards against UnboundLocalError
            while file:
                file, basename = os.path.split(file)
            topdirs.add(basename)

        # REVISION: sometimes there are multiple folders in a single archive
        # (even though the wiki says only one); eg: "__MACOSX" in
        # "Mining Drones Harder" mod (seems to be reserved file when
        # compressing on Mac)
        if len(topdirs) == 1:
            # If there's one folder, use that
            mod_folder = topdirs.pop()
        elif folder_name in topdirs:
            # If there's multiple, but one matches exactly, use that
            mod_folder = folder_name
        else:
            # Otherwise, who knows! Fix your mods or update the wiki!
            # Why do I always get the short end of the stick!?
            raise IncorrectModFormatError(
                "Mod archive '{}' has more than one internal folder, and "
                "none of the internal folders match it's external name".format(mod_name)
            )

        try:
            # Zipfiles don't like backslashes on Windows, so we manually
            # concatenate
            mod_info = json.loads(archive_to_string(files, mod_folder + "/info.json"))
        except KeyError:
            raise IncorrectModFormatError(
                "Mod '{}' has no 'info.json' file in its root folder".format(mod_name)
            )

        mod_version = mod_info["version"]
        archive = True
        location = mod_location  # containing_dir + "/" + mod_name

    elif os.path.isdir(mod_location):
        # Folder
        m = mod_folder_regex.match(mod_name)
        if not m:
            raise IncorrectModFormatError(
                "Mod folder '{}' does not fit the 'name' or 'name_version' format".format(
                    mod_name
                )
            )
        mod_name = m.group(1)
        external_mod_version = m.group(2)
        try:
            with open(os.path.join(mod_location, "info.json"), "r") as info_file:
                mod_info = json.load(info_file)
        except FileNotFoundError:
            raise IncorrectModFormatError(
                "Mod '{}' has no 'info.json' file in its root folder".format(mod_name)
            )

        mod_folder = mod_location
        mod_version = mod_info.get("version", "")  # "core" doesn't have version
        archive = False
        files = None
        location = mod_location

    else:  # Regular file
        return  # Ignore: cannot be considered a mod

    # # First make sure the mod is enabled, and skip if not
    # # (The mod itself is not guaranteed to be in the enabled_mod_list if we
    # # added it manually when mod-list.json already exists, so we default to
    # # True if a particular mod is not found)
    # if not enabled_mod_list.get(mod_name, True):
    #     continue

    # Idiot check: assert external version matches internal version
    # if external_mod_version:
    #     assert version_string_to_tuple(
    #         external_mod_version
    #     ) == version_string_to_tuple(
    #         mod_version
    #     ), "{}: External version ({}) does not match internal version ({})".format(
    #         mod_name, external_mod_version, mod_version
    #     )

    # Ensure that the mod's factorio version is correct
    # (Except for in the cases of the "base" and "core" mods, which are exempt)
    if mod_name not in ("base", "core"):
        mod_factorio_version = version_string_to_tuple(mod_info["factorio_version"])
        assert mod_factorio_version <= factorio_version_info

    mod_data = {}
    if archive:
        # Attempt to load setting files
        try:
            settings = archive_to_string(files, mod_folder + "/settings.lua")
            mod_data["settings.lua"] = settings
        except KeyError:
            pass
        try:
            settings = archive_to_string(files, mod_folder + "/settings-updates.lua")
            mod_data["settings-updates.lua"] = settings
        except KeyError:
            pass
        try:
            settings = archive_to_string(
                files, mod_folder + "/settings-final-fixes.lua"
            )
            mod_data["settings-final-fixes.lua"] = settings
        except KeyError:
            pass
        # Attempt to load data files
        try:
            data = archive_to_string(files, mod_folder + "/data.lua")
            mod_data["data.lua"] = data
        except KeyError:
            pass
        try:
            data_updates = archive_to_string(files, mod_folder + "/data-updates.lua")
            mod_data["data-updates.lua"] = data_updates
        except KeyError:
            pass
        try:
            data_final_fixes = archive_to_string(
                files, mod_folder + "/data-final-fixes.lua"
            )
            mod_data["data-final-fixes.lua"] = data_final_fixes
        except KeyError:
            pass
    else:  # folder
        # Attempt to load setting files
        try:
            settings = file_to_string(mod_folder + "/settings.lua")
            mod_data["settings.lua"] = settings
        except FileNotFoundError:
            pass
        try:
            settings = file_to_string(mod_folder + "/settings-updates.lua")
            mod_data["settings-updates.lua"] = settings
        except FileNotFoundError:
            pass
        try:
            settings = file_to_string(mod_folder + "/settings-final-fixes.lua")
            mod_data["settings-final-fixes.lua"] = settings
        except FileNotFoundError:
            pass
        # Attempt to load data files
        try:
            data = file_to_string(mod_folder + "/data.lua")
            mod_data["data.lua"] = data
        except FileNotFoundError:
            pass
        try:
            data_updates = file_to_string(mod_folder + "/data-updates.lua")
            mod_data["data-updates.lua"] = data_updates
        except FileNotFoundError:
            pass
        try:
            data_final_fixes = file_to_string(mod_folder + "/data-final-fixes.lua")
            mod_data["data-final-fixes.lua"] = data_final_fixes
        except FileNotFoundError:
            pass

    # It's possible that a user might have multiples of the same mod with
    # different versions (issue #15). This can cause conficts where a
    # earlier version of the mod is loaded last which causes dependency
    # errors.

    # To fix this, we explicitly check for mods with a duplicate name, and
    # we only overwrite it if the latter mod's version is greater than the
    # existing mod's version.

    # In addition, if there are two versions of the same mod with equivalent
    # versions, but one is a zip archive and the other is a folder, then the
    # folder will take precedence over the zip file.

    current_mod = Mod(
        name=mod_name,
        internal_folder=mod_folder,
        version=mod_version,
        archive=archive,
        location=location.replace("\\", "/"),  # Make sure forward slashes
        info=mod_info,
        files=files,
        data=mod_data,
    )

    if verbose or report:
        # TODO: move this outside
        # TODO: show more information, like file location and whether it's enabled
        print("(zip)" if archive else "(dir)", mod_name, mod_version)

    # If a mod with this name already exists
    if mod_name in mods:
        # We warn the user, as this can lead to undesired behavior
        previous_mod = mods[mod_name]
        print(
            "WARNING: Duplicate of mod '{}' found (current: {} -> new: {})".format(
                mod_name, previous_mod.version, current_mod.version
            )
        )

        # Skip overwriting this mod if the current one is of a later version
        # than the current
        if version_string_to_tuple(previous_mod.version) < version_string_to_tuple(
            current_mod.version
        ):
            print(
                "\tOverwriting older version ({}) with newer version ({})".format(
                    previous_mod.version, current_mod.version
                )
            )
        elif version_string_to_tuple(previous_mod.version) > version_string_to_tuple(
            current_mod.version
        ):
            print(
                "\tSkipping older version ({}) in favor of newer version ({})".format(
                    current_mod.version, previous_mod.version
                )
            )
            return previous_mod
        else:  # versions are identical
            # If the previous mod is a folder, and the new mod is an archive,
            # defer to the folder
            if previous_mod.archive and not current_mod.archive:
                print("\tUsing folder version instead of zip archive")
            else:
                print("\tDeferring to folder version instead of zip archive")
                return previous_mod

    return current_mod


def update(
    verbose=False,
    game_path=None,
    mods_path=None,
    show_logs=False,
    no_mods=False,
    report=None,
    factorio_version=None,
) -> None:
    """
    Updates the data in the :py:mod:`.draftsman.data` modules.

    Emulates the load pattern of Factorio and loads all of its data (hopefully)
    in the same way. Then that data is extracted into the module, updating it's
    contents. Updates and changes made to the ``factorio-data`` folder are also
    reflected in this routine.

    :param verbose: Whether or not to print status updates to stdout.
    :param game_path: The specific path of the game installation. By default,
        this value points to the `factorio-data` repo inside of Draftsman, but
        this repo does not contain any assets. If you own the game and wish to
        extract these assets, then you can use this path to point directly to
        wherever your Factorio install is.
    :param mods_path: The specific path to use when searching for mods. Defaults
        to the folder `factorio-mods` located in the install directory of
        Draftsman. A common alternative path to use is your current Factorio
        install's mod folder, typically in `%APPDATA%/Roaming/Factorio/mods/`.
    :param show_logs: Whether or not to display logs created by the Factorio
        load process itself to stdout.
    :param no_mods: Whether or not to ignore non-official mods when performing
        the update. Wube developed expansions (mods) such as Quality, Elevated
        Rails, and Space Age are not omitted with this flag.
    :param report: If true, prints a list of all mods being used under the
        current configuration and then exits.
    :param factorio_version: If true, prints the current Git tag that the
        currently installed `factorio-data` uses and exits. If specified to a
        string, this function will treat that as the "target" tag and will
        attempt to set that tag to the new version. In addition to all known
        tags, `factorio_version` also reserves the phrase `"latest"`, which
        is simply a shorthand to the latest released version.

    .. NOTE::

        You'd think that the Git tag used for ``factorio-data`` and the
        generated value of ``draftsman.__factorio_version__`` would be equivalent;
        but this is NOT the case. In general the generated ``__factorio_version__``
        by Draftsman always points 1 version ahead of stable, while the git tag
        is always the stable version.
    """
    # TODO: `--report` and `--factorio-version` should really be extricated from
    # this function, they just don't belong here

    # Figure out what directory we're in
    env_dir = os.path.dirname(__file__)
    # Create some quick access folders
    factorio_data_path = os.path.join(env_dir, "factorio-data")
    data_location = os.path.join(env_dir, "data")

    # Check the currently checked out tag for `factorio-data`
    repo = Repo(factorio_data_path)
    repo.git.fetch()
    # https://stackoverflow.com/a/32524783/8167625
    current_tag = next(
        (tag for tag in repo.tags if tag.commit == repo.head.commit), None
    )

    if verbose or type(factorio_version) is bool:
        print("Current Factorio version: {}".format(current_tag.name))

    if type(factorio_version) is bool:
        return

    # We want to handle the case where the user specifies the string "latest":
    if factorio_version == "latest":
        factorio_version = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)[
            -1
        ]
    # If no preferred version was provided, we adopt the current version
    elif factorio_version is None:
        factorio_version = current_tag.name

    # Checkout a different version of `factorio-data` if necessary
    if factorio_version != current_tag.name:
        if verbose:
            print(
                "Different Factorio version requested ({}) -> ({})".format(
                    current_tag, factorio_version
                )
            )

        repo.git.checkout(factorio_version)

        if verbose:
            print("Changed to Factorio version {}\n".format(factorio_version))

    if mods_path is None:
        factorio_mods_folder = os.path.join(env_dir, "factorio-mods")
    else:
        factorio_mods_folder = mods_path

    if verbose:
        print("Reading mods from:", factorio_mods_folder)

    # Get the info from factorio-data and treat it as the "base" mod
    with open(os.path.join(factorio_data_path, "base", "info.json")) as base_info_file:
        base_info = json.load(base_info_file)
        factorio_version = base_info["version"]
        # Normalize it to 4 numbers to make our versioning lives easier
        if factorio_version.count(".") == 2:
            factorio_version += ".0"
        factorio_version_info = version_string_to_tuple(factorio_version)

    # Write `_factorio_version.py` with the current factorio version
    with open(os.path.join(env_dir, "_factorio_version.py"), "w") as version_file:
        version_file.write("# _factorio_version.py\n\n")
        version_file.write('__factorio_version__ = "' + factorio_version + '"\n')
        version_file.write(
            "__factorio_version_info__ = {}\n".format(str(factorio_version_info))
        )

    # This shouldn't need to be done, but lets create the factorio-mod folder if
    # it doesn't exist in case the user deletes the whole thing accidently
    if mods_path is None and not os.path.isdir(factorio_mods_folder):
        os.mkdir(factorio_mods_folder)

    # Check that our path actually exists (in case it was user specified)
    if not os.path.isdir(factorio_data_path):
        raise OSError("Directory '{}' not found".format(factorio_data_path))
    if not os.path.isdir(factorio_mods_folder):
        raise OSError("Directory '{}' not found".format(factorio_mods_folder))

    # Attempt to get the list of enabled mods from mod-list.json
    enabled_mod_list = {}
    try:
        with open(os.path.join(factorio_mods_folder, "mod-list.json")) as mod_list_file:
            mod_json = json.load(mod_list_file)
            for mod in mod_json["mods"]:
                enabled_mod_list[mod["name"].replace(" ", "")] = (
                    mod["enabled"] and not no_mods
                )
    except FileNotFoundError:  # If no such file is found
        pass  # Every mod is enabled by default, unless `no_mods` is True
        # enabled_mod_list["base"] = True
        # for mod_obj in os.listdir(factorio_mods_folder):
        #     if mod_obj.lower().endswith(".zip"):
        #         mod_name = mod_archive_regex.match(mod_obj).group(1).replace(" ", "")
        #         enabled_mod_list[mod_name] = not no_mods
        #     elif os.path.isdir(os.path.join(factorio_mods_folder, mod_obj)):
        #         mod_name = mod_obj
        #         enabled_mod_list[mod_name] = not no_mods

    if verbose:
        print("\nDiscovering mods...\n")

    # Dictionary of "mods". In factorio parlance, a Mod is a collection of files
    # associated with one another, meaning that base-game components like `base`
    # and `core` are also considered "mods".
    mods: dict[str, Mod] = {}

    # Because of this lack of distinction, we traverse the game-data folder and
    # treat every folder inside of it as a mod:
    for game_obj in os.listdir(factorio_data_path):
        location = factorio_data_path + "/" + game_obj  # TODO: better
        if not os.path.isdir(location):
            continue

        # First make sure the mod is enabled, and skip if not
        if not enabled_mod_list.get(game_obj, True):
            continue

        # Add the mod to the list of mods
        mods[game_obj] = register_mod(
            game_obj, location, mods, factorio_version_info, verbose, report
        )

    # After that, we can register all of the regular mods, if present
    for mod_obj in os.listdir(factorio_mods_folder):
        location = factorio_mods_folder + "/" + mod_obj  # TODO: better

        # First make sure the mod is enabled, and skip if not
        if not enabled_mod_list.get(mod_obj, not no_mods):
            continue

        # Add the mod to the list of mods
        mods[mod_obj] = register_mod(
            mod_obj, location, mods, factorio_version_info, verbose, report
        )

    if report:
        # TODO: reimplement properly
        # if len(mods) == 1: # just the base mod
        #     print("No mods found at '{}'.".format(factorio_mods_folder))
        return

    # Create the dependency tree
    if verbose:
        print("\nDetermining dependency tree...\n")
    for mod_name, mod in mods.items():
        # Core has no dependecies, so determining it's tree is redundant
        if mod_name == "core":
            continue
        # Base depends on core, though the game does not tell us this
        elif mod_name == "base":
            mod_dependencies = ["core"]
        # All other mod names. A user mod may not be specified with dependencies;
        # in this case, we make the mod dependent on the current Factorio base:
        else:
            print(mod_name, mod)
            mod_dependencies = mod.info.get("dependencies", ["base"])

        if verbose:
            print(mod_name, mod.version)
            print("archive?", mod.archive)
            print("dependencies:")

        for dependency in mod_dependencies:
            # remove whitespace for consistency
            dependency = "".join(dependency.split())
            m = dependency_regex.match(dependency)
            flag, dep_name, op, version = m[1], m[2], m[3], m[4]

            if verbose:
                print("\t", flag or " ", dep_name, op or "", version or "")

            if flag == "!":
                # Mod is incompatible with the current mod
                # Check if that mod exists in the mods folder
                if dep_name in mods:
                    # If it does, throw an error
                    raise IncompatableModError(mod_name)
                else:
                    continue  # Otherwise, don't worry about it
            elif flag == "?":
                # Mod is optional to the current mod
                if dep_name not in mods:
                    continue  # Don't worry about it

            # Now that we know this is a regular dependency, we ensure that it
            # exists
            if dep_name not in mods:
                raise MissingModError(dep_name)

            # Ensure the mod's version is correct
            # TODO: re-implement (#51)
            # if version is not None:
            #     assert op in ["==", ">=", "<=", ">", "<"], "incorrect operation"
            #     actual_version_tuple = version_string_to_tuple(mods[dep_name].version)
            #     target_version_tuple = version_string_to_tuple(version)
            #     expr = str(actual_version_tuple) + op + str(target_version_tuple)
            #     # print(expr)
            #     if not eval(expr):
            #         raise IncorrectModVersionError(
            #             "mod '{}' version {} not {} {}".format(
            #                 mod_name, actual_version_tuple, op, target_version_tuple
            #             )
            #         )

            if flag == "~":
                # The mod is needed and considered a dependency, but we don't
                # want it to modify the load order, so we skip that part
                continue

            mod.add_dependency(mods[dep_name])

    # Get load order (Sort the mods by the least to most deep dependency tree
    # first and their name second)
    load_order = [
        k[0] for k in sorted(mods.items(), key=lambda x: (x[1].get_depth(), x[1].name))
    ]

    if verbose:
        print("\nLoad order:")
        print(load_order, end="\n\n")

    # Setup emulated factorio environment (Set up at {site-packages}/draftsman)
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)

    # First we load `defines.lua` in this context, which is a set of constant
    # values used by the game. We do this first because these can be used at any
    # point in any of the subsequent steps.
    # This is not included in `factorio-data` and has to be manually extracted
    # (See compatibility/defines.lua for more info).
    lua.execute(file_to_string(os.path.join(env_dir, "compatibility", "defines.lua")))

    # "interface.lua" houses a number of patching functions used to emulate
    # Factorio's internal load process.
    # Primarily, it updates the require function to now handle python_require,
    # and fixes a few small discrepancies that Factorio's environment has.
    lua.execute(file_to_string(os.path.join(env_dir, "compatibility", "interface.lua")))

    # For ease of access, we setup some aliases and variables between the two
    # contexts:

    # Register logging status within Lua context
    lua.globals().LOG_ENABLED = show_logs

    # Record where to look for mod folders
    lua.globals().MOD_FOLDER_LOCATION = factorio_mods_folder

    # Adds path to Lua `package.path`.
    lua_add_path = lua.globals()["lua_add_path"]
    # Set Lua `package.path` to a specific value.
    lua_set_path = lua.globals()["lua_set_path"]
    # Unload all cached files. Lua attempts to save time when requiring files
    # by only loading each file once, and reusing the file when requiring with
    # the same name. This can lead to problems when two mods have the same name
    # for a file, where Lua will load the incorrect one and create issues.
    # To counteract this, we completly unload all files with this function,
    # which is called at the end of every load stage.
    lua_unload_cache = lua.globals()["lua_unload_cache"]
    # In order to properly search archives, we need to keep track of which file
    # and mod we're currently in. Due to a number of reasons, this needs to be
    # done manually; this function empties the stack of mods that we've
    # traversed through in preparation for loading the next mod's stage.
    lua_wipe_mods = lua.globals()["lua_wipe_mods"]

    # Register `python_require` in lua context.
    # This function is in charge of reading a required file from a zip archive
    # and providing the source to Lua's `require` function.
    lua.globals().python_require = python_require

    # Factorio utility functions
    lua.execute(
        file_to_string(os.path.join(factorio_data_path, "core", "lualib", "util.lua"))
    )

    # Because Lupa can't handle byte-order marks in input files, we can't rely
    # on Lua itself to load raw files using require unmodified
    # We can try to strip the byte-order mark on the Lua side of things, but
    # frankly I trust Python here way more than I trust Lua to handle file
    # formatting
    # So instead, we open a correctly encoded file on the python side of things
    # and then pass a file handle to Lua instead (which Lua reads from and
    # unloads)
    def python_get_file(filepath):
        try:
            return open(filepath, mode="r", encoding="utf-8-sig")
        except Exception as e:  # Exceptions in Lua are evil, so we don't do that
            return None, repr(e)

    lua.globals().python_get_file = python_get_file

    # TODO: FIXME
    # Set meta stuff
    lua.globals().MOD_LIST = mods
    # lua.globals().MOD = mod
    lua.globals().MOD_DIR = mods["core"].location
    lua.globals().lua_push_mod(mods["core"])
    lua.globals().CURRENT_FILE = mods["core"].location + "/lualib/dataloader.lua"

    # # Factorio `data:extend` function
    lua.execute(
        file_to_string(
            os.path.join(factorio_data_path, "core", "lualib", "dataloader.lua")
        )
    )

    # print(mods["core"].internal_folder)
    # lua.globals().CURRENT_FILE = os.path.join(factorio_data_path, "core", "lualib", "util.lua")
    # lua.globals().CURRENT_MOD
    # lua.globals().MOD_DIR = os.path.join(factorio_data_path, "core")
    # load_stage(lua, mods, mods["core"], "data.lua")

    # Construct and send the mods table to the Lua instance in `interface.lua`
    python_mods = {}
    for mod in mods:
        python_mods[mod] = mods[mod].version
    lua.globals().python_mods = python_mods
    # This is still a Python data structure though, so we run the following bit
    # of code to convert the `python_mods` global to the `mods` Lua table
    # Factorio wants
    lua.execute(
        """
    mods = {}
    for k in python.iter(python_mods) do
        mods[k] = python_mods[k]
    end
    """
    )

    # Add Draftsman's root folder to Lua (to access the `compatibility` folder)
    root_path = os.path.join(env_dir, "?.lua")
    lua_add_path(root_path)

    # Add the path to and setup the `core` module
    # This should probably be part of the main load process in case more than
    # "data.lua" is added to the core module, but core is kinda special and
    # would have to be integrated into the load order as a unique case anyway
    lualib_path = os.path.join(factorio_data_path, "core", "lualib", "?.lua")
    lua_add_path(lualib_path)
    # load_stage(lua, mods, core_mod, "data.lua")

    # We also add a special path, which is just the entire module
    # (This is used for absolute paths in archives, so we add it once here)
    lua_add_path("?.lua")

    # We want to include core in all further mods, so we set this as the "base"
    # path to return to every time a new mod is initialized
    base_path = lua.globals().package.path

    # Load the settings stage
    stages = ["settings.lua", "settings-updates.lua", "settings-final-fixes.lua"]
    for stage in stages:
        if verbose:
            print(stage.upper() + ":")

        for mod_name in load_order:
            mod = mods[mod_name]

            # Reset the directory so we dont require from different mods
            # Well, unless we need to. Otherwise, avoid it
            lua_set_path(base_path)

            if stage in mod.data:
                if verbose:
                    print("\tmod:", mod_name)

                # lua.execute(mod["data"]["data.lua"])
                load_stage(lua, mods, mod, stage)

                # Reset the included modules
                lua_unload_cache()

    # Factorio then converts the settings which were stored in data.raw
    # to the global 'settings' table: We emulate that here in 'settings.lua':
    lua.execute(file_to_string(os.path.join(env_dir, "compatibility", "settings.lua")))

    # If there is a mod settings file present, we overwrite the current values
    # with those
    try:
        user_settings = get_mod_settings(factorio_mods_folder)
        # If so, Overwrite the 'value' key for all the settings present
        for setting_type, setting_dict in user_settings.items():
            lua_settings = lua.globals().settings[setting_type]
            for name in setting_dict:
                if lua_settings[name] is not None:
                    lua_settings[name].value = setting_dict[name]["value"]
    except FileNotFoundError:
        pass

    # Load the data stage
    stages = ["data.lua", "data-updates.lua", "data-final-fixes.lua"]
    for stage in stages:
        if verbose:
            print(stage.upper() + ":")

        for mod_name in load_order:
            mod = mods[mod_name]

            # Reset the directory so we dont require from different mods
            # Well, unless we need to. Otherwise, avoid it
            lua_set_path(base_path)

            if stage in mod.data:
                if verbose:
                    print("\tmod:", mod_name)

                load_stage(lua, mods, mod, stage)

                # Reset the included modules
                lua_unload_cache()

                # Reset the MODS tree to an empty state
                lua_wipe_mods()

    # At this point, `data.raw` and all other constructs should(!) be properly
    # initialized. Hence, we can now extract the data we wish:

    if verbose:
        print()

    extract_mods(mods, data_location, verbose)  # Mod names and their versions

    # Lots of items are sorted by item order, subgroup and group
    # Here we get these things once and pass them into each extraction function
    # as necessary
    items = get_items(lua)

    extract_entities(lua, data_location, verbose, items)
    extract_fluids(lua, data_location, verbose, items)
    extract_instruments(lua, data_location, verbose)
    extract_items(lua, data_location, verbose, items)
    extract_modules(lua, data_location, verbose, items)
    extract_recipes(lua, data_location, verbose, items)
    extract_signals(lua, data_location, verbose, items)
    extract_tiles(lua, data_location, verbose)

    # TODO: Think about a way that users can extract the data that they want
    # instead of it being hardcoded for my purposes alone

    if verbose:
        print("\nUpdate finished.")  # Phew.
        print("hella slick; nothing broke!")


def main():
    """
    ``draftsman-update`` console script entry point. Runs ``update()`` with
    command line arguments passed through. Type ``draftsman-update -h`` for a
    list of commands.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show extra information during the update",
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        help="The path to search for mods; defaults to "
        "`python_install/site-packages/draftsman/factorio-mods`",
    )
    parser.add_argument(
        "-l",
        "--log",
        action="store_true",
        help="Display any 'log()' messages to stdout; any logged messages will "
        "be ignored if this argument is not set",
    )
    parser.add_argument(
        "--no-mods",
        action="store_true",
        help="Only load the 'base' mod and ignore all others; simulates no mods",
    )
    parser.add_argument(
        "--lua-version",
        action="store_true",
        help="Prints the version of Lua used when loading and exits",
    )
    parser.add_argument(
        "-r",
        "--report",
        nargs="?",
        default=None,
        const=True,
        help="Outputs a list of mods at '--path' as well as their configurations",
    )
    parser.add_argument(
        "--factorio-version",
        nargs="?",
        default=None,
        const=True,
        help="Displays the current Factorio version, or sets a particular Factorio version",
    )
    args = parser.parse_args()
    if args.lua_version:
        print(
            "Using {} (compiled with {})".format(
                lupa.LuaRuntime().lua_implementation, lupa.LUA_VERSION
            )
        )
    else:
        update(
            verbose=args.verbose,
            mods_path=args.path,
            show_logs=args.log,
            no_mods=args.no_mods,
            report=args.report,
            factorio_version=args.factorio_version,
        )
