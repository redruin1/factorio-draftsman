# mod_list.py

from draftsman.utils import get_suggestion
from draftsman.error import IncorrectModFormatError, MissingModError
from draftsman.utils import version_string_to_tuple

import io
import json
import os
import re
from typing import NamedTuple
import zipfile


class Dependency(NamedTuple):
    flag: str
    name: str
    operation: str
    version: str

    def __str__(self):
        return "{} {} {} {}".format(
            self.flag if self.flag else "",
            self.name,
            self.operation if self.operation else "",
            self.version if self.version else "",
        )


class Mod:
    """
    Mod object that stores metadata during the load process. Mostly used for
    structuring the data and determining the load order.
    """

    archive_regex = re.compile(r"(([\w\D]+)_([\d\.]+))\.zip")
    folder_regex = re.compile(r"([^\s.]+)(?:_([\d\.]+))?$")
    dependency_regex = re.compile(
        r"^(\!|\?|\(\?\)|~)?[^\w\?\!]*([\w-]+)([><=]=?)?([\d\.]+)?"
    )

    def __init__(
        self,
        # Path to the parent folder or archive file
        location: str,
        stages: set[str],
        # Standard info.json data
        name: str,
        title: str,
        author: str,
        version: str = "",  # Required, but `core` is special for some reason
        contact: str | None = None,
        homepage: str | None = None,
        description: str | None = None,
        factorio_version: str | None = None,
        dependencies: list[str] = ["base"],
        # Feature flags (new in 2.0)
        quality_required: bool = False,
        rail_bridges_required: bool = False,
        space_travel_required: bool = False,
        spoiling_required: bool = False,
        freezing_required: bool = False,
        segmented_units_required: bool = False,
        expansion_shaders_required: bool = False,
        # Other goodies not normally included, but nice to know
        enabled: bool = True,
        # is_archive: bool,
        # internal_folder: str,
        # location: str,
        # info: json,
        # files: dict[str, str],
        # data: zipfile.ZipFile,
        # All other keys are free for users to write, so we collect them here
        **kwargs,
    ):
        self.location = location
        self.stages = stages

        self.name = name
        self.title = title
        self.author = author
        self.version = version
        self.contact = contact
        self.homepage = homepage
        self.description = description
        self.factorio_version = factorio_version

        for i, dependency in enumerate(dependencies):
            # Remove whitespace
            dependency = dependency.replace(" ", "")
            # Convert
            m = Mod.dependency_regex.match(dependency)
            dependency = Dependency(flag=m[1], name=m[2], operation=m[3], version=m[4])
            # Replace
            dependencies[i] = dependency
        self.dependencies: list[Dependency] = dependencies

        self.feature_flags = {
            "quality": quality_required,
            "rail_bridges": rail_bridges_required,
            "space_travel": space_travel_required,
            "spoiling": spoiling_required,
            "freezing": freezing_required,
            "segmented_units": segmented_units_required,
            "expansion_shaders": expansion_shaders_required,
        }

        self.enabled = enabled

        # self.name = name
        # self.author = author
        # self.
        # self.internal_folder = internal_folder
        # self.version = version
        # self.is_archive = is_archive
        # self.location = location
        # self.info = info
        # self.files = files
        # self.data = data
        # self.enabled = enabled
        # self.dependencies = []

    def setup_archive(self):
        """
        Initialize the internal structure with archive data.
        """
        self.is_archive = True

    def setup_folder(self):
        """
        Initialize the internal structure with folder data.
        """
        self.is_archive = False

    def depends_on(self, mod_name):
        """
        Returns true if ``mod`` is a required dependency of this Mod.
        """
        return mod_name in {dep.name for dep in self.dependencies}

    def get_depth(self):
        depth = 1
        for dependency in self.dependencies:
            dependency: "Mod"
            depth = max(depth, depth + dependency.get_depth())
        return depth

    def get_file(self, filepath) -> str:
        """
        Grabs the data from the file as a string.
        """
        if self.is_archive:
            return archive_to_string(self.data)
        else:
            return file_to_string(filepath=self.location + "/" + filepath)
        pass

    def __lt__(self, other: "Mod") -> bool:
        return self.name < other.name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "Mod('{}'{})".format(
            self.name, " " + self.version if self.version else ""
        )


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


def read_mod_list_json(mods_path):
    """
    Simple wrapper to read from a `mod-list.json` file.
    """
    with open(os.path.join(mods_path, "mod-list.json")) as mod_list_file:
        return json.load(mod_list_file)


def write_mod_list_json(mods_path, json_dict):
    """
    Simple wrapper to write to a `mod-list.json` file.
    """
    with open(os.path.join(mods_path, "mod-list.json"), "w") as mod_list_file:
        out = json.dumps(json_dict, indent=2)
        # Factorio likes to prepend a newline behind every open bracket, for
        # readability I suppose. Might as well stay consistent.
        # We casually do a bit of the dark arts (aka regex):
        fixed = re.sub(r"^(\s*){$", "\n\\1{", out, flags=re.M)
        mod_list_file.write(fixed)


def register_mod(mod_name, mod_location, mod_list_json={"mods": {}}):
    """
    Attempts to create a :py:class:`.Mod` object from the given folder or zip
    file. This function not only touches the archive or folder pointed to, but
    also determines whether or not it's enabled from the ``mod_list_json``
    parameter (if present).
    """

    # external_mod_version = None  # Optional (the version indicated by filepath)

    if mod_name.lower().endswith(".zip"):
        # Zip file
        m = Mod.archive_regex.match(mod_name)
        if not m:
            raise IncorrectModFormatError(
                "Mod archive '{}' does not fit the 'name_version' format".format(
                    mod_name
                )
            )
        folder_name = m.group(1)
        mod_name = m.group(2)
        # external_mod_version = m.group(3)
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
            # Try a case insensitive alphanumeric only comparison,
            # and succeed if we get exactly one hit.
            dirs = list(topdirs)
            simplified_dirs = [re.sub(r"[^a-zA-Z0-9]", "", s).lower() for s in dirs]
            simplified_foldername = re.sub(r"[^a-zA-Z0-9]", "", folder_name).lower()
            if simplified_dirs.count(simplified_foldername) == 1:
                # we want the original folder, so get the index.
                index = simplified_dirs.index(simplified_foldername)
                mod_folder = dirs[index]
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
            mod_info = json.loads(archive_to_string(files, mod_folder + "/info.json"))
        except KeyError:
            raise IncorrectModFormatError(
                "Mod '{}' has no 'info.json' file in its root folder".format(mod_name)
            )

        # mod_version = mod_info["version"]
        is_archive = True
        location = mod_location  # containing_dir + "/" + mod_name

    elif os.path.isdir(mod_location):
        # Folder
        m = Mod.folder_regex.match(mod_name)
        if not m:
            raise IncorrectModFormatError(
                "Mod folder '{}' does not fit the 'name' or 'name_version' format".format(
                    mod_name
                )
            )
        mod_name = m.group(1)
        # external_mod_version = m.group(2)
        try:
            with open(os.path.join(mod_location, "info.json"), "r") as info_file:
                mod_info = json.load(info_file)
        except FileNotFoundError:
            raise IncorrectModFormatError(
                "Mod '{}' has no 'info.json' file in its root folder".format(mod_name)
            )

        mod_folder = mod_location
        # mod_version = mod_info.get("version", "")  # "core" doesn't have a version
        is_archive = False
        files = None
        location = mod_location

    else:  # Regular file
        raise IncorrectModFormatError(
            "Given path '{}' not interpretable as a mod".format(mod_location)
        )

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
        mod_factorio_version = version_string_to_tuple(  # noqa: F841
            mod_info["factorio_version"]
        )
        # TODO: this check cannot happen here, has to happen after all mods are
        # registered
        # assert mod_factorio_version <= mods.versions["base"]

    mod_stages = set()
    if is_archive:
        # Attempt to load any setting files present
        settings_stages = (
            "settings.lua",
            "settings-updates.lua",
            "settings-final-fixes.lua",
        )
        for stage in settings_stages:
            try:
                # mod_data[stage] = archive_to_string(files, mod_folder + "/" + stage)
                files.getinfo(mod_folder + "/" + stage)
                mod_stages.add(stage)
            except KeyError:
                pass
        # Attempt to load any data files present
        data_stages = ("data.lua", "data-updates.lua", "data-final-fixes.lua")
        for stage in data_stages:
            try:
                # mod_data[stage] = archive_to_string(files, mod_folder + "/" + stage)
                files.getinfo(mod_folder + "/" + stage)
                mod_stages.add(stage)
            except KeyError:
                pass
    else:  # folder
        # Attempt to load any setting files present
        settings_stages = (
            "settings.lua",
            "settings-updates.lua",
            "settings-final-fixes.lua",
        )
        for stage in settings_stages:
            if os.path.isfile(mod_folder + "/" + stage):
                mod_stages.add(stage)
        # Attempt to load any data files present
        data_stages = ("data.lua", "data-updates.lua", "data-final-fixes.lua")
        for stage in data_stages:
            if os.path.isfile(mod_folder + "/" + stage):
                mod_stages.add(stage)

    enabled = next(
        (
            mod_dict
            for mod_dict in mod_list_json["mods"]
            if mod_dict["name"] == mod_name
        ),
        {"enabled": True},
    )["enabled"]

    current_mod = Mod(
        location=location.replace("\\", "/"),  # Make sure forward slashes
        stages=mod_stages,
        **mod_info,
        enabled=enabled,
    )

    if is_archive:
        current_mod.setup_archive()
    else:
        current_mod.setup_folder()

    # current_mod = Mod(
    #     name=mod_name,
    #     version=mod_version,
    #     internal_folder=mod_folder,
    #     is_archive=is_archive,
    #     location=location.replace("\\", "/"),  # Make sure forward slashes
    #     info=mod_info,
    #     files=files,
    #     data=mod_data,
    #     enabled=enabled # Default is enabled
    # )

    return current_mod


def discover_mods(
    game_path: str, mods_path: str, no_mods: bool = False
) -> dict[str, list[Mod]]:
    """
    Returns an list of all mods detected at a specific game data and mod folder
    location, including different versions of the same mod. If there are
    multiples of the same mod found, the mods are sorted latest version first,
    preferring folders if there's a tie.

    :param game_path: Path to the directory which houses Factorio's game data.
    :param mods_path: Path the the directory which houses the desired user mods.
    :param no_mods: Omits any user mods found at ``mods_path``, while leaving
        game data untouched.
    """

    # Check that our paths actually exist
    if not os.path.isdir(game_path):
        raise OSError("Directory '{}' not found".format(game_path))
    if not os.path.isdir(mods_path):
        raise OSError("Directory '{}' not found".format(mods_path))

    # Attempt to read `mod-list.json`
    try:
        mod_list_json = read_mod_list_json(mods_path=mods_path)
    except FileNotFoundError:
        # Supply default
        mod_list_json = {"mods": {}}

    # List of "mods". In Factorio parlance, a Mod is just a collection of files
    # associated with one another, meaning that base-game components like `base`
    # and `core` are also considered "mods", and as such are returned by this
    # function.
    # All found interpretable mods are added to this list, regardless of whether
    # or not they are enabled or not. Any duplicate mods (same name, different
    # version) are added to the list of mods with that name.
    mod_list: dict[str, list[Mod]] = {}

    # Traverse the game-data folder to find Wube "mods", like `base` and `core`
    for game_obj in os.listdir(game_path):
        location = os.path.join(game_path, game_obj)

        # In the game data folder, modules must be folders
        if not os.path.isdir(location):
            continue

        # Add the mod to the list of mods
        mod = register_mod(
            mod_name=game_obj,
            mod_location=location,
            mod_list_json=mod_list_json,
        )
        if mod.name in mod_list:
            mod_list[mod.name].append(mod)
        else:
            mod_list[mod.name] = [mod]

    # After that, we can register all of the regular mods, if present at path
    # and the no_mods flag is false
    if not no_mods:
        for mod_obj in os.listdir(mods_path):
            location = os.path.join(mods_path, mod_obj)

            # Only consider folders and zipfiles
            if not os.path.isdir(location) and not zipfile.is_zipfile(location):
                continue

            # Add the mod to the list of mods
            mod = register_mod(
                mod_name=mod_obj,
                mod_location=location,
                mod_list_json=mod_list_json,
            )
            if mod.name in mod_list:
                mod_list[mod.name].append(mod)
            else:
                mod_list[mod.name] = [mod]

    # Sort mods of different versions, preferring more modern ones. If two mods
    # of the same version are found and one is a folder, the folder is preferred
    # (since it's likely being locally developed)
    # After sort, the first item in the mod versions list should be the mod that
    # Factorio would use during its load process.
    for mod_name, mod_versions in mod_list.items():
        if mod_name == "core":  # Skip core because it has no versions to sort
            continue
        sorted_versions = sorted(
            mod_versions,
            key=lambda x: (version_string_to_tuple(x.version), not x.is_archive),
            reverse=True,
        )
        mod_list[mod_name] = sorted_versions

    return mod_list


def display_mods(mods: dict[str, list[Mod]], verbose=False) -> None:
    """
    Pretty-print a given list of mods, primarily for command line interface
    purposes.
    """

    def clamp(minimum, value, maximum):
        return max(minimum, min(value, maximum))

    # Determine the max length of each dynamic category
    name_width = clamp(4, max(len(mod_name) for mod_name in mods), 50)
    version_width = clamp(
        7, max(len(submod.version) for _, mod in mods.items() for submod in mod), 30
    )
    location_width = clamp(
        8, max(len(submod.location) for _, mod in mods.items() for submod in mod), 100
    )

    def truncate_str(input_str, max_length):
        """
        Truncate a given string to a fixed length with the last characters being "...".
        """
        return (
            input_str[0 : max_length - 3] + "..."
            if len(input_str) > max_length
            else input_str
        )

    if verbose:
        # Print header lines
        print(
            "{} ┃ {:<5} ┃ {:<{name_width}} ┃ {:<{version_width}} ┃ {}".format(
                "on?",
                "type",
                "name",
                "version",
                "location",
                name_width=name_width,
                version_width=version_width,
            )
        )
        print(
            "{0:━<3}━╋━{0:━<5}━╋━{0:━<{name_width}}━╋━{0:━<{version_width}}━╋━{0:━<{location_width}}".format(
                "━",
                name_width=name_width,
                version_width=version_width,
                location_width=location_width,
            )
        )

        for mod_name, mod_versions in mods.items():
            for i, mod in enumerate(mod_versions):
                if i == 0:
                    printed_name = truncate_str(mod.name, name_width)
                elif i == len(mod_versions) - 1:
                    printed_name = "└" + ("─" * (len(mod_name) - 2)) + ">"
                else:
                    printed_name = "├" + ("─" * (len(mod_name) - 2)) + ">"

                print(
                    "{} ┃ {} ┃ {:<{name_width}} ┃ {:>{version_width}} ┃ {}".format(
                        " ✓ " if mod.enabled and i == 0 else "   ",
                        "(zip)" if mod.is_archive else "(dir)",
                        printed_name,
                        (
                            "-"
                            if mod.version == ""
                            else truncate_str(mod.version, version_width)
                        ),
                        truncate_str(mod.location, location_width),
                        name_width=name_width,
                        version_width=version_width,
                    )
                )
    else:
        for mod_name, mod_versions in mods.items():
            for i, mod in enumerate(mod_versions):
                if i == 0:
                    printed_name = truncate_str(mod.name, name_width)
                elif i == len(mod_versions) - 1:
                    printed_name = "└" + ("─" * (len(mod_name) - 2)) + ">"
                else:
                    printed_name = "├" + ("─" * (len(mod_name) - 2)) + ">"

                print(
                    "{} {} {:<{name_width}}    {:>{version_width}}".format(
                        "✓" if mod.enabled and i == 0 else " ",
                        "(zip)" if mod.is_archive else "(dir)",
                        printed_name,
                        (
                            "-"
                            if mod.version == ""
                            else truncate_str(mod.version, version_width)
                        ),
                        name_width=name_width,
                        version_width=version_width,
                    )
                )


def set_mods_enabled(
    game_path: str,
    mods_path: str,
    mod_names: list[str],
    enabled: bool = True,
    verbose: bool = False,
):
    """
    Sets a given list of mod names to be either enabled or disabled, based on
    parameter ``enabled``.
    """
    # Grab the mods at `game_path` and `mods_path`
    mods = discover_mods(game_path=game_path, mods_path=mods_path)

    # Grab the current `mod-list.json` (or get default if not present)
    try:
        mod_list_dict = read_mod_list_json(mods_path=mods_path)
    except FileNotFoundError:
        # Generate default
        mod_list_dict = {"mods": [{"name": mod, "enabled": True} for mod in mods]}

    if mod_names == ["all"]:
        mod_names = [mod for mod in mods if mod not in ("base", "core")]
    else:
        # Check to make sure that all of the mods given point to discovered mods
        for mod_name in mod_names:
            if mod_name not in mods:
                raise MissingModError(
                    "Unrecognized mod name '{}'{}".format(
                        mod_name, get_suggestion(mod_name, mods.keys(), n=1)
                    )
                )

    for mod_name in mod_names:
        i = next(
            (
                i
                for i, mod_dict in enumerate(mod_list_dict["mods"])
                if mod_dict["name"] == mod_name
            )
        )
        mod_list_dict["mods"][i]["enabled"] = enabled

    if verbose:
        print("Mods {}: {}".format("enabled" if enabled else "disabled", mod_names))

    # Write the new `mod-list.json` back out
    write_mod_list_json(mods_path=mods_path, json_dict=mod_list_dict)
