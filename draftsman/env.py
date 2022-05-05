# env.py

"""
Manages the Factorio environment. Primarily holds :py:func:`draftsman.env.update()`,
which runs through the Factorio data lifecycle and updates the data in 
:py:mod:`draftsman.data`.
"""

# TODO:
# Make sure everything is sorted
# Make sure everything uses OrderedDict for backwards compatability(?)

from __future__ import print_function

# Python 2 compat
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError

from draftsman.error import (
    MissingModError,
    IncompatableModError,
    IncorrectModVersionError,
)
from draftsman.utils import decode_version, version_string_to_tuple
from draftsman._factorio_version import __factorio_version_info__

import argparse
from collections import OrderedDict
import json
import lupa
import os
import pickle
import re
import struct
import zipfile


mod_archive_pattern = "([\\w\\D]+)_([\\d\\.]+)\\."
mod_archive_regex = re.compile(mod_archive_pattern)

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


def file_to_string(filepath):
    """
    Simply grabs a file's contents and returns it as a string.
    """
    with open(filepath, mode="r") as file:
        return file.read()


def get_mod_settings(location):
    """
    Reads `mod_settings.dat` and stores it as an easy-to-read dict. Would be
    trivial to implement an editor with this function. (Well, assuming you write
    a function to export back to a ``.dat`` file)
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
        # print("String")
        string_absent = bool(
            # int.from_bytes(binary_stream.read(1), "little", signed=False)
            struct.unpack("<?", binary_stream.read(1))[0]
        )
        # print("string absent?", string_absent)
        if string_absent:
            return None
        # handle the Space Optimized length
        # length = int.from_bytes(binary_stream.read(1), "little", signed=False)
        length = struct.unpack("<B", binary_stream.read(1))[0]
        if length == 255:  # length is actually longer
            # length = int.from_bytes(binary_stream.read(4), "little", signed=False)
            length = struct.unpack("<I", binary_stream.read(4))[0]
        # print(length)
        return binary_stream.read(length).decode()

    def get_data(binary_stream):
        data_type = struct.unpack("<B", binary_stream.read(1))[0]
        # print("data_type:", data_type)
        binary_stream.read(1)  # any type flag, largely internal, ignore
        if data_type == PropertyTreeType["None"]:
            # print("None")
            return None
        elif data_type == PropertyTreeType["Bool"]:
            # print("Bool")
            return bool(struct.unpack("<?", binary_stream.read(1))[0])
        elif data_type == PropertyTreeType["Number"]:
            # print("Number")
            value = struct.unpack("d", binary_stream.read(8))[0]
            return value
        elif data_type == PropertyTreeType["String"]:
            return get_string(binary_stream)
        elif data_type == PropertyTreeType["List"]:
            # print("List")
            length = struct.unpack("<I", binary_stream.read(4))
            out = list()
            for i in range(length):
                out.append(get_data(binary_stream))
            return out
        elif data_type == PropertyTreeType["Dictionary"]:
            # print("Dict")
            length = struct.unpack("<I", binary_stream.read(4))[0]
            out = dict()
            for i in range(length):
                name = get_string(binary_stream)
                value = get_data(binary_stream)
                # print(name, value)
                out[name] = value
            return out

    mod_settings = {}
    with open(
        os.path.join(location, "mod-settings.dat"), mode="rb"
    ) as mod_settings_dat:
        # header
        # version_num = int.from_bytes(mod_settings_dat.read(8), "little")
        version_num = struct.unpack("<Q", mod_settings_dat.read(8))[0]
        # print(version_num)
        version = decode_version(version_num)
        # print(version)
        # header_flag = bool(int.from_bytes(mod_settings_dat.read(1), "little", signed=False))
        header_flag = bool(struct.unpack("<?", mod_settings_dat.read(1))[0])
        # print(header_flag)
        # assert version[::-1] >= __factorio_version_info__ and not header_flag
        mod_settings = get_data(mod_settings_dat)

    return mod_settings


def python_require(mod_list, current_mod, module_name, package_path):
    """
    Function called from Lua that checks for a file in a ``zipfile`` archive,
    and returns the contents of the file if found.

    Used in the modified Lua ``require()`` function that handles special cases
    to model Factorio's load pattern.
    """

    # Determine the mod we need
    try:
        mod_name = lua_module_regex.match(module_name)[1]
    except TypeError:
        mod_name = None

    if mod_name:
        mod = mod_list[mod_name]
    else:
        mod = current_mod

    if not mod.archive:
        return

    # emulate lua filepath searching
    filepaths = package_path.split(";")
    filepaths.insert(0, "?.lua")  # Add the raw module to the paths as well
    for filepath in filepaths:
        # Replace the question mark with the module_name
        filepath = filepath.replace("?", module_name)
        # Make it local to the archive
        filepath = filepath.replace("./factorio-mods/" + mod.name, mod.internal_folder)
        # Normalize for Zipfile
        filepath = filepath.replace("\\", "/")
        try:
            return mod.files.read(filepath)
        except KeyError:
            pass

    # otherwise
    return None, "no file '{}' found in '{}' archive".format(module_name, mod.name)


def load_stage(lua, mod_list, mod, stage):
    """
    Load a stage of the Factorio data lifecycle.
    """
    # Set meta stuff
    lua.globals().MOD_LIST = mod_list
    lua.globals().MOD = mod
    lua.globals().MOD_NAME = mod.name
    lua.globals().MOD_DIR = mod.location
    lua.globals().CURRENT_FILE = os.path.join(mod.location, stage)

    lua.globals().ADD_PATH(os.path.join(mod.location, "?.lua"))

    lua.execute(mod.data[stage])


def convert_table_to_dict(table):
    """
    Converts a Lua table to a Python dict. Correctly handles nesting, and
    interprets Lua arrays as lists.
    """
    out = dict(table)
    # print(out)
    is_list = True
    for key in out:
        # print(key)
        if not isinstance(key, int):
            is_list = False

        if lupa.lua_type(out[key]) == "table":
            # print(out[key])
            # out[key] = convert_table_to_dict(out[key])
            out[key] = convert_table_to_dict(out[key])
            # check if its actually a dict and not a list

    if is_list:
        return list(out.values())

    return out


def get_order(data, objects_to_sort):
    """
    Sorts the list of objects according to their Factorio order. Attempts to
    sort by item order first, and defaults to entity order if not present.

    Item sort order:
    (https://forums.factorio.com/viewtopic.php?p=23818#p23818)

    1. object groups
    2. object subgroups
    3. object itself

    Across the previous categories, each is sorted by:

    1. the item order string
    2. the item name (lexographic)
    """

    item_groups = convert_table_to_dict(data.raw["item-group"])
    item_subgroups = convert_table_to_dict(data.raw["item-subgroup"])
    items = convert_table_to_dict(data.raw["item"])
    # Rail planners:
    rail_planners = convert_table_to_dict(data.raw["rail-planner"])
    for _, rail_planner in rail_planners.items():
        straight_rail_name = rail_planner["straight_rail"]
        items[straight_rail_name] = rail_planner
        curved_rail_name = rail_planner["curved_rail"]
        items[curved_rail_name] = rail_planner

    def general_iterator(obj):
        if isinstance(obj, dict):
            return obj.values()
        else:
            return obj

    modified = []
    for object_to_sort in general_iterator(objects_to_sort):
        # Try to sort by item order if possible because thats more intuitive
        # Otherwise, fall back onto entity order
        if object_to_sort["name"] in items:
            sort_object = items[object_to_sort["name"]]
            # Get the item's sort name to actually sort with
            sort_name = sort_object["name"]
            # Replace only the order and its subgroup
            object_to_sort["order"] = sort_object["order"]
            try:
                object_to_sort["subgroup"] = sort_object["subgroup"]
            except KeyError:
                pass
        else:
            # Set the sort name to be identical to the actual object name
            sort_name = object_to_sort["name"]

        if "order" not in object_to_sort:
            object_to_sort["order"] = "zzzzzzzzzzzzzzzzzzzzzzz"

        if "subgroup" in object_to_sort:
            subgroup = item_subgroups[object_to_sort["subgroup"]]
        else:
            subgroup = item_subgroups["other"]

        group = item_groups[subgroup["group"]]  # "group" is required

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
                "obj": (object_to_sort["order"], sort_name, object_to_sort["name"]),
                "subgroup": (subgroup["order"], subgroup["name"]),
                "group": (group["order"], group["name"]),
            }
        )

    order = sorted(modified, key=lambda x: (x["group"], x["subgroup"], x["obj"]))
    return [x["obj"][2] for x in order]


# =============================================================================


def extract_mods(loaded_mods, data_location, verbose):
    """
    Extract all the mod versions to ``mods.pkl`` in :py:mod:`draftsman.data`.
    """
    out_mods = {}
    for mod in loaded_mods:
        out_mods[mod] = version_string_to_tuple(loaded_mods[mod].version)

    with open(os.path.join(data_location, "mods.pkl"), "wb") as out:
        pickle.dump(out_mods, out, pickle.HIGHEST_PROTOCOL)

    if verbose:
        print("Extracted mods...")


def extract_entities(lua, data_location, verbose):
    """
    Extracts the entities to ``entities.pkl`` in :py:mod:`draftsman.data`.
    """

    data = lua.globals().data

    items = convert_table_to_dict(data.raw["item"])

    entities = {}
    unordered_entities_raw = {}

    def categorize_entities(entity_table, target_list):
        entity_dict = convert_table_to_dict(entity_table)
        for entity_name, entity in entity_dict.items():
            flags = entity["flags"]
            if (
                "not-blueprintable" in flags or "not-deconstructable" in flags
            ):  # or "hidden" in flags
                continue
            # maybe move this to get_order?
            unordered_entities_raw[entity_name] = entity
            target_list.append(entity)

    def sort(target_list):
        sorted_list = get_order(data, target_list)
        for i, x in enumerate(sorted_list):
            target_list[i] = x

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
        unordered_entities_raw[inserter_name] = inserter
        if "order" not in inserter:
            inserter["order"] = items[inserter_name]["order"]
        if "filter_count" in inserter:
            entities["filter_inserters"].append(inserter)
        else:
            entities["inserters"].append(inserter)
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
    entities["curved_rails"] = []
    categorize_entities(data.raw["curved-rail"], entities["curved_rails"])
    sort(entities["curved_rails"])

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
        unordered_entities_raw[container_name] = container
        container_type = container["logistic_mode"]
        if "order" not in container:
            container["order"] = items[container_name]["order"]
        container_order = container["order"]
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

    #  Electric Energy Interfaces
    entities["electric_energy_interfaces"] = []
    categorize_entities(
        data.raw["electric-energy-interface"], entities["electric_energy_interfaces"]
    )
    sort(entities["electric_energy_interfaces"])

    #  Linked Containers
    entities["linked_containers"] = []
    try:
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
    try:
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

    raw_order = get_order(data, unordered_entities_raw)
    entities["raw"] = OrderedDict()
    for name in raw_order:
        entities["raw"][name] = unordered_entities_raw[name]

    with open(os.path.join(data_location, "entities.pkl"), "wb") as out:
        pickle.dump(entities, out, pickle.HIGHEST_PROTOCOL)

    if verbose:
        print("Extracted entities...")


# =============================================================================


def extract_instruments(lua, data_location, verbose):
    """
    Extracts the instruments to ``instruments.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    instrument_raw = {}
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

    # Ideally, I'd like to be able to write:
    # instruments.raw["programmable-speaker"]["alarms"] -> { ... }
    # instruments.raw["programmable-speaker"][0] -> { ... } # (same dict as above)

    # instruments.index["programmable-speaker"]["alarms"]["self"] -> 0
    # instruments.index["programmable-speaker"]["alarms"]["siren"] -> 6

    with open(os.path.join(data_location, "instruments.pkl"), "wb") as out:
        instrument_data = [instrument_raw, instrument_index, instrument_names]
        pickle.dump(instrument_data, out, pickle.HIGHEST_PROTOCOL)

    if verbose:
        print("Extracted instruments...")


# =============================================================================


def extract_items(lua, data_location, verbose):
    """
    Extracts the items to ``items.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    groups = convert_table_to_dict(data.raw["item-group"])
    subgroups = convert_table_to_dict(data.raw["item-subgroup"])

    def to_ordered_dict(elem):
        sorted_elem = OrderedDict()
        for v in elem:
            sorted_elem[v["name"]] = v
        return sorted_elem

    # Sort the groups and subgroups dictionaries
    test_values = sorted(list(groups.values()), key=lambda x: x["order"])
    # sorted_groups = {}
    # for v in test_values:
    #     sorted_groups[v["name"]] = v
    sorted_groups = to_ordered_dict(test_values)

    test_values = sorted(list(subgroups.values()), key=lambda x: x["order"])
    # sorted_subgroups = {}
    # for v in test_values:
    #     sorted_subgroups[v["name"]] = v
    sorted_subgroups = to_ordered_dict(test_values)

    index_dict = {}

    # Initialize item groups
    group_list = list(groups.values())
    for group in group_list:
        group["subgroups"] = []
        index_dict[group["name"]] = group

    # Initialize item subgroups
    subgroup_list = list(subgroups.values())
    for subgroup in subgroup_list:
        subgroup["items"] = []
        parent_group = index_dict[subgroup["group"]]
        parent_group["subgroups"].append(subgroup)
        index_dict[subgroup["name"]] = subgroup

    def add_item(category, item_name):
        item = category[item_name]
        # if "flags" in item:
        #     if "hidden" in item["flags"].values():
        #         return
        if "subgroup" in item:
            subgroup = index_dict[item["subgroup"]]
        else:
            subgroup = index_dict["other"]
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
                    key=lambda x: (x["order"], x["name"]),
                )
            )
        group_list[i]["subgroups"] = to_ordered_dict(
            sorted(group_list[i]["subgroups"], key=lambda x: (x["order"], x["name"]))
        )
    group_list = sorted(group_list, key=lambda x: (x["order"], x["name"]))

    # print(json.dumps(group_list[0]["subgroups"], indent=2))

    # print(json.dumps(sorted_groups, indent=2))

    # Flatten into all_items dictionary
    sorted_items = OrderedDict()
    for group in group_list:
        for subgroup_name in group["subgroups"]:
            subgroup = group["subgroups"][subgroup_name]
            for item_name in subgroup["items"]:
                item = subgroup["items"][item_name]
                sorted_items[item["name"]] = item

    with open(os.path.join(data_location, "items.pkl"), "wb") as out:
        items = [sorted_items, sorted_subgroups, sorted_groups]
        pickle.dump(items, out, pickle.HIGHEST_PROTOCOL)

    if verbose:
        print("Extracted items...")


# =============================================================================


def extract_modules(lua, data_location, verbose):
    """
    Extracts the modules to ``modules.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    # Init categories
    categories = convert_table_to_dict(data.raw["module-category"])
    out_categories = {}
    for category in categories:
        out_categories[category] = []

    modules = convert_table_to_dict(data.raw["module"])
    unsorted_modules_raw = {}
    for module in modules:
        unsorted_modules_raw[module] = modules[module]
        module_type = modules[module]["category"]
        out_categories[module_type].append(module)

    raw_order = get_order(data, unsorted_modules_raw)
    modules_raw = OrderedDict()
    for name in raw_order:
        modules_raw[name] = unsorted_modules_raw[name]

    with open(os.path.join(data_location, "modules.pkl"), "wb") as out:
        pickle.dump([modules_raw, out_categories], out, pickle.HIGHEST_PROTOCOL)

    if verbose:
        print("Extracted modules...")


# =============================================================================


def extract_recipes(lua, data_location, verbose):
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
        if "category" in unsorted_recipes[recipe]:
            category = unsorted_recipes[recipe]["category"]
        else:
            category = "crafting"
        out_categories[category].append(unsorted_recipes[recipe]["name"])

    machines = convert_table_to_dict(data.raw["assembling-machine"])
    for machine_name in machines:
        for_machine[machine_name] = []
        machine = machines[machine_name]
        for category_name in machine["crafting_categories"]:
            category = out_categories[category_name]
            for recipe_name in category:
                for_machine[machine_name].append(recipe_name)

    # TODO: sort all recipes and categories
    # Problem here is that we should use recipe groups and subgroups instead of
    # item groups and subgroups
    # recipe_order = get_order(data, unsorted_recipes)
    # print(recipe_order)
    # recipes = OrderedDict()

    with open(os.path.join(data_location, "recipes.pkl"), "wb") as out:
        data = [unsorted_recipes, out_categories, for_machine]
        pickle.dump(data, out, pickle.HIGHEST_PROTOCOL)

    if verbose:
        print("Extracted recipes...")


# =============================================================================


def extract_signals(lua, data_location, verbose):
    """
    Extracts the signals to ``signals.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    signals = {}
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
            signals[signal_name] = signal_type
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

    item_signals = get_order(data, item_signals)
    # for signal in fluid_signals:
    #     print(signal)
    fluid_signals = get_order(data, fluid_signals)
    virtual_signals = get_order(data, virtual_signals)

    with open(os.path.join(data_location, "signals.pkl"), "wb") as out:
        data = [signals, item_signals, fluid_signals, virtual_signals]
        pickle.dump(data, out, pickle.HIGHEST_PROTOCOL)

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
        if "order" not in tiles[tile]:
            tiles[tile]["order"] = "zzzzzzzzzzzzzzzzzzzzzzzzz"
        tile_list.append((tiles[tile]["order"], tile))

    # Sort
    result = sorted(tile_list)
    result = [x[1] for x in result]

    # Construct new output dict
    out_tiles = {}
    for tile in result:
        out_tiles[tile] = tiles[tile]

    with open(os.path.join(data_location, "tiles.pkl"), "wb") as out:
        pickle.dump(out_tiles, out, pickle.HIGHEST_PROTOCOL)

    if verbose:
        print("Extracted tiles...")


# =============================================================================


def update(verbose=False, no_mods=False):
    """
    Updates the data in the :py:mod:`.draftsman.data` modules.

    Emulates the load pattern of Factorio and loads all of its data (hopefully)
    in the same way. Then that data is extracted into the module, updating it's
    contents. Updates and changes made to the ``factorio-data`` folder are also
    reflected in this routine.
    """
    # Figure out what directory we're in
    env_dir = os.path.dirname(__file__)
    # Create some quick access folders
    factorio_data = os.path.join(env_dir, "factorio-data")
    factorio_mods = os.path.join(env_dir, "factorio-mods")
    data_location = os.path.join(env_dir, "data")

    # Get the info from factorio-data and treat it as the "base" mod
    with open(os.path.join(factorio_data, "base", "info.json")) as base_info_file:
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
            "__factorio_version_info__ = {}".format(str(factorio_version_info))
        )

    # Dictionary of mods
    mods = {}

    # Add "base" and "core" mods
    # Core mod is somewhat special, and not loaded in the standard lifecycle
    # Instead, it is loaded first thing and its functions are reused throughout
    core_mod = Mod(
        name="core",
        internal_folder=None,
        version=factorio_version,
        archive=False,
        location=os.path.join(
            factorio_data, "core"
        ),  # "./draftsman/factorio-data/core",
        info=None,
        files=None,
        data={
            "data.lua": file_to_string(
                os.path.join(factorio_data, "core", "data.lua")
            )  # file_to_string("draftsman/factorio-data/core/data.lua")
        },
    )
    mods["base"] = Mod(
        name="base",
        internal_folder=None,
        version=factorio_version,
        archive=False,
        location=os.path.join(
            factorio_data, "base"
        ),  # "./draftsman/factorio-data/base",
        info=None,
        files=None,
        data={
            "data.lua": file_to_string(
                os.path.join(factorio_data, "base", "data.lua")
            ),  # file_to_string("draftsman/factorio-data/base/data.lua"),
            "data-updates.lua": file_to_string(
                os.path.join(factorio_data, "base", "data-updates.lua")
            ),  # file_to_string("draftsman/factorio-data/base/data-updates.lua")
        },
    )

    # Attempt to get the list of enabled mods from mod-list.json
    mod_list = {}
    try:
        with open(os.path.join(factorio_mods, "mod-list.json")) as mod_list_file:
            mod_json = json.load(mod_list_file)
            for mod in mod_json["mods"]:
                mod_list[mod["name"]] = mod["enabled"] and not no_mods
    except FileNotFoundError:  # If no such file is found
        # Every mod is enabled by default, unless `no_mods` is True
        mod_list["base"] = True
        for mod_obj in os.listdir(factorio_mods):
            if mod_obj.lower().endswith(".zip"):
                mod_name = mod_archive_regex.match(mod_obj).group(1)
                mod_list[mod_name] = not no_mods
            elif os.path.isdir(os.path.join(factorio_mods, mod_obj)):
                mod_name = mod_obj
                mod_list[mod_name] = not no_mods

    # Preload all the mods and their versions
    for mod_obj in os.listdir(factorio_mods):
        mod_name = None
        mod_version = None
        mod_location = os.path.join(factorio_mods, mod_obj)
        archive = None
        mod_info = None
        data = {}

        if mod_obj.lower().endswith(".zip"):  # Zip file

            m = mod_archive_regex.match(mod_obj)
            mod_name = m.group(1)
            external_mod_version = m.group(2)
            files = zipfile.ZipFile(mod_location, mode="r")
            # (Zipfiles don't like backslashes even on Windows)
            try:
                internal_folder = mod_name
                mod_info = json.loads(files.read(internal_folder + "/info.json"))
            except KeyError:
                internal_folder = "{}_{}".format(mod_name, external_mod_version)
                mod_info = json.loads(files.read(internal_folder + "/info.json"))
            mod_version = mod_info["version"]
            archive = True

            # Idiot check:
            assert version_string_to_tuple(
                external_mod_version
            ) == version_string_to_tuple(mod_version)

        elif os.path.isdir(os.path.join(factorio_mods, mod_obj)):  # Folder

            # TODO: mod folders can also be named with the "name_version" format
            mod_name = mod_obj
            with open(os.path.join(mod_location, "info.json"), "r") as info_file:
                mod_info = json.load(info_file)
            mod_version = mod_info["version"]
            archive = False

            raise NotImplementedError("working on it")  # TODO: finish

        else:  # Regular file
            continue  # Ignore

        # First make sure the mod is enabled
        if not mod_list[mod_name]:
            continue

        # Ensure that the mod's factorio version is correct
        mod_factorio_version = version_string_to_tuple(mod_info["factorio_version"])
        assert mod_factorio_version <= factorio_version_info

        mod_data = {}
        # Attempt to load setting files
        try:
            settings = files.read(internal_folder + "/settings.lua")
            mod_data["settings.lua"] = settings
        except KeyError:
            pass
        try:
            settings = files.read(internal_folder + "/settings-updates.lua")
            mod_data["settings-updates.lua"] = settings
        except KeyError:
            pass
        try:
            settings = files.read(internal_folder + "/settings-final-fixes.lua")
            mod_data["settings-final-fixes.lua"] = settings
        except KeyError:
            pass
        # Attempt to load data files
        try:
            data = files.read(internal_folder + "/data.lua")
            mod_data["data.lua"] = data
        except KeyError:
            pass
        try:
            data_updates = files.read(internal_folder + "/data-updates.lua")
            mod_data["data-updates.lua"] = data_updates
        except KeyError:
            pass
        try:
            data_final_fixes = files.read(internal_folder + "/data-final-fixes.lua")
            mod_data["data-final-fixes.lua"] = data_final_fixes
        except KeyError:
            pass

        mods[mod_name] = Mod(
            name=mod_name,
            internal_folder=internal_folder,
            version=mod_version,
            archive=archive,
            location="./factorio-mods/" + mod_name,  # maybe absolute?
            info=mod_info,
            files=files,
            data=mod_data,
        )

    # Create the dependency tree
    for mod_name, mod in mods.items():
        if mod_name == "base" or mod_name == "core":
            continue  # clunky, but works for now

        if verbose:
            print(mod_name, mod.version)
            print("dependencies:")

        for dependency in mod.info["dependencies"]:
            # remove whitespace for consistency
            dependency = "".join(dependency.split())
            m = dependency_regex.match(dependency)
            flag, dep_name, op, version = m[1], m[2], m[3], m[4]

            if verbose:
                print("\t", flag or " ", dep_name, op or "", version or "")

            if flag == "!":
                # Check if that mod exists in the mods folder
                if dep_name in mods:
                    # if it does, throw an error
                    raise IncompatableModError(mod_name)
                else:
                    continue
            elif flag == "?":
                if dep_name not in mods:
                    continue

            # Ensure that the mod exists
            if dep_name not in mods:
                raise MissingModError(dep_name)

            if flag == "~":
                # The mod is needed, but its not considered a dependency, so
                # don't modify the tree
                continue

            # Ensure version is correct
            if version is not None:
                assert op in ["==", ">=", "<=", ">", "<"], "incorrect operation"
                actual_version_tuple = version_string_to_tuple(mods[dep_name].version)
                target_version_tuple = version_string_to_tuple(version)
                expr = str(actual_version_tuple) + op + str(target_version_tuple)
                # print(expr)
                if not eval(expr):
                    raise IncorrectModVersionError(version)

            mod.add_dependency(mods[dep_name])

    # Get load order
    load_order = [
        k[0] for k in sorted(mods.items(), key=lambda x: (x[1].get_depth(), x[1].name))
    ]

    if verbose:
        print("Load order:")
        print(load_order)

    # Setup emulated factorio environment
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)

    # Factorio utils
    lua.execute(
        file_to_string(os.path.join(factorio_data, "core", "lualib", "util.lua"))
    )
    lua.execute(
        file_to_string(os.path.join(factorio_data, "core", "lualib", "dataloader.lua"))
    )

    # Construct and send the mods table to the lua instance
    python_mods = {}
    for mod in mods:
        python_mods[mod] = mods[mod].version
    lua.globals().python_mods = python_mods

    # Register `python_require` in lua context
    lua.globals().python_require = python_require

    # Register more compatability changes and define helper functions
    lua.execute(file_to_string(os.path.join(env_dir, "compatibility", "interface.lua")))
    # Get the functions from Lua for ease of access
    ADD_PATH = lua.globals()["ADD_PATH"]
    SET_PATH = lua.globals()["SET_PATH"]
    UNLOAD_SESSION_CACHE = lua.globals()["UNLOAD_SESSION_CACHE"]
    UNLOAD_ENTIRE_CACHE = lua.globals()["UNLOAD_ENTIRE_CACHE"]
    RESET_MOD_STATE = lua.globals()["RESET_MOD_STATE"]

    # Add our root folder to lua (compatibility folder)
    root_path = os.path.join(env_dir, "?.lua")
    ADD_PATH(root_path)

    # Setup the `core` module
    lualib_path = os.path.join(factorio_data, "core", "lualib", "?.lua")
    ADD_PATH(lualib_path)
    load_stage(lua, mods, core_mod, "data.lua")

    # We want to keep core constant, so we wipe the deletion table
    # NOTE: this might end up being a problem, to be safe we might just
    # completely wipe the cache every mod we load
    UNLOAD_SESSION_CACHE()
    lua.execute("required_in_session = {}")

    # We want to include core in all further mods, so we set this as the "base"
    base_path = lua.globals().package.path

    # Load the settings stage
    stages = ["settings.lua", "settings-updates.lua", "settings-final-fixes.lua"]
    for stage in stages:
        if verbose:
            print(stage.upper() + ":")

        for i, mod_name in enumerate(load_order):
            mod = mods[mod_name]

            # Reset the directory so we dont require from different mods
            # Well, unless we need to. Otherwise, avoid it
            SET_PATH(base_path)

            if stage in mod.data:
                if verbose:
                    print("\tmod:", mod_name)

                # lua.execute(mod["data"]["data.lua"])
                load_stage(lua, mods, mod, stage)

                # Reset the included modules
                UNLOAD_ENTIRE_CACHE()

                # Reset the deletion table
                RESET_MOD_STATE()

    # Factorio then converts the settings which were stored in data.raw
    # to the global 'settings' table: We emulate that here in 'settings.lua'
    lua.execute(file_to_string(os.path.join(env_dir, "compatibility", "settings.lua")))

    try:  # to read mod settings from the dat file if present
        user_settings = get_mod_settings(factorio_mods)
        # If so, Overwrite the 'value' key for all the settings
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

        for i, mod_name in enumerate(load_order):
            mod = mods[mod_name]

            # Reset the directory so we dont require from different mods
            # Well, unless we need to. Otherwise, avoid it
            SET_PATH(base_path)

            if stage in mod.data:
                if verbose:
                    print("\tmod:", mod_name)

                # lua.execute(mod["data"]["data.lua"])
                load_stage(lua, mods, mod, stage)

                # Reset the included modules
                UNLOAD_ENTIRE_CACHE()

                # Reset the deletion table
                RESET_MOD_STATE()

    extract_mods(mods, data_location, verbose)

    extract_entities(lua, data_location, verbose)
    extract_instruments(lua, data_location, verbose)
    extract_items(lua, data_location, verbose)
    extract_modules(lua, data_location, verbose)
    extract_recipes(lua, data_location, verbose)
    extract_signals(lua, data_location, verbose)
    extract_tiles(lua, data_location, verbose)

    print("Update finished.")


def main():
    """
    ``draftsman-update`` console script entry point. Runs ``update()`` with
    command line arguments passed through. Type ``draftsman-update -h`` for a
    list of commands for ``draftsman-update``.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show extra information during the update",
    )
    parser.add_argument(
        "--no-mods",
        action="store_true",
        help="Only load the 'base' mod and ignore all others; simulates no mods",
    )
    args = parser.parse_args()
    update(verbose=args.verbose, no_mods=args.no_mods)
    print("hella slick; nothing broke!")
