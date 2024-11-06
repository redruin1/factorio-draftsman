# script.py

import draftsman
from draftsman._version import __version__
from draftsman._factorio_version import __factorio_version__

from draftsman.environment.mod_list import discover_mods, display_mods, set_mods_enabled
from draftsman.environment.mod_settings import read_mod_settings, write_mod_settings
from draftsman.environment.update import specify_factorio_version, update_draftsman_data

import argparse
import os


class DraftsmanCommandArgs(argparse.Namespace):
        game_path: str
        mods_path: str
        verbose: bool
        operation: str
        
        # `factorio-version`
        desired_version: str

        # `enable/disable`
        recursive: bool

def main():
    """
    ``draftsman`` console script entry point. Header point which directs to 
    different methods depending on mode passed in.
    """
    # Determine where the module is installed
    draftsman_install_folder = os.path.dirname(os.path.abspath(draftsman.__file__))
    draftsman_environment_folder = os.path.join(draftsman_install_folder, "environment") # TODO

    default_game_path = os.path.join(draftsman_install_folder, "factorio-data")
    default_mod_path = os.path.join(draftsman_install_folder, "factorio-mods")

    parser = argparse.ArgumentParser(
        prog="draftsman", 
        description="A command-line utility for reporting and manipulating Draftsman's source data."
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
        "prototype data."
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
    list_command = subparsers.add_parser("list", help="Lists information about all mods in the current environment.")

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
        "which must be manually specified."
    )
    enable_command.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively enable the dependencies of the specified mods."
    )

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
        "which must be manually specified."
    )
    disable_command.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively disable the dependencies of the specified mods. Note "
        "that this will only disable mod dependencies of a particular mod if no "
        "other enabled mod still depends on it. This flag will also not disable "
        "the `base` or `core` mod, though it will disable official Wube mods "
        "like `space-age`."
    )

    # `draftsman version [-h]`
    version_command = subparsers.add_parser("version", help="Displays the current Draftsman version.")

    # `draftsman factorio-version [-h] [desired-version]`
    factorio_version_command = subparsers.add_parser("factorio-version", help="Displays or sets the current version of Factorio's data.")
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
        "will update the game to the latest version it can find."
    )

    update_command = subparsers.add_parser("update", help="Updates Draftsman's environment by emulating Factorio's data lifecycle.")
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
        "`draftsman enable|disable [official-mod]`"
    )

    args: DraftsmanCommandArgs = parser.parse_args(namespace=DraftsmanCommandArgs())
    print(args)

    if args.operation == "version":
        print("Draftsman {}".format(__version__))

    elif args.operation == "factorio-version":
        if args.desired_version is None:
            print("Factorio {}".format(__factorio_version__))
        else:
            # Ensure we're not trying to update the actual game
            # TODO: this should be more specific, since it's hypothetically
            # possible that someone might want to update a different git repo
            assert args.game_path == default_game_path, "Can only update local `factorio-data`; cannot upgrade a regular Factorio installation"
            
            specify_factorio_version(game_path=args.game_path, desired_version=args.desired_version, verbose=args.verbose)

    elif args.operation == "list":
        mod_list = discover_mods(args.game_path, args.mods_path)
        display_mods(mod_list, verbose=args.verbose)

    elif args.operation == "enable":
        set_mods_enabled(args.game_path, args.mods_path, args.mod_names, True, args.recursive, args.verbose)

    elif args.operation == "disable":
        set_mods_enabled(args.game_path, args.mods_path, args.mod_names, False, args.recursive, args.verbose)

    elif args.operation in "update":
        update_draftsman_data(
            verbose=args.verbose,
            mods_path=args.mods_path,
            show_logs=args.log,
            no_mods=args.no_mods,
            report=args.report,
            factorio_version=args.factorio_version,
        )


if __name__ == "__main__":
    main()