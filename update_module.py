# update_module.py

"""
Updates the `draftsman` structures and objects to the current mods and base.
Use this function if you've added/altered/removed mods or updated the factorio
data version.
"""

# TODO:
# handle version numbers with errors if incompatable (DONE)
# handle optionals and conflicts (DONE)
# Load mod-list.json and only enable mods if they're enabled inside it (DONE)
# Read mod-settings.dat and import it into compatability.lua so prototypes can read them (DONE)
# Extract the version info from factorio-data and write it out (DONE)
# Keep track of all loaded lua modules, and unload them on mod change so the cache doesn't get ahead of itself (DONE)
# Keep track of mods table; seems to keep mod versions under their keys (DONE)
# Recursively iterate through all directories within the mod folder and modify package.path (DONE)
# Figure out a way to load all mods without extracting them(!) (DONE)
# Unify mod loading between base, core and all other mods (DONE)

# Allow mods to be either extracted or in folders (change version to the one in `info.json`)
# Create a testing suite to test edge cases
# Make it so that mods can load files from other mods

from email import generator
from lib2to3.pytree import convert
from draftsman.errors import (
    MissingMod, 
    IncompatableMod, 
    IncorrectModVersion
)
from draftsman.utils import decode_version, version_string_2_tuple

import json
import lupa
import os
import pickle
import re
import struct
import zipfile


verbose = True

mod_archive_pattern = "([\\w\\D]+)_([\\d\\.]+)\\."
mod_archive_regex = re.compile(mod_archive_pattern)

dependency_string_pattern = "[^\\w\\?\\!~]*([\\?\\!~])?[^\\w\\?\\!]*([\\w-]+)([><=]=?)?([\\d\\.]+)?"
dependency_regex = re.compile(dependency_string_pattern)


class DepNode:
    def __init__(self, name, *deps):
        self.name = name
        self.set_elements(*deps)

    def set_elements(self, *deps):
        self.deps = [*deps]
        self.deps.sort()

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return "Node(" + self.name + ")" + str(self.deps)


class Mod:
    def __init__(self, name, version, archive, location, info, files, data):
        self.name = name
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
            "dependencies": self.dependencies
        }

    def __lt__(self, other):
        return self.name < other.name

    def __repr__(self):
        return str(self.to_dict())


def file_to_string(filepath):
    with open(filepath, mode="r") as file:
        return file.read()


def get_mod_settings():
    # Property Tree Enum
    PropertyTreeType = {
        "None": 0,
        "Bool": 1,
        "Number": 2,
        "String": 3,
        "List": 4,
        "Dictionary": 5
    }

    def get_string(binary_stream):
        #print("String")
        string_absent = bool(
            int.from_bytes(binary_stream.read(1), "little", signed=False)
        )
        #print("string absent?", string_absent)
        if string_absent:
            return None
        # handle the Space Optimized length
        length = int.from_bytes(binary_stream.read(1), "little", signed=False)
        if length == 255: # length is actually longer
            length = int.from_bytes(binary_stream.read(4), "little", signed=False)
        #print(length)
        return binary_stream.read(length).decode()

    def get_data(binary_stream):
        data_type=int.from_bytes(binary_stream.read(1), "little", signed=False)
        #print("data_type:", data_type)
        binary_stream.read(1) # any type flag, largely internal, ignore
        if data_type == PropertyTreeType["None"]:
            #print("None")
            return None
        elif data_type == PropertyTreeType["Bool"]:
            #print("Bool")
            return bool(
                int.from_bytes(binary_stream.read(1), "little", signed=False)
            )
        elif data_type == PropertyTreeType["Number"]:
            #print("Number")
            value = struct.unpack('d', binary_stream.read(8))[0]
            return value
        elif data_type == PropertyTreeType["String"]:
            return get_string(binary_stream)
        elif data_type == PropertyTreeType["List"]:
            #print("List")
            length = int.from_bytes(binary_stream.read(4), "little", signed=False)
            out = list()
            for i in range(length):
                out.append(get_data(binary_stream))
            return out
        elif data_type == PropertyTreeType["Dictionary"]:
            #print("Dict")
            length = int.from_bytes(binary_stream.read(4), "little", signed=False)
            #print("length:", length)
            out = dict()
            for i in range(length):
                name = get_string(binary_stream)
                value = get_data(binary_stream)
                #print(name, value)
                out[name] = value
            return out

    mod_settings = {}
    with open("factorio-mods/mod-settings.dat", mode="rb") as mod_settings_dat:
        # header
        version_num = int.from_bytes(mod_settings_dat.read(8), "little")
        #print(version_num)
        version = decode_version(version_num)
        #print(version)
        header_flag = bool(int.from_bytes(mod_settings_dat.read(1), "little", signed=False))
        #print(header_flag)
        # TODO version is not quite right, seems to be backwards?
        #assert version == __factorio_version_info__ and not header_flag
        mod_settings = get_data(mod_settings_dat)
        
        if verbose:
            print("mod-settings.dat:")
            print(json.dumps(mod_settings, indent=4))

    return mod_settings


def python_require(mod, module_name, package_path):
    """
    Function called from lua that attempts to get the python copy of the data.

    TODO: might be better to have this be entirely on the lua side, but this 
    works for now
    """
    #print("PYTHON: ", module_name)

    if not mod.archive: 
        return
    
    # emulate lua filepath searching
    filepaths = package_path.split(';')
    filepaths.insert(0, "?.lua") # Add the raw module to the paths as well
    for filepath in filepaths:
        # Replace the question mark with the module_name
        filepath = filepath.replace("?", module_name)
        # Make it local to the archive
        filepath = filepath.replace("./factorio-mods/" + mod.name, mod.name)
        try:
            return mod.files.read(filepath)
        except:
            pass        

    # otherwise
    return None, "no file '{}' found in '{}' archive".format(module_name, mod.name)


def load_stage(lua, mod, stage):
    """
    Load a stage of the Factorio data lifecycle.
    """
    # Set meta stuff
    current_file = mod.location + "/" + stage
    lua.globals().MOD = mod
    lua.globals().MOD_NAME = mod.name
    lua.globals().MOD_DIR = mod.location
    lua.globals().CURRENT_FILE = current_file

    lua.globals().ADD_PATH(mod.location + "/?.lua") # TODO: maybe remove?

    # print(current_file)
    # if mod["archive"]:
    #     pass
    # else:
    #     lua.execute(file_to_string(current_file))
    lua.execute(mod.data[stage])


def update():
    """
    Updates the data in the `draftsman` module. Emulates the load pattern of
    Factorio and loads all of its data (hopefully) in the same way. Then that
    data is extracted into the module, updating its contents. Updates and 
    changes made to `factorio-data` are also reflected in this routine.

    NOTE: this function does NOT update mods or the factorio-data master repo!
    First you will have to run `update_data.py` to actually update the data, 
    then you can call this function to resolve the changes in the module.
    Clunky, but sometimes you don't want to do both!
    """
    # Get the info from factorio-data and treat it as the "base" mod
    with open("factorio-data/base/info.json") as base_info_file:
        base_info = json.load(base_info_file)
        factorio_version = base_info["version"]
        # Normalize it to 4 numbers to make our versioning lives easier
        if factorio_version.count('.') == 2:
            factorio_version += ".0"
        factorio_version_info = version_string_2_tuple(factorio_version)


    # Write `_factorio_version.py` with the current factorio version
    with open("draftsman/_factorio_version.py", "w") as version_file:
        version_file.write("# _factorio_version.py\n\n")
        version_file.write('__factorio_version__ = "'+factorio_version+'"\n')
        version_file.write("__factorio_version_info__ = " + str(factorio_version_info))

    # What does a mod need to have
    # Name
    # Version
    # Location
    # all the files it needs to execute itself

    # build the dependency tree
    dependency_tree = []
    mods = {}
    # Add "base" and "core" mods
    core_mod = Mod(
        name = "core",
        version = factorio_version,
        archive = False,
        location = "./factorio-data/core",
        info = None,
        files = None,
        data = {
            "data.lua": file_to_string("factorio-data/core/data.lua")
        }
    )
    mods["base"] = Mod(
        name = "base",
        version = factorio_version,
        archive = False,
        location = "./factorio-data/base",
        info = None,
        files = None,
        data = {
            "data.lua": file_to_string("factorio-data/base/data.lua"),
            "data-updates.lua": file_to_string("factorio-data/base/data-updates.lua")
        }
    )

    # Attempt to get the list of enabled mods from mod-list.json
    # TODO: throw an error if mods are found but no mod list or mod settings
    # file is found
    mod_list = {}
    try:
        with open("factorio-mods/mod-list.json") as mod_list_file:
            mod_json = json.load(mod_list_file)
            for mod in mod_json["mods"]:
                mod_list[mod["name"]] = mod["enabled"]
    except FileNotFoundError:
        mod_list["base"] = True

    # Preload all the mods and their versions
    for mod_obj in os.listdir("factorio-mods"):
        print("\t", mod_obj)
        mod_name = None
        mod_version = None
        mod_location = os.path.join("factorio-mods", mod_obj)
        archive = None
        mod_info = None
        data = {}

        if mod_obj.lower().endswith(".zip"): # Zip file
            print("Zipfile")

            # NOTE: we assume the filename version and the internal json version are the same
            m = mod_archive_regex.match(mod_obj)
            mod_name = m[1]
            external_mod_version = m[2]

            files = zipfile.ZipFile(mod_location, mode="r")

            mod_info = json.loads(files.read(mod_name + "/info.json"))

            mod_version = mod_info["version"]

            archive = True

            assert version_string_2_tuple(external_mod_version) == version_string_2_tuple(mod_version)            

        elif os.path.isdir("factorio-mods/" + mod_obj): # Regular Folder
            print("Folder")

            mod_name = mod_obj

            with open(mod_location + "/info.json", "r") as info_file:
                mod_info = json.load(info_file)

            raise Exception("Not ready yet!")

        else: # Regular file
            continue # Ignore

        print("mod_info:", mod_info)

        if verbose:
            print(mod_obj)
            print(mod_name)
            print(mod_version)
            print(archive)
            print(mod_location)

        # Ensure that the mod's factorio version is correct
        mod_factorio_version = version_string_2_tuple(mod_info["factorio_version"])
        assert mod_factorio_version <= factorio_version_info

        # First make sure the mod is enabled
        if not mod_list[mod_name]:
            continue

        if mod_list[mod_name]:
            # Attempt to load data files
            mod_data = {}
            try:
                data = files.read(mod_name + "/data.lua")
                mod_data["data.lua"] = data
            except:
                pass
            try:
                data_updates = files.read(mod_name + "/data-updates.lua")
                mod_data["data-updates.lua"] = data_updates
            except:
                pass
            try:
                data_final_fixes = files.read(mod_name + "/data-final-fixes.lua")
                mod_data["data-final-fixes.lua"] = data_final_fixes
            except:
                pass

            mods[mod_name] = Mod(
                name = mod_name,
                version = mod_version,
                archive = archive, 
                location = "./factorio-mods/" + mod_name,
                info = mod_info,
                files = files,
                data = mod_data
            )

    # Create the dependency tree
    for mod_name, mod in mods.items():
        if mod_name == "base" or mod_name == "core":
            continue # clunky, but works for now

        if verbose:
            print(mod_name, mod.version)
            print("dependencies:")

        # TODO: check if all mods should have dependencies
        for dependency in mod.info["dependencies"]:
            # remove whitespace for consistency
            dependency = "".join(dependency.split())
            m = dependency_regex.match(dependency)
            flag, dep_name, op, version = m[1], m[2], m[3], m[4]
            
            if verbose:
                print("\t", flag or " ", dep_name, op or "", version or "")

            if flag == '!':
                # Check if that mod exists in the mods folder
                if dep_name in mods:
                    # if it does, throw an error
                    raise IncompatableMod(mod_name)
                else:
                    continue
            elif flag == '?':
                if dep_name not in mods:
                    continue

            # Ensure that the mod exists
            if dep_name not in mods:
                raise MissingMod(dep_name)

            if flag == '~':
                # The mod is needed, but its not considered a dependency, so
                # don't modify the tree
                continue

            # Ensure version is correct
            if version is not None:
                assert op in ["==", ">=", "<=", ">", "<"], "incorrect operation"
                actual_version_tuple = version_string_2_tuple(mods[dep_name].version)
                target_version_tuple = version_string_2_tuple(version)
                expr = str(actual_version_tuple) + op + str(target_version_tuple)
                #print(expr)
                if not eval(expr):
                    raise IncorrectModVersion(version)

            mod.add_dependency(mods[dep_name])

    # Get load order
    load_order = [
        k[0] for k in sorted(
            mods.items(), 
            key = lambda x: (x[1].get_depth(), x[1].name)
        )
    ]

    if verbose:
        print("Load order:")
        print(load_order)

    # Setup emulated factorio environment
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)

    # Factorio utils
    lua.execute(file_to_string("factorio-data/core/lualib/util.lua"))
    lua.execute(file_to_string("factorio-data/core/lualib/dataloader.lua"))
    
    # Attempt to read mod settings and set in lua context
    try:
        mod_settings = get_mod_settings()
    except FileNotFoundError:
        mod_settings = {}
    lua.globals().settings = mod_settings

    # Construct and send the mods table to the lua instance
    python_mods = {} # TODO
    for mod in mods:
        python_mods[mod] = mods[mod].version
    lua.globals().python_mods = python_mods

    # Register `python_require` in lua context
    lua.globals().python_require = python_require

    # Register more compatability changes and define helper functions
    lua.execute(file_to_string("draftsman/compatability/compatability.lua"))
    # Get the functions from Lua for ease of access
    ADD_PATH             = lua.globals()["ADD_PATH"]
    SET_PATH             = lua.globals()["SET_PATH"]
    UNLOAD_SESSION_CACHE = lua.globals()["UNLOAD_SESSION_CACHE"]
    UNLOAD_ENTIRE_CACHE  = lua.globals()["UNLOAD_ENTIRE_CACHE"]
    RESET_MOD_STATE      = lua.globals()["RESET_MOD_STATE"]

    # Setup the `core` module
    ADD_PATH("./factorio-data/core/lualib/?.lua")
    load_stage(lua, core_mod, "data.lua")

    # we want to keep core constant, so we wipe the deletion table
    # NOTE: this might end up being a problem, to be safe we might just completely wipe the cache every mod we load
    UNLOAD_SESSION_CACHE()
    lua.execute("required_in_session = {}")

    # We want to include core in all further mods, so we set this as the "base"
    base_path = lua.globals().package.path

    # Time to pray
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
                    print("mod:", mod_name)

                #lua.execute(mod["data"]["data.lua"])
                load_stage(lua, mod, stage)

                # Reset the included modules so lua reloads files with same name
                #UNLOAD_SESSION_CACHE()
                UNLOAD_ENTIRE_CACHE()

                if verbose:
                    print("The following modules were unloaded: ")
                    for entry in lua.globals()["required_in_session"]:
                        print("\t", entry)

                # Reset the deletion table
                RESET_MOD_STATE()

    print("hella slick")

    data = lua.globals().data

    def convert_table_to_dict(table):
        out = dict(table)
        for key in out:
            if lupa.lua_type(out[key]) == "table":
                out[key] = convert_table_to_dict(out[key])

        return out

    groups = convert_table_to_dict(data.raw["item-group"])
    subgroups = convert_table_to_dict(data.raw["item-subgroup"])

    def to_ordered_dict(elem):
        sorted_elem = {}
        for v in elem:
            sorted_elem[v["name"]] = v
        return sorted_elem

    # Sort the groups and subgroups dictionaries
    test_values = sorted(list(groups.values()), key = lambda x: x["order"])
    # sorted_groups = {}
    # for v in test_values:
    #     sorted_groups[v["name"]] = v
    sorted_groups = to_ordered_dict(test_values)

    test_values = sorted(list(subgroups.values()), key = lambda x: x["order"])
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
    add_items(data.raw["repair-tool"]) # not an item somehow
    add_items(data.raw["rail-planner"])

    # Sort everything
    for i, _ in enumerate(group_list):
        for j, _ in enumerate(group_list[i]["subgroups"]):
            group_list[i]["subgroups"][j]["items"] = to_ordered_dict(sorted(group_list[i]["subgroups"][j]["items"], key = lambda x: (x["order"], x["name"])))
        group_list[i]["subgroups"] = to_ordered_dict(sorted(group_list[i]["subgroups"], key = lambda x: (x["order"], x["name"])))
    group_list = sorted(group_list, key = lambda x: (x["order"], x["name"]))

    #print(json.dumps(group_list[0]["subgroups"], indent=2))

    #print(json.dumps(sorted_groups, indent=2))

    # Flatten into all_items dictionary
    sorted_items = {}
    for group in group_list:
        for subgroup_name in group["subgroups"]:
            subgroup = group["subgroups"][subgroup_name]
            for item_name in subgroup["items"]:
                item = subgroup["items"][item_name]
                sorted_items[item["name"]] = item


    #print(json.dumps(sorted_subgroups["raw-resource"], indent=2))

    with open("draftsman/data/items.pkl", "wb") as out:
        items = [sorted_items, sorted_subgroups, sorted_groups]
        pickle.dump(items, out, pickle.HIGHEST_PROTOCOL)


    # Entities
    entities = {}
    entities["data"] = {}

    def categorize_entities(entity_table, target_list):
        entity_dict = convert_table_to_dict(entity_table)
        for entity_name, entity in entity_dict.items():
            # extract flags
            # if entity_name == "big-ship-wreck-1":
            #     print("\t", entity_name)
            #     #print(json.dumps(entity, skipkeys=True, indent=2))
            #     print(entity.keys())
            flags = {}
            for _, flag in entity["flags"].items():
                #print(flag)
                flags[flag] = True
            if "not-blueprintable" in flags or "not-deconstructable" in flags: # or "hidden" in flags
                continue
            if "order" not in entity:
                try: 
                    entity["order"] = sorted_items[entity_name]["order"]
                except KeyError:
                    entity["order"] = "zzzzzzzzzzzzzzzzzzzzzzz"
                #continue
            entities["data"][entity_name] = entity # TODO sort
            target_list.append({"name": entity_name, "order": entity["order"]})

    def sort_and_flatten(target_list):
        sorted_list = sorted(target_list, key = lambda x: (x["order"], x["name"]))
        for i, x in enumerate(sorted_list):
            target_list[i] = x["name"]

    #  Chests
    #  TODO: narrow this category, includes a number of unplacable entities
    #  (crashed ship parts, factorio logos, etc.)
    entities["containers"] = []
    categorize_entities(data.raw["container"], entities["containers"])
    #entities["containers"] = sort_and_flatten(containers) # do this later
    #  Storage tanks
    entities["storage_tanks"] = []
    categorize_entities(data.raw["storage-tank"], entities["storage_tanks"])
    sort_and_flatten(entities["storage_tanks"])
    #  Belts
    entities["transport_belts"] = []
    categorize_entities(data.raw["transport-belt"], entities["transport_belts"])
    sort_and_flatten(entities["transport_belts"])
    entities["underground_belts"] = []
    categorize_entities(data.raw["underground-belt"], entities["underground_belts"])
    sort_and_flatten(entities["underground_belts"])
    entities["splitters"] = []
    categorize_entities(data.raw["splitter"], entities["splitters"])
    sort_and_flatten(entities["splitters"])
    #  Inserters
    entities["inserters"] = []
    entities["filter_inserters"] = []
    #categorize_entities(data.raw["inserter"], inserters)
    temp_inserters = convert_table_to_dict(data.raw["inserter"])
    for inserter_name, inserter in temp_inserters.items():
        entities["data"][inserter_name] = inserter
        if "order" not in inserter:
            inserter["order"] = sorted_items[inserter_name]["order"]
        inserter_order = inserter["order"]
        if "filter_count" in inserter:
            entities["filter_inserters"].append({"name": inserter_name, "order": inserter_order})
        else:
            entities["inserters"].append({"name": inserter_name, "order": inserter_order})
    sort_and_flatten(entities["inserters"])
    sort_and_flatten(entities["filter_inserters"])
    #  Loaders
    entities["loaders"] = []
    categorize_entities(data.raw["loader"], entities["loaders"])
    sort_and_flatten(entities["loaders"])
    #  Electric poles
    entities["electric_poles"] = []
    categorize_entities(data.raw["electric-pole"], entities["electric_poles"])
    sort_and_flatten(entities["electric_poles"])
    #  Pipes
    entities["pipes"] = []
    categorize_entities(data.raw["pipe"], entities["pipes"])
    sort_and_flatten(entities["pipes"])
    entities["underground_pipes"] = []
    categorize_entities(data.raw["pipe-to-ground"], entities["underground_pipes"])
    sort_and_flatten(entities["underground_pipes"])
    #  Pumps
    entities["pumps"] = []
    categorize_entities(data.raw["pump"], entities["pumps"])
    sort_and_flatten(entities["pumps"])
    #  Rails
    entities["straight_rails"] = []
    categorize_entities(data.raw["straight-rail"], entities["straight_rails"])
    sort_and_flatten(entities["straight_rails"])
    entities["curved_rails"] = []
    categorize_entities(data.raw["curved-rail"], entities["curved_rails"])
    sort_and_flatten(entities["curved_rails"])
    #  Train stops
    entities["train_stops"] = []
    categorize_entities(data.raw["train-stop"], entities["train_stops"])
    sort_and_flatten(entities["train_stops"])
    #  Rail signals
    entities["rail_signals"] = []
    categorize_entities(data.raw["rail-signal"], entities["rail_signals"])
    sort_and_flatten(entities["rail_signals"])
    entities["rail_chain_signals"] = []
    categorize_entities(data.raw["rail-chain-signal"], entities["rail_chain_signals"])
    sort_and_flatten(entities["rail_chain_signals"])
    #  Train cars
    entities["locomotives"] = []
    categorize_entities(data.raw["locomotive"], entities["locomotives"])
    sort_and_flatten(entities["locomotives"])
    entities["cargo_wagons"] = []
    categorize_entities(data.raw["cargo-wagon"], entities["cargo_wagons"])
    sort_and_flatten(entities["cargo_wagons"])
    entities["fluid_wagons"] = []
    categorize_entities(data.raw["fluid-wagon"], entities["fluid_wagons"])
    sort_and_flatten(entities["fluid_wagons"])
    entities["artillery_wagons"] = []
    categorize_entities(data.raw["artillery-wagon"], entities["artillery_wagons"])
    sort_and_flatten(entities["artillery_wagons"])
    #  Logistics containers (Special)
    #logistic_active_provider_containers = [] # TODO
    #logisitc_passive_provider_containers = [] # TODO
    logistic_storage_containers = []
    logistic_buffer_containers = []
    logistic_request_containers = []
    logi_containers = convert_table_to_dict(data.raw["logistic-container"])
    for container_name, container in logi_containers.items():
        entities["data"][container_name] = container
        container_type = container["logistic_mode"]
        if "order" not in container:
            container["order"] = sorted_items[container_name]["order"]
        container_order = container["order"]
        if container_type == "passive-provider":
            entities["containers"].append({"name": container_name, "order": container_order})
        elif container_type == "active-provider":
            entities["containers"].append({"name": container_name, "order": container_order})
        elif container_type == "storage":
            logistic_storage_containers.append({"name": container_name, "order": container_order})
        elif container_type == "buffer":
            logistic_buffer_containers.append({"name": container_name, "order": container_order})
        elif container_type == "requester":
            logistic_request_containers.append({"name": container_name, "order": container_order})
    sort_and_flatten(entities["containers"])
    sort_and_flatten(logistic_storage_containers)
    entities["logistic_storage_containers"] = logistic_storage_containers
    sort_and_flatten(logistic_buffer_containers)
    entities["logistic_buffer_containers"] = logistic_buffer_containers
    sort_and_flatten(logistic_request_containers)
    entities["logistic_request_containers"] = logistic_request_containers
    #  Roboports
    entities["roboports"] = []
    categorize_entities(data.raw["roboport"], entities["roboports"])
    sort_and_flatten(entities["roboports"])
    #  Lamps
    entities["lamps"] = []
    categorize_entities(data.raw["lamp"], entities["lamps"])
    sort_and_flatten(entities["lamps"])
    #  Combinators
    entities["arithmetic_combinators"] = []
    categorize_entities(data.raw["arithmetic-combinator"], entities["arithmetic_combinators"])
    sort_and_flatten(entities["arithmetic_combinators"])
    entities["decider_combinators"] = []
    categorize_entities(data.raw["decider-combinator"], entities["decider_combinators"])
    sort_and_flatten(entities["decider_combinators"])
    entities["constant_combinators"] = []
    categorize_entities(data.raw["constant-combinator"], entities["constant_combinators"])
    sort_and_flatten(entities["constant_combinators"])
    entities["power_switches"] = []
    categorize_entities(data.raw["power-switch"], entities["power_switches"])
    sort_and_flatten(entities["power_switches"])
    entities["programmable_speakers"] = []
    categorize_entities(data.raw["programmable-speaker"], entities["programmable_speakers"])
    sort_and_flatten(entities["programmable_speakers"])
    #  Boilers / Heat exchangers
    entities["boilers"] = []
    categorize_entities(data.raw["boiler"], entities["boilers"])
    sort_and_flatten(entities["boilers"])
    #  Steam engines / turbines
    entities["generators"] = []
    categorize_entities(data.raw["generator"], entities["generators"])
    sort_and_flatten(entities["generators"])
    #  Solar panels
    entities["solar_panels"] = []
    categorize_entities(data.raw["solar-panel"], entities["solar_panels"])
    sort_and_flatten(entities["solar_panels"])
    #  Accumulators
    entities["accumulators"] = []
    categorize_entities(data.raw["accumulator"], entities["accumulators"])
    sort_and_flatten(entities["accumulators"])
    #  Reactors
    entities["reactors"] = []
    categorize_entities(data.raw["reactor"], entities["reactors"])
    sort_and_flatten(entities["reactors"])
    #  Heat pipes
    entities["heat_pipes"] = []
    categorize_entities(data.raw["heat-pipe"], entities["heat_pipes"])
    sort_and_flatten(entities["heat_pipes"])
    #  Mining drills (Burner, Electric, Pumpjack)
    entities["mining_drills"] = []
    categorize_entities(data.raw["mining-drill"], entities["mining_drills"])
    sort_and_flatten(entities["mining_drills"])
    #  Offshore pumps
    entities["offshore_pumps"] = []
    categorize_entities(data.raw["offshore-pump"], entities["offshore_pumps"])
    sort_and_flatten(entities["offshore_pumps"])
    #  Furnaces
    entities["furnaces"] = []
    categorize_entities(data.raw["furnace"], entities["furnaces"])
    sort_and_flatten(entities["furnaces"])
    #  Assembling machines (1-3 + chemical plant, refinery, and centrifuge)
    entities["assembling_machines"] = []
    categorize_entities(data.raw["assembling-machine"], entities["assembling_machines"])
    sort_and_flatten(entities["assembling_machines"])
    #  Labs
    entities["labs"] = []
    categorize_entities(data.raw["lab"], entities["labs"])
    sort_and_flatten(entities["labs"])
    #  Beacons
    entities["beacons"] = []
    categorize_entities(data.raw["beacon"], entities["beacons"])
    sort_and_flatten(entities["beacons"])
    #  Rocket silos
    entities["rocket_silos"] = []
    categorize_entities(data.raw["rocket-silo"], entities["rocket_silos"])
    sort_and_flatten(entities["rocket_silos"])
    #  Landmines
    entities["land_mines"] = []
    categorize_entities(data.raw["land-mine"], entities["land_mines"])
    sort_and_flatten(entities["land_mines"])
    #  Walls
    entities["walls"] = []
    categorize_entities(data.raw["wall"], entities["walls"])
    sort_and_flatten(entities["walls"])
    #  Gates
    entities["gates"] = []
    categorize_entities(data.raw["gate"], entities["gates"])
    sort_and_flatten(entities["gates"])
    #  Turrets
    entities["turrets"] = []
    categorize_entities(data.raw["ammo-turret"], entities["turrets"])
    categorize_entities(data.raw["electric-turret"], entities["turrets"])
    categorize_entities(data.raw["fluid-turret"], entities["turrets"])
    categorize_entities(data.raw["artillery-turret"], entities["turrets"])
    sort_and_flatten(entities["turrets"])
    #  Radars
    entities["radars"] = []
    categorize_entities(data.raw["radar"], entities["radars"])
    sort_and_flatten(entities["radars"])
    #  Electric Energy Interfaces
    entities["electric_energy_interfaces"] = []
    categorize_entities(data.raw["electric-energy-interface"], entities["electric_energy_interfaces"])
    sort_and_flatten(entities["electric_energy_interfaces"])
    #  Linked Containers
    entities["linked_containers"] = []
    categorize_entities(data.raw["linked-container"], entities["linked_containers"])
    sort_and_flatten(entities["linked_containers"])
    #  Heat interfaces
    entities["heat_interfaces"] = []
    categorize_entities(data.raw["heat-interface"], entities["heat_interfaces"])
    sort_and_flatten(entities["heat_interfaces"])
    #  Linked belts
    entities["linked_belts"] = []
    categorize_entities(data.raw["linked-belt"], entities["linked_belts"])
    sort_and_flatten(entities["linked_belts"])
    #  Infinity containers
    entities["infinity_containers"] = []
    categorize_entities(data.raw["infinity-container"], entities["infinity_containers"])
    sort_and_flatten(entities["infinity_containers"])
    #  Infinity pipes
    entities["infinity_pipes"] = []
    categorize_entities(data.raw["infinity-pipe"], entities["infinity_pipes"])
    sort_and_flatten(entities["infinity_pipes"])
    #  Burner generators
    entities["burner_generators"] = []
    categorize_entities(data.raw["burner-generator"], entities["burner_generators"])
    sort_and_flatten(entities["burner_generators"])

    # TODO: sort entities["data"]?

    with open("draftsman/data/entities.pkl", "wb") as out:
        pickle.dump(entities, out, pickle.HIGHEST_PROTOCOL)

    # run the extractor
    lua.execute(file_to_string("draftsman/compatability/extract_data.lua"))


if __name__ == "__main__":
    update()