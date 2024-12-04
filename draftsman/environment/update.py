# update.py

# TODO: rewrite all of the extract functions to use `add_signal`, `add_item`, etc.
# This is hard because we want to keep everything sorted if possible, but that
# requires information on item groups when modifying things like entities, which
# is annoying.

from draftsman import __file__ as draftsman_root_file
from draftsman.classes.collision_set import CollisionSet
from draftsman.data.entities import add_entity
from draftsman.environment.mod_list import (
    Dependency,
    Mod,
    file_to_string,
    archive_to_string,
    discover_mods,
    display_mods,
)
from draftsman.environment.mod_settings import read_mod_settings
from draftsman.error import MissingModError, IncompatableModError, IncorrectModVersionError
from draftsman.utils import AABB, version_string_to_tuple, version_tuple_to_string

import git
import git.exc
import lupa.lua52 as lupa

from collections import OrderedDict
import json
import os
import pickle
from typing import Union


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


def specify_factorio_version(
    game_path: str, desired_version: str, verbose: bool = False
) -> None:
    """
    TODO
    Updates the `factorio-data` git repository to a specific version tag.

    Note that this does not actually update Draftsman's data; you have to call
    `update_draftsman_data()` for that.

    :param game_path: Filepath to the git repo to modify. Draftsman's copy lies
        within its ``site-packages`` installation.
    :param desired_version: A string corresponding to the version of the game
        data desired.
    :param verbose: Whether or not to print status messages to stdout for
        clarity/readability. When ``false``, this function behaves silently.
    """
    if verbose:
        print()

    # Grab and populate the repo, making sure its a git repo we expect
    repo = git.Repo(game_path)
    repo.git.fetch()
    assert (
        repo.remotes.origin.url == "https://github.com/wube/factorio-data"
    ), "Targeted repo is not `wube/factorio-data`"

    # Grab the currently checked out tag for this repo
    # https://stackoverflow.com/a/32524783/8167625
    current_tag = next(
        (tag for tag in repo.tags if tag.commit == repo.head.commit), None
    )

    if verbose:
        print("Current Factorio version: {}".format(current_tag.name))

    # The string "latest" should point to the most recent git tag
    if desired_version == "latest":
        desired_version = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)[
            -1
        ].name

    # Try to normalize the version string to "maj.min.rev" so the user can
    # specify a version like "1.0" or "2.0.1.13" without it exploding. If it
    # fails, the user did something wrong
    try:
        version_tuple = version_string_to_tuple(desired_version)[0:3]
        version_tuple = version_tuple + (0,) * (3 - len(version_tuple))
        desired_version = version_tuple_to_string(version_tuple)
    except ValueError:
        raise ValueError("Invalid semantic version string '{}'".format(desired_version))

    # Check to make sure that the specified version is an actual valid version
    if desired_version not in (tag.name for tag in repo.tags):
        raise ValueError("Unknown version '{}'".format(desired_version))

    # Checkout a different version of `factorio-data` if necessary
    if desired_version != current_tag.name:
        if verbose:
            print(
                "Different Factorio version requested:\n\t({}) -> ({})".format(
                    current_tag, desired_version
                )
            )

        repo.git.checkout(desired_version)

        if verbose:
            print("Changed to Factorio version {}\n".format(desired_version))
    else:
        if verbose:
            print(
                "Desired Factorio version ({}) already matches current.".format(
                    desired_version
                )
            )

def python_require(
    mod: Mod, mod_folder: str, module_name: str, package_path: str
) -> tuple[str | None, str]:
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
    if not mod.is_archive:
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

def run_mod_phase(
    lua: lupa.LuaRuntime, mod: Mod, stage: str
) -> None:
    """
    Runs one of the mod entry-points for either the settings or the data stage.
    (`settings.lua`, `data-updates.lua`, etc.)
    """
    # lua.globals().MOD = mod
    lua.globals().MOD_DIR = mod.location
    lua.globals().lua_push_mod(mod)
    lua.globals().CURRENT_FILE = mod.location + "/" + stage

    # Add the base mod folder as a base path (in addition to base and core)
    lua.globals().lua_add_path(mod.location + "/?.lua")

    lua.execute(mod.get_file(stage))


def run_settings_stage(lua: lupa.LuaRuntime, load_order: list[Mod], mods_path: str, draftsman_path: str, base_path: str, verbose: bool=False):
    stages = ("settings.lua", "settings-updates.lua", "settings-final-fixes.lua")
    for stage in stages:
        if verbose:
            print(stage.upper() + ":")

        for mod in load_order:

            # Reset the directory so we dont require from different mods
            # Well, unless we need to. Otherwise, avoid it
            # TODO: fixme
            lua.globals().lua_set_path(base_path)

            if stage in mod.stages:
                if verbose:
                    print("\tmod:", mod.name)

                run_mod_phase(lua, mod, stage)                

                # Reset the included modules
                lua.globals().lua_unload_cache()

    # Factorio then converts the settings which were stored in data.raw
    # to the global 'settings' table: We emulate that here in 'settings.lua':
    lua.execute(file_to_string(os.path.join(draftsman_path, "compatibility", "settings.lua")))

    # If there is a `mod-settings.dat` file present, we overwrite the current 
    # values with the user-specified ones:
    try:
        user_settings = read_mod_settings(mods_path)
        # If so, Overwrite the 'value' key for all the settings present
        for setting_type, setting_dict in user_settings.items():
            lua_settings = lua.globals().settings[setting_type]
            for name in setting_dict:
                if lua_settings[name] is not None:
                    lua_settings[name].value = setting_dict[name]["value"]
    except FileNotFoundError:
        pass


def run_data_stage(lua: lupa.LuaRuntime, load_order: list[Mod], base_path: str, verbose: bool=False):
    """
    TODO
    """
    stages = ("data.lua", "data-updates.lua", "data-final-fixes.lua")
    for stage in stages:
        if verbose:
            print(stage.upper() + ":")

        for mod in load_order:
            # Reset the directory so we dont require from different mods
            # Well, unless we need to. Otherwise, avoid it
            # TODO: fixme
            lua.globals().lua_set_path(base_path)

            if stage in mod.stages:
                if verbose:
                    print("\tmod:", mod.name)

                run_mod_phase(lua, mod, stage)

                # Reset the included modules
                # TODO: probably better to just have this be a snippet of code
                # so we don't pollute the global namespace
                lua.globals().lua_unload_cache()

                # Reset the MODS tree to an empty state
                lua.globals().lua_wipe_mods()


def run_data_lifecycle(
    draftsman_path: str,
    game_path: str,
    mods_path: str,
    show_logs: bool = False,
    no_mods: bool = False,
    verbose: bool = False,
) -> lupa.LuaRuntime:
    """
    Runs the entire Factorio data lifecycle, from discovering mods, determining
    the dependency tree, to executing both the settings and data stages. Returns
    a Lua instance which contains all of the relevant data to that particular
    load cycle.

    :returns: A :py:class:`lupa.LuaRuntime` object containing all relevant Lua
        tables with corresponding data, such as `data.raw`, `mods`, etc. that
        can be parsed.
    """

    if verbose:
        print("Discovering mods...\n")

    mods = discover_mods(game_path=game_path, mods_path=mods_path, no_mods=no_mods)

    if verbose:
        display_mods(mods, verbose=False)  # We want the slick version
        print()

    # Create the dependency tree
    if verbose:
        print("Determining dependency tree...\n")

    # Currently, `mods` contains all versions of each mod detected under each
    # mod name. Once we get to the actual load process however, we only want the
    # active mods, and only one version of each mod if there are multiple.
    # Here we select only the enabled mods and collapse the list of different 
    # mod versions to just the first mod in the list, since that Mod should be
    # the one that Factorio should select:
    mods = {name: mod_list[0] for name, mod_list in mods.items() if mod_list[0].enabled}

    for mod_name, mod in mods.items():
        # Core has no dependecies, so determining it's tree is redundant
        if mod_name == "core":
            continue
        # Base depends on core, though the game does not tell us this
        elif mod_name == "base":
            mod.dependencies = [
                Dependency(flag=None, name="core", operation=None, version=None)
            ]

        if verbose:
            print(mod_name)

        for i, dependency in enumerate(mod.dependencies):
            # remove whitespace for consistency
            # dependency = "".join(dependency.split())
            # m = Mod.dependency_regex.match(dependency)
            # flag, dep_name, op, version = m[1], m[2], m[3], m[4]

            if verbose:
                print("\t", dependency)

            if dependency.flag == "!":
                # Mod is incompatible with the current mod
                # Check if that mod exists in the mods folder
                if dependency.name in mods:
                    # If it does, throw an error
                    raise IncompatableModError(mod_name)
                else:
                    continue  # Otherwise, don't worry about it
            elif dependency.flag == "?" or dependency.flag == "(?)":
                # Mod is optional to the current mod
                if dependency.name not in mods:
                    continue  # Don't worry about it

            # Now that we know this is a regular dependency, we ensure that it
            # exists
            if dependency.name not in mods:
                raise MissingModError(dependency.name)

            # Ensure the mod's version is correct
            if dependency.version is not None:
                assert dependency.operation in ["==", ">=", "<=", ">", "<"], "incorrect operation"
                actual_version = version_string_to_tuple(mods[dependency.name].version)
                target_version = version_string_to_tuple(dependency.version)
                expr = str(actual_version) + dependency.operation + str(target_version)
                if not eval(expr):
                    raise IncorrectModVersionError(
                        "mod '{}' version {} not {} {}".format(
                            mod_name, 
                            actual_version, 
                            dependency.operation, 
                            target_version
                        )
                    )

            if dependency.flag == "~":
                # The mod is needed and considered a dependency, but we don't
                # want it to modify the load order, so we skip that part
                continue

            # Replace the Dependency object with a reference to the actual
            # loaded and selected Mod
            # TODO: would be better to not do this since it's technically destructive
            mod.dependencies[i] = mods[dependency.name]

    # Get load order (Sort the mods by the least to most deep dependency tree
    # first and their name second)
    load_order: list[Mod] = [
        mod for mod in sorted(mods.values(), key=lambda x: (x.get_depth(), x.name))
    ]

    if verbose:
        print("\nLoad order:")
        print([mod.name for mod in load_order], end="\n\n")

    # Create lua runtime
    lua = lupa.LuaRuntime(unpack_returned_tuples=True)

    # First we load `defines.lua` in this context, which is a set of constant
    # values used by the game. We do this first because these can be used at any
    # point in any of the subsequent steps.
    # This is not included in `factorio-data` and has to be manually extracted
    # (See compatibility/defines.lua for more info).
    lua.execute(
        file_to_string(os.path.join(draftsman_path, "compatibility", "defines.lua"))
    )

    # "interface.lua" houses a number of patching functions used to emulate
    # Factorio's internal load process.
    # Primarily, it updates the require function to now handle python_require,
    # and fixes a few small discrepancies that Factorio's environment has.
    lua.execute(
        file_to_string(os.path.join(draftsman_path, "compatibility", "interface.lua"))
    )

    # For ease of access, we setup some aliases and variables between the two
    # contexts:

    # Register logging status within Lua context
    lua.globals().LOG_ENABLED = show_logs

    # Record where to look for mod folders
    lua.globals().MOD_FOLDER_LOCATION = mods_path

    # Set this once at the beginning
    lua.globals().MOD_LIST = mods

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
        file_to_string(os.path.join(game_path, "core", "lualib", "util.lua"))
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

    # Factorio `data:extend` function
    lua.execute(
        file_to_string(
            os.path.join(game_path, "core", "lualib", "dataloader.lua")
        )
    )

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
    root_path = os.path.join(draftsman_path, "?.lua")
    lua_add_path(root_path)

    # Add the path to and setup the `core` module
    # This should probably be part of the main load process in case more than
    # "data.lua" is added to the core module, but core is kinda special and
    # would have to be integrated into the load order as a unique case anyway
    lualib_path = os.path.join(game_path, "core", "lualib", "?.lua")
    lua_add_path(lualib_path)
    # load_stage(lua, mods, core_mod, "data.lua")

    # We also add a special path, which is just the entire module
    # (This is used for absolute paths in archives, so we add it once here)
    lua_add_path("?.lua")

    # We want to include core in all further mods, so we set this as the "base"
    # path to return to every time a new mod is initialized
    base_path = lua.globals().package.path

    # Load the settings stage
    run_settings_stage(
        lua=lua, 
        load_order=load_order, 
        mods_path=mods_path, 
        draftsman_path=draftsman_path, 
        base_path=base_path, 
        verbose=verbose
    )

    # Load the data stage
    run_data_stage(lua, load_order=load_order, base_path=base_path, verbose=verbose)

    return lua


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


def extract_mods(lua: lupa.LuaRuntime, draftsman_path: str, verbose: bool=False) -> None:
    """
    Extract all the mod versions to ``mods.pkl`` in :py:mod:`draftsman.data`.
    """
    # out_mods = {}
    # for mod in mods:
    #     if mod.name == "core":
    #         continue
    #     out_mods[mod] = version_string_to_tuple(mod.version)

    # print(out_mods)
    out_mods = {key: value for key, value in convert_table_to_dict(lua.globals().mods).items() if key != "core"}

    with open(os.path.join(draftsman_path, "data", "mods.pkl"), "wb") as out:
        pickle.dump(out_mods, out, 4)

    if verbose:
        print("Extracted mods...")

def extract_entities(lua: lupa.LuaRuntime, draftsman_path: str, sort_tuple, verbose: bool=False) -> None:
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
        if ("not-blueprintable" in flags):  # or "hidden" in flags
            return False

        collision_mask = entity.get("collision_mask", None)
        if not collision_mask:
            entity["collision_mask"] = get_default_collision_mask(entity["type"])
        else:
            entity["collision_mask"] = set(collision_mask)

        # Check if an entity is flippable or not
        is_flippable[entity_name] = is_entity_flippable(entity)

        # maybe move this to get_order?
        # unordered_entities_raw[entity_name] = entity
        return True

    def sort(target_list): # TODO: FIXME
        # sorted_list = get_order(target_list, *sort_tuple)
        # for i, x in enumerate(sorted_list):
        #     target_list[i] = x
        pass

    # unordered_entities_raw = {}
    entities["of_type"] = {}

    def add_entities(prototype_name: str):
        if prototype_name not in data.raw:
            # TODO: handle the case where it's not available, ideally just
            # passing an empty list
            entities["of_type"][prototype_name] = []
            return
        for name, contents in convert_table_to_dict(data.raw[prototype_name]).items():
            if not categorize_entity(name, contents):
                continue
            add_entity(**contents, target=(unordered_entities_raw, entities["of_type"]))

        sort(entities["of_type"][prototype_name])

    add_entities("accumulator")
    add_entities("agricultural-tower") # Space Age
    add_entities("ammo-turret")
    add_entities("arithmetic-combinator")
    add_entities("artillery-turret")
    add_entities("artillery-wagon")
    add_entities("assembling-machine")
    add_entities("asteroid-collector") # Space Age
    add_entities("beacon")
    add_entities("boiler")
    add_entities("burner-generator")
    add_entities("car") # Blueprintable in 2.0
    add_entities("cargo-bay") # Space Age
    add_entities("cargo-landing-pad") # Space Age
    add_entities("cargo-wagon")
    add_entities("constant-combinator")
    add_entities("container")
    add_entities("curved-rail-a")
    add_entities("curved-rail-b")
    add_entities("decider-combinator")
    add_entities("display-panel") # Space Age (?)
    add_entities("electric-energy-interface")
    add_entities("electric-pole")
    add_entities("electric-turret")
    add_entities("elevated-curved-rail-a") # Elevated rails
    add_entities("elevated-curved-rail-b") # Elevated rails
    add_entities("elevated-half-diagonal-rail") # Elevated rails
    add_entities("elevated-straight-rail") # Elevated rails
    add_entities("fluid-turret")
    add_entities("fluid-wagon")
    add_entities("furnace")
    add_entities("fusion-generator") # Space Age
    add_entities("fusion-reactor") # Space Age
    add_entities("gate")
    add_entities("generator")
    add_entities("half-diagonal-rail")
    add_entities("heat-interface")
    add_entities("heat-pipe")
    add_entities("infinity-container")
    add_entities("infinity-pipe")
    add_entities("inserter")
    add_entities("lab")
    add_entities("lamp")
    add_entities("land-mine")
    add_entities("legacy-straight-rail")
    add_entities("legacy-curved-rail")
    add_entities("lightning-attractor") # Space Age
    add_entities("linked-belt")
    add_entities("linked-container")
    add_entities("loader")
    add_entities("loader-1x1")
    add_entities("locomotive")
    add_entities("logistic-container")
    add_entities("market")
    add_entities("mining-drill")
    add_entities("offshore-pump")
    add_entities("pipe")
    add_entities("pipe-to-ground")
    add_entities("player-port") # Deprecated in 2.0
    add_entities("power-switch")
    add_entities("programmable-speaker")
    add_entities("pump")
    add_entities("radar")
    add_entities("rail-chain-signal")
    add_entities("rail-ramp")
    add_entities("rail-signal")
    add_entities("rail-support")
    add_entities("reactor")
    add_entities("roboport")
    add_entities("rocket-silo")
    add_entities("selector-combinator")
    add_entities("simple-entity-with-force")
    add_entities("simple-entity-with-owner")
    add_entities("solar-panel")
    add_entities("space-platform-hub")
    add_entities("spider-vehicle") # Blueprintable in 2.0
    add_entities("splitter")
    add_entities("storage-tank")
    add_entities("straight-rail")
    add_entities("thruster") # Space Age
    add_entities("train-stop")
    add_entities("transport-belt")
    add_entities("turret") # turrets that require no ammo whatsoever
    add_entities("underground-belt")
    add_entities("wall")

    entities["flippable"] = is_flippable
    entities["collision_sets"] = collision_sets

    # In order to fully sort an arbitrary entity, we need to:
    # Sort by item group has order string
    # Sort by the `order` string of the item group it belongs to
    # Sort by the lexographic string of the item group
    # Sort by subgroup has order string
    # Sort by the `order` string of the item subgroup
    # Sort by the lexographic string of the item subgroup
    # Sort by item has order string
    # Sort by item `order` string
    # Sort by item lexographic order
    # Sort by entity `order` (?)
    # Sort by entity lexographic order (?)

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

    with open(os.path.join(draftsman_path, "data", "entities.pkl"), "wb") as out:
        pickle.dump(entities, out, 4)

    if verbose:
        print("Extracted entities...")


# =============================================================================


def extract_fluids(lua: lupa.LuaRuntime, draftsman_path: str, sort_tuple, verbose: bool=False):
    """
    Extracts the fluids to ``fluids.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    unordered_fluids_raw = convert_table_to_dict(data.raw["fluid"])
    raw_order = get_order(unordered_fluids_raw, *sort_tuple)

    fluids_raw = OrderedDict()
    for name in raw_order:
        fluids_raw[name] = unordered_fluids_raw[name]

    with open(os.path.join(draftsman_path, "data", "fluids.pkl"), "wb") as out:
        pickle.dump((fluids_raw,), out, 4)

    if verbose:
        print("Extracted fluids...")


# =============================================================================


def extract_instruments(lua: lupa.LuaRuntime, draftsman_path: str, verbose: bool=False):
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

    with open(os.path.join(draftsman_path, "data", "instruments.pkl"), "wb") as out:
        instrument_data = [instrument_raw, instrument_index, instrument_names]
        pickle.dump(instrument_data, out, 4)

    if verbose:
        print("Extracted instruments...")


# =============================================================================


def extract_items(lua: lupa.LuaRuntime, draftsman_path: str, sort_tuple, verbose):
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

    with open(os.path.join(draftsman_path, "data", "items.pkl"), "wb") as out:
        items = [sorted_items, sorted_subgroups, sorted_groups, fuels]
        pickle.dump(items, out, 4)

    if verbose:
        print("Extracted items...")


# =============================================================================


def extract_modules(lua: lupa.LuaRuntime, draftsman_path: str, sort_tuple, verbose: bool=False):
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

    with open(os.path.join(draftsman_path, "data", "modules.pkl"), "wb") as out:
        pickle.dump([modules_raw, out_categories], out, 4)

    if verbose:
        print("Extracted modules...")


# =============================================================================


def extract_recipes(lua: lupa.LuaRuntime, draftsman_path: str, sort_tuple, verbose: bool=False):
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

    with open(os.path.join(draftsman_path, "data", "recipes.pkl"), "wb") as out:
        data = [recipes, out_categories, for_machine]
        pickle.dump(data, out, 4)

    if verbose:
        print("Extracted recipes...")


# =============================================================================


def extract_signals(lua: lupa.LuaRuntime, draftsman_path: str, sort_tuple, verbose: bool=False):
    """
    Extracts the signals to ``signals.pkl`` in :py:mod:`draftsman.data`.
    """
    data = lua.globals().data

    unsorted_raw_signals = {}
    type_of_signals: dict[str, set[str]] = {}

    virtual_signals = []
    item_signals = []
    fluid_signals = []
    recipe_signals = []
    entity_signals = []
    space_location_signals = []
    asteroid_chunk_signals = []
    quality_signals = []

    # hidden_signals = []

    def add_signals(signal_category_name, target_location, signal_type):
        signal_category = convert_table_to_dict(data.raw[signal_category_name])
        for signal_name in signal_category:
            signal_obj = signal_category[signal_name]

            # if signal_name == "tank-flamethrower":
            #     print("found: ", signal_category_name)
            #     print(signal_category[signal_name])

            # if "hidden" in signal_obj:
            #     continue

            unsorted_raw_signals[signal_name] = signal_obj

            # if "flags" in signal_obj and "hidden" in signal_obj["flags"]:
            #     hidden_signals.append(signal_category[signal_name])
            #     continue

            if signal_name not in type_of_signals:
                type_of_signals[signal_name] = {signal_type}
            else:
                type_of_signals[signal_name].add(signal_type)
            
            target_location.append(signal_category[signal_name])

    # Virtual Signals
    add_signals("virtual-signal", virtual_signals, "virtual")

    # Item Signals
    add_signals("item", item_signals, "item")
    add_signals("item-with-entity-data", item_signals, "item")
    add_signals("tool", item_signals, "item")
    add_signals("ammo", item_signals, "item")
    add_signals("module", item_signals, "item")
    add_signals("armor", item_signals, "item")
    add_signals("gun", item_signals, "item")
    add_signals("capsule", item_signals, "item")
    add_signals("selection-tool", item_signals, "item")
    add_signals("copy-paste-tool", item_signals, "item")
    add_signals("blueprint", item_signals, "item")
    add_signals("blueprint-book", item_signals, "item")
    add_signals("upgrade-item", item_signals, "item")
    add_signals("deconstruction-item", item_signals, "item")
    add_signals("spidertron-remote", item_signals, "item")
    add_signals("repair-tool", item_signals, "item")  # not an item somehow
    add_signals("rail-planner", item_signals, "item")
    add_signals("space-platform-starter-pack", item_signals, "item")

    # Fluid Signals
    add_signals("fluid", fluid_signals, "fluid")

    # Recipe Signals
    add_signals("recipe", recipe_signals, "recipe")

    # Entity Signals
    add_signals("accumulator", entity_signals, "entity")
    add_signals("agricultural-tower", entity_signals, "entity")
    add_signals("ammo-turret", entity_signals, "entity")
    add_signals("arithmetic-combinator", entity_signals, "entity")
    add_signals("arrow", entity_signals, "entity")
    add_signals("artillery-flare", entity_signals, "entity")
    add_signals("artillery-projectile", entity_signals, "entity")
    add_signals("artillery-turret", entity_signals, "entity")
    add_signals("artillery-wagon", entity_signals, "entity")
    add_signals("assembling-machine", entity_signals, "entity")
    add_signals("asteroid", entity_signals, "entity")
    # add_signals("asteroid-chunk", entity_signals, "entity")
    add_signals("asteroid-collector", entity_signals, "entity")
    add_signals("beacon", entity_signals, "entity")
    add_signals("beam", entity_signals, "entity")
    add_signals("boiler", entity_signals, "entity")
    add_signals("burner-generator", entity_signals, "entity")
    add_signals("capture-robot", entity_signals, "entity")
    add_signals("car", entity_signals, "entity")
    add_signals("cargo-bay", entity_signals, "entity")
    add_signals("cargo-landing-pad", entity_signals, "entity")
    add_signals("cargo-pod", entity_signals, "entity")
    add_signals("cargo-wagon", entity_signals, "entity")
    add_signals("character", entity_signals, "entity")
    add_signals("character-corpse", entity_signals, "entity")
    add_signals("cliff", entity_signals, "entity")
    add_signals("combat-robot", entity_signals, "entity")
    add_signals("constant-combinator", entity_signals, "entity")
    add_signals("construction-robot", entity_signals, "entity")
    add_signals("container", entity_signals, "entity")
    add_signals("corpse", entity_signals, "entity")
    add_signals("curved-rail-a", entity_signals, "entity")
    add_signals("curved-rail-b", entity_signals, "entity")
    add_signals("decider-combinator", entity_signals, "entity")
    add_signals("deconstructible-tile-proxy", entity_signals, "entity")
    add_signals("display-panel", entity_signals, "entity") # Space Age (?)
    add_signals("electric-energy-interface", entity_signals, "entity")
    add_signals("electric-pole", entity_signals, "entity")
    add_signals("electric-turret", entity_signals, "entity")
    add_signals("elevated-curved-rail-a", entity_signals, "entity") # Elevated rails
    add_signals("elevated-curved-rail-b", entity_signals, "entity") # Elevated rails
    add_signals("elevated-half-diagonal-rail", entity_signals, "entity") # Elevated rails
    add_signals("elevated-straight-rail", entity_signals, "entity") # Elevated rails
    add_signals("entity-ghost", entity_signals, "entity")
    add_signals("explosion", entity_signals, "entity")
    add_signals("fluid-turret", entity_signals, "entity")
    add_signals("fluid-wagon", entity_signals, "entity")
    add_signals("fire", entity_signals, "entity")
    add_signals("fish", entity_signals, "entity")
    add_signals("furnace", entity_signals, "entity")
    add_signals("fusion-generator", entity_signals, "entity") # Space Age
    add_signals("fusion-reactor", entity_signals, "entity") # Space Age
    add_signals("gate", entity_signals, "entity")
    add_signals("generator", entity_signals, "entity")
    add_signals("half-diagonal-rail", entity_signals, "entity")
    add_signals("heat-interface", entity_signals, "entity")
    add_signals("heat-pipe", entity_signals, "entity")
    add_signals("highlight-box", entity_signals, "entity")
    add_signals("infinity-container", entity_signals, "entity")
    add_signals("infinity-pipe", entity_signals, "entity")
    add_signals("inserter", entity_signals, "entity")
    add_signals("item-entity", entity_signals, "entity")
    add_signals("item-request-proxy", entity_signals, "entity")
    add_signals("lab", entity_signals, "entity")
    add_signals("lamp", entity_signals, "entity")
    add_signals("land-mine", entity_signals, "entity")
    add_signals("lane-splitter", entity_signals, "entity")
    add_signals("legacy-straight-rail", entity_signals, "entity")
    add_signals("legacy-curved-rail", entity_signals, "entity")
    add_signals("lightning", entity_signals, "entity")
    add_signals("lightning-attractor", entity_signals, "entity")
    add_signals("linked-belt", entity_signals, "entity")
    add_signals("linked-container", entity_signals, "entity")
    add_signals("loader-1x1", entity_signals, "entity")
    add_signals("loader", entity_signals, "entity")
    add_signals("locomotive", entity_signals, "entity")
    add_signals("logistic-container", entity_signals, "entity")
    add_signals("logistic-robot", entity_signals, "entity")
    add_signals("market", entity_signals, "entity")
    add_signals("mining-drill", entity_signals, "entity")
    add_signals("offshore-pump", entity_signals, "entity")
    add_signals("particle-source", entity_signals, "entity")
    add_signals("pipe", entity_signals, "entity")
    add_signals("pipe-to-ground", entity_signals, "entity")
    add_signals("plant", entity_signals, "entity")
    # add_signals("player-port", entity_signals, "entity") # Deprecated in 2.0
    add_signals("power-switch", entity_signals, "entity")
    add_signals("programmable-speaker", entity_signals, "entity")
    add_signals("projectile", entity_signals, "entity")
    add_signals("pump", entity_signals, "entity")
    add_signals("radar", entity_signals, "entity")
    add_signals("rail-chain-signal", entity_signals, "entity")
    add_signals("rail-ramp", entity_signals, "entity")
    add_signals("rail-remnants", entity_signals, "entity")
    add_signals("rail-signal", entity_signals, "entity")
    add_signals("rail-support", entity_signals, "entity")
    add_signals("reactor", entity_signals, "entity")
    add_signals("resource", entity_signals, "entity")
    add_signals("roboport", entity_signals, "entity")
    add_signals("rocket-silo", entity_signals, "entity")
    add_signals("rocket-silo-rocket", entity_signals, "entity")
    add_signals("rocket-silo-rocket-shadow", entity_signals, "entity")
    add_signals("segment", entity_signals, "entity")
    add_signals("segmented-unit", entity_signals, "entity")
    add_signals("selector-combinator", entity_signals, "entity")
    add_signals("simple-entity", entity_signals, "entity")
    add_signals("simple-entity-with-force", entity_signals, "entity")
    add_signals("simple-entity-with-owner", entity_signals, "entity")
    add_signals("smoke-with-trigger", entity_signals, "entity")
    add_signals("solar-panel", entity_signals, "entity")
    add_signals("space-platform-hub", entity_signals, "entity")
    add_signals("speech-bubble", entity_signals, "entity")
    add_signals("spider-leg", entity_signals, "entity")
    add_signals("spider-vehicle", entity_signals, "entity")
    add_signals("spider-unit", entity_signals, "entity")
    add_signals("splitter", entity_signals, "entity")
    add_signals("sticker", entity_signals, "entity")
    add_signals("storage-tank", entity_signals, "entity")
    add_signals("straight-rail", entity_signals, "entity")
    add_signals("stream", entity_signals, "entity")
    add_signals("temporary-container", entity_signals, "entity")
    add_signals("thruster", entity_signals, "entity") # Space Age
    add_signals("tile-ghost", entity_signals, "entity")
    add_signals("train-stop", entity_signals, "entity")
    add_signals("transport-belt", entity_signals, "entity")
    add_signals("tree", entity_signals, "entity")
    add_signals("turret", entity_signals, "entity") # turrets that require no ammo whatsoever
    add_signals("underground-belt", entity_signals, "entity")
    add_signals("unit", entity_signals, "entity")
    add_signals("unit-spawner", entity_signals, "entity")
    add_signals("wall", entity_signals, "entity")
    
    # Space Location Signals
    add_signals("planet", space_location_signals, "space-location")
    add_signals("space-location", space_location_signals, "space-location")

    # Asteroid Chunks Signals
    #add_signals("asteroid-chunk", asteroid_chunk_signals, "asteroid-chunk")

    # Quality Signals
    add_signals("quality", quality_signals, "quality")

    all_signals = virtual_signals + item_signals + fluid_signals + recipe_signals + entity_signals + space_location_signals + asteroid_chunk_signals + quality_signals
    all_signals_order = get_order(all_signals, *sort_tuple)

    virtual_signals = get_order(virtual_signals, *sort_tuple)
    item_signals = get_order(item_signals, *sort_tuple)
    fluid_signals = get_order(fluid_signals, *sort_tuple)
    recipe_signals = get_order(recipe_signals, *sort_tuple)
    entity_signals = get_order(entity_signals, *sort_tuple)
    space_location_signals = get_order(space_location_signals, *sort_tuple)
    asteroid_chunk_signals = get_order(asteroid_chunk_signals, *sort_tuple)
    quality_signals = get_order(quality_signals, *sort_tuple)

    raw_signals = OrderedDict()
    for signal in all_signals_order:
        raw_signals[signal] = unsorted_raw_signals[signal]

    with open(os.path.join(draftsman_path, "data", "signals.pkl"), "wb") as out:
        data = {
            "raw": raw_signals,
            "type_of": type_of_signals,

            "virtual": virtual_signals,
            "item": item_signals,
            "fluid": fluid_signals,
            "recipe": recipe_signals,
            "entity": entity_signals,
            "space-location": space_location_signals,
            "asteroid-chunk": asteroid_chunk_signals,
            "quality": quality_signals,
            # "hidden": hidden_signals
        }
        pickle.dump(data, out, 4)

    if verbose:
        print("Extracted signals...")


# =============================================================================


def extract_tiles(lua: lupa.LuaRuntime, draftsman_path: str, verbose: bool=False):
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

    with open(os.path.join(draftsman_path, "data", "tiles.pkl"), "wb") as out:
        pickle.dump(out_tiles, out, 4)

    if verbose:
        print("Extracted tiles...")


def extract_data(lua: lupa.LuaRuntime, draftsman_path: str, verbose: bool=False):
    # TODO: this needs to be customizable; how do we do this?
    # Ideally we would have some user-friendly pattern syntax that users could
    # specify...
    # Or maybe we could just run a filter on `data.raw` so that a user only gets
    # what they want, and then it's up to them to take the game object and
    # translate it into their desired form
    # That seems to make the most sense, and is essentially what we're already
    # doing on the Draftsman side.

    # Preferrably as well I would like to reuse the `entity.add_entity`, etc.
    # functions to keep everything consistent for both my end and the end user's
    # end
    if verbose:
        print("Extracting data...\n")

    extract_mods(lua=lua, draftsman_path=draftsman_path, verbose=verbose)

    # Lots of items are sorted by item order, subgroup and group
    # Here we get these things once and pass them into each extraction function
    # as necessary
    items = get_items(lua)

    extract_entities(lua, draftsman_path, items, verbose)
    extract_fluids(lua, draftsman_path, items, verbose)
    extract_instruments(lua, draftsman_path, verbose)
    extract_items(lua, draftsman_path, items, verbose)
    extract_modules(lua, draftsman_path, items, verbose)
    extract_recipes(lua, draftsman_path, items, verbose)
    extract_signals(lua, draftsman_path, items, verbose)
    extract_tiles(lua, draftsman_path, verbose)


def update_draftsman_data(
    game_path: str,
    mods_path: str,
    no_mods: bool = False,
    verbose: bool = False,
    show_logs: bool = False,
) -> None:
    """
    Runs the Factorio data lifecycle, and then extracts all of the relevant data
    that Draftsman needs to operate. The extracted data is written to a set of
    pickle files located in the ``draftsman/data`` folder, wherever it is
    installed.

    If you want to just run the data lifecycle part so that you can extract the
    game's data in whatever manner you wish, then instead use
    :py:meth:`.run_data_lifecycle`.

    :param game_path: The path pointing to Factorio's data, where "official" 
        mods like `base` and `core` live.
    :param mods_path: The path pointing to the user mods folder. Also the
        location where ``mod-settings.dat`` and ``mod-list.json`` files are 
        searched for and parsed from.
    :param no_mods: Whether or not to actually use any of the mods at ``mods_path``.
        Does not omit any "official" mods found at ``game_path``. Useful to 
        quickly toggle modded/unmodded configurations without having to 
        respecify any paths.
    :param verbose: Pretty-prints additional status messages and information to
        stdout.
    :param show_logs: If enabled, any `log()` messages created on the Lua side
        of things will be printed to stdout. This will happen regardless of the 
        value of ``verbose``.
    """
    draftsman_path = os.path.dirname(os.path.abspath(draftsman_root_file))

    lua_instance = run_data_lifecycle(
        draftsman_path=draftsman_path,
        game_path=game_path,
        mods_path=mods_path,
        show_logs=show_logs,
        no_mods=no_mods,
        verbose=verbose,
    )

    # Get the version of Factorio specified by the game data, and write 
    # `_factorio_version.py` with the current factorio version
    with open(os.path.join(game_path, "base", "info.json")) as base_info_file:
        base_info = json.load(base_info_file)
        factorio_version = base_info["version"]
        # Normalize it to 4 numbers to make our versioning lives easier
        if factorio_version.count(".") == 2:
            factorio_version += ".0"
        factorio_version_info = version_string_to_tuple(factorio_version)
    
    with open(os.path.join(draftsman_path, "_factorio_version.py"), "w") as version_file:
        version_file.write("# _factorio_version.py\n\n")
        version_file.write('__factorio_version__ = "' + factorio_version + '"\n')
        version_file.write(
            "__factorio_version_info__ = {}\n".format(str(factorio_version_info))
        )

    data_raw = convert_table_to_dict(lua_instance.globals().data.raw)
    #print(data_raw.keys())

    # At this point, `data.raw` in `lua_instance` and should(!) be properly
    # initialized. Hence, we can now extract the data we wish:

    if verbose:
        print()
    extract_data(lua=lua_instance, draftsman_path=draftsman_path, verbose=verbose)

    if verbose:
        print("\nUpdate finished.")  # Phew.
        print("hella slick; nothing broke!")
