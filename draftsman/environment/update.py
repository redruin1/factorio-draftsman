# update.py

from draftsman.error import IncorrectModFormatError
from draftsman.utils import version_string_to_tuple, version_tuple_to_string

from git import Repo

import io
import json
import os
import re
import zipfile


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

    # Check the currently checked out tag for `factorio-data`
    repo = Repo(game_path)
    repo.git.fetch()
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
    

def register_mod(mod_name, mod_location, mods, factorio_version_info, verbose, report):
    mod_archive_regex = re.compile("(([\\w\\D]+)_([\\d\\.]+))\\.zip")
    mod_folder_regex = re.compile()

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
                "none of the internal folders match it's external name".format(
                    mod_name
                )
            )

        try:
            # Zipfiles don't like backslashes on Windows, so we manually 
            # concatenate
            mod_info = json.loads(
                archive_to_string(files, mod_folder + "/info.json")
            )
        except KeyError:
            raise IncorrectModFormatError(
                "Mod '{}' has no 'info.json' file in its root folder".format(
                    mod_name
                )
            )

        mod_version = mod_info["version"]
        archive = True
        location = mod_location #containing_dir + "/" + mod_name

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
                "Mod '{}' has no 'info.json' file in its root folder".format(
                    mod_name
                )
            )

        mod_folder = mod_location
        mod_version = mod_info.get("version", "") # "core" doesn't have version
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
            settings = archive_to_string(
                files, mod_folder + "/settings-updates.lua"
            )
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
            data_updates = archive_to_string(
                files, mod_folder + "/data-updates.lua"
            )
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
        elif version_string_to_tuple(
            previous_mod.version
        ) > version_string_to_tuple(current_mod.version):
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


def discover_mods(game_path, mods_path, no_mods=False, verbose=False):
    """
    TODO
    """
    # Check that our path actually exists (in case it was user specified)
    if not os.path.isdir(game_path):
        raise OSError("Directory '{}' not found".format(game_path))
    if not os.path.isdir(mods_path):
        raise OSError("Directory '{}' not found".format(mods_path))

    enabled_mod_list = {}
    try:
        with open(os.path.join(mods_path, "mod-list.json")) as mod_list_file:
            mod_json = json.load(mod_list_file)
            for mod in mod_json["mods"]:
                enabled_mod_list[mod["name"].replace(" ", "")] = (
                    mod["enabled"] and not no_mods
                )
    except FileNotFoundError:  # If no such file is found
        pass

    if verbose:
        print("\nDiscovering mods...\n")

    # Dictionary of "mods". In factorio parlance, a Mod is a collection of files
    # associated with one another, meaning that base-game components like `base`
    # and `core` are also considered "mods".
    mods: dict[str, Mod] = {}

    # Because of this lack of distinction, we traverse the game-data folder and 
    # treat every folder inside of it as a mod:
    for game_obj in os.listdir(game_path):
        location = game_path + "/" + game_obj # TODO: better
        if not os.path.isdir(location):
            continue

        # First make sure the mod is enabled, and skip if not
        if not enabled_mod_list.get(game_obj, True):
            continue

        # Add the mod to the list of mods
        mods[game_obj] = register_mod(game_obj, location, mods, factorio_version_info, verbose)

    # After that, we can register all of the regular mods, if present
    for mod_obj in os.listdir(factorio_mods_folder):
        location = mods_path + "/" + mod_obj # TODO: better

        # First make sure the mod is enabled, and skip if not
        if not enabled_mod_list.get(mod_obj, not no_mods):
            continue

        # Add the mod to the list of mods
        mods[mod_obj] = register_mod(mod_obj, location, mods, factorio_version_info, verbose)

    return mods

def run_data_lifecycle():
    pass

def extract_data():
    pass

def update_draftsman_data():

    run_data_lifecycle()

    extract_data()