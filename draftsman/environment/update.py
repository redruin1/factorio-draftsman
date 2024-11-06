# update.py

from draftsman.environment.mod_list import discover_mods
from draftsman.utils import version_string_to_tuple, version_tuple_to_string

import git
import git.exc
import lupa.lua52 as lupa

import io
import json
import os
import re
import zipfile
    

def specify_factorio_version(game_path: str, desired_version: str, verbose: bool=False) -> None:
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
    assert repo.remotes.origin.url == "https://github.com/wube/factorio-data", "Targeted repo is not `wube/factorio-data`"

    # Grab the currently checked out tag for this repo
    # https://stackoverflow.com/a/32524783/8167625
    current_tag = next(
        (tag for tag in repo.tags if tag.commit == repo.head.commit), None
    )

    if verbose:
        print("Current Factorio version: {}".format(current_tag.name))

    # The string "latest" should point to the most recent git tag
    if desired_version == "latest":
        desired_version = sorted(
            repo.tags, key=lambda t: t.commit.committed_datetime
        )[-1].name
    
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
            print("Desired Factorio version ({}) already matches current.".format(desired_version))


def run_data_lifecycle(game_path: str, mods_path: str, verbose: bool=False):
    """
    Runs the Factorio data lifecycle.

    :returns: A :py:class:`lupa.LuaRuntime` object containing all relevant Lua
        tables with corresponding data, such as `data.raw`, `mods`, etc. that
        can be pulled from.
    """

    if verbose:
        print("Discovering mods...")

    mods = discover_mods(game_path=game_path, mods_path=mods_path)

    # Prune disabled mods
    # TODO

    # Handle duplicate mod versions

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

    # List mods that we will be operating with

    # Create lua runtime
    lua_instance = lupa.LuaRuntime()

    return lua_instance

def extract_data():
    # TODO: this needs to be customizable; how do we do this?
    # Ideally we would have some user-friendly pattern syntax that users could
    # specify...
    # Or maybe we could just run a filter on `data.raw` so that a user only gets
    # what they want, and then it's up to them to take the game object and 
    # translate it into their desired form
    # That seems to make the most sense, and is essentially what we're already
    # doing on the draftsman side.
    pass

def update_draftsman_data(game_path: str, mods_path: str, verbose: bool=False):

    lua_instance = run_data_lifecycle(game_path=game_path, mods_path=mods_path, verbose=verbose)

    extract_data()