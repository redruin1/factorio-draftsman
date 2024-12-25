# script.py

import draftsman
from draftsman._version import __version__
from draftsman._factorio_version import __factorio_version__

from draftsman.environment.mod_list import discover_mods, display_mods, set_mods_enabled
from draftsman.environment.mod_settings import read_mod_settings, write_mod_settings
from draftsman.environment.update import specify_factorio_version, update_draftsman_data

import argparse
import json
import os


class DraftsmanCommandArgs(argparse.Namespace):
    game_path: str
    mods_path: str
    verbose: bool
    operation: str

    # `factorio-version`
    desired_version: str

    # `enable/disable`
    mod_names: list[str]

    # `update`
    log: bool
    no_mods: bool


def main():
    """
    ``draftsman`` console script entry point. Header point which directs to
    different methods depending on mode passed in.
    """
    # Determine where the module is installed
    draftsman_install_folder = os.path.dirname(os.path.abspath(draftsman.__file__))
    draftsman_environment_folder = os.path.join(
        draftsman_install_folder, "environment"
    )  # TODO

    default_game_path = os.path.join(draftsman_install_folder, "factorio-data")
    default_mod_path = os.path.join(draftsman_install_folder, "factorio-mods")

    parser = argparse.ArgumentParser(
        prog="draftsman",
        description="A command-line utility for reporting and manipulating Draftsman's source data.",
    )
    # General arguments used by all subcommands
    parser.add_argument(
        "-p",
        "--game-path",
        type=str,
        default=default_game_path,
        help="The path to the data folder of the game; defaults to: "
        "`[python_install]/site-packages/draftsman/factorio-data`. If you own "
        "the game, you can pass in the folder where Factorio is installed, "
        "which will give you the ability to extract asset data in addition to "
        "prototype data.",
    )
    parser.add_argument(
        "-m",
        "--mods-path",
        type=str,
        default=default_mod_path,
        help="The path to search for (user) mods; defaults to "
        "`[python_install]/site-packages/draftsman/factorio-mods`.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Report additional information to stdout when available.",
    )

    subparsers = parser.add_subparsers(dest="operation", help="Operation:")

    # `draftsman list`
    list_command = subparsers.add_parser(
        "list", help="Lists information about all mods in the current environment."
    )

    # `draftsman mod-settings [mod.setting=value, ...]`
    mod_settings_command = subparsers.add_parser(
        "mod-settings",
        help="Displays all custom mod settings in `mod-settings.dat`, if present.",
    )
    # TODO: it would kinda be nice to be able to modify mod settings from here,
    # but it becomes complex once you remember that certain settings can only
    # have one out of a set of possible values, each of which is only defined
    # during their settings stage...

    # `draftsman enable [-r] mod-name [mod-name ...]`
    enable_command = subparsers.add_parser("enable", help="Enables a mod or mods.")
    enable_command.add_argument(
        "mod_names",
        metavar="mod-name",
        nargs="+",
        type=str,
        help="The name of the mod you want to enable. Modifies (or creates) the "
        "`mod-list.json` file located at the mod directory (-m). Passing in the "
        "keyword `all` will enable all present mods EXCEPT for `base` and `core`, "
        "which must be manually specified.",
    )
    # TODO: I think this would be useful. It's also very complex, so I'm going
    # to postepone it for the time someone actively asks for it.
    # enable_command.add_argument(
    #     "-r",
    #     "--recursive",
    #     action="store_true",
    #     help="Recursively enable the dependencies of the specified mods."
    # )

    # `draftsman disable [-r] mod-name [mod-name ...] `
    disable_command = subparsers.add_parser("disable", help="Disables a mod or mods.")
    disable_command.add_argument(
        "mod_names",
        metavar="mod-name",
        nargs="+",
        type=str,
        help="The name of the mod you want to disable. Modifies (or creates) the "
        "`mod-list.json` file located at the mod directory (-m). Passing in the "
        "keyword `all` will disable all present mods EXCEPT for `base` and `core`, "
        "which must be manually specified.",
    )
    # disable_command.add_argument(
    #     "-r",
    #     "--recursive",
    #     action="store_true",
    #     help="Recursively disable the dependencies of the specified mods. Note "
    #     "that this will only disable mod dependencies of a particular mod if no "
    #     "other enabled mod still depends on it. This flag will also not disable "
    #     "the `base` or `core` mod, though it will disable official Wube mods "
    #     "like `space-age`."
    # )

    # `draftsman version [-h]`
    version_command = subparsers.add_parser(
        "version", help="Displays the current Draftsman version."
    )

    # `draftsman factorio-version [-h] [desired-version]`
    factorio_version_command = subparsers.add_parser(
        "factorio-version",
        help="Displays or sets the current version of Factorio's data.",
    )
    factorio_version_command.add_argument(
        "desired_version",
        metavar="desired-version",
        nargs="?",
        default=None,
        const=True,
        help="If no argument is given, this command will report the version of "
        "the game at the game path (-p). If a version string is given, Draftsman "
        "will update the data at the repo to that value, IF the game path points "
        "to the default `factorio-data` repository; Draftsman is not capable of "
        "updating your actual Factorio client. Passing in the keyword `latest` "
        "will update the game to the latest version it can find.",
    )

    update_command = subparsers.add_parser(
        "update",
        help="Updates Draftsman's environment by emulating Factorio's data lifecycle.",
    )
    update_command.add_argument(
        "-l",
        "--log",
        action="store_true",
        help="Display any `log()` messages to stdout; any logged messages will "
        "be ignored if this argument is not set.",
    )
    update_command.add_argument(
        "--no-mods",
        action="store_true",
        help="Prevents user mods from loading even if they are enabled. Official "
        "mods made by Wube (`quality`, `elevated-rails`, `space-age`) are NOT "
        "affected by this flag; those should be manually configured with "
        "`draftsman enable|disable [official-mod]`",
    )

    args: DraftsmanCommandArgs = parser.parse_args(namespace=DraftsmanCommandArgs())

    if args.operation == "version":
        print("Draftsman {}".format(__version__))

    elif args.operation == "factorio-version":
        if args.desired_version is None:
            # Grab and populate the repo, making sure its a git repo we expect
            import git
            repo = git.Repo(args.game_path)
            repo.git.fetch()
            assert (
                repo.remotes.origin.url == "https://github.com/wube/factorio-data"
            ), "Targeted repo is not `wube/factorio-data`"

            # Grab the currently checked out tag for this repo
            # https://stackoverflow.com/a/32524783/8167625
            current_tag = next(
                (tag for tag in repo.tags if tag.commit == repo.head.commit), None
            )

            print("Factorio {}".format(current_tag))
        else:
            # This command will only work if we're pointing at a git repo of the
            # correct type
            specify_factorio_version(
                game_path=args.game_path,
                desired_version=args.desired_version,
                verbose=args.verbose,
            )

    elif args.operation == "list":
        mod_list = discover_mods(args.game_path, args.mods_path)
        display_mods(mod_list, verbose=args.verbose)

    elif args.operation == "mod-settings":
        try:
            mod_settings = read_mod_settings(mods_path=args.mods_path)
            for setting_type in ("startup", "runtime-global", "runtime-per-user"):
                # If the setting has no entries, skip it
                if len(mod_settings[setting_type]) == 0:
                    continue
                print("{}:".format(setting_type.upper()))
                for setting, value_dict in mod_settings[setting_type].items():
                    print(
                        "\t{}: {}".format(
                            setting,
                            "'" + value_dict["value"] + "'"
                            if type(value_dict["value"]) is str
                            else value_dict["value"],
                        )
                    )
        except FileNotFoundError:
            # TODO: If the file doesn't exist, the only way we get mod settings
            # info is by physically emulating the entire settings stage, prep
            # work and all. This is close to overkill, and it also might not be
            # what the user actually wants; maybe they only want to read the
            # settings specifically in the file. We could run the settings stage
            # if no `mod-settings.dat file`` is detected, and then write it out
            # to that folder (just like Factorio does); but this means that
            # Draftsman will be overwriting canonical user settings, so if I
            # ever introduce a bug it can wipe peoples mod settings...

            # For now, we take the simple route and just restrict this operation
            # to reading `mod-settings.dat` only.
            print("No `mod-settings.dat` file found at '{}'".format(args.mods_path))

    elif args.operation == "enable":
        set_mods_enabled(
            args.game_path, args.mods_path, args.mod_names, True, args.verbose
        )

    elif args.operation == "disable":
        set_mods_enabled(
            args.game_path, args.mods_path, args.mod_names, False, args.verbose
        )

    elif args.operation in "update":
        update_draftsman_data(
            game_path=args.game_path,
            mods_path=args.mods_path,
            show_logs=args.log,
            no_mods=args.no_mods,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    main()
