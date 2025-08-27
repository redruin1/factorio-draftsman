# test_waypoint_factorio_versions.py

"""
Not part of the traditional pytest suite (despite it's name); instead it
automatically iterates over every single Factorio version and runs the test
suite using that data.
"""

import draftsman
from draftsman.environment.update import update_draftsman_data
from draftsman.utils import version_string_to_tuple, version_tuple_to_string

import git
from lupa import lua52
import os
import subprocess


def main():
    # Grab and populate the repo, making sure its a git repo we expect
    draftsman_path = os.path.dirname(os.path.abspath(draftsman.__file__))
    repo = git.Repo(draftsman_path + "/factorio-data")
    repo.git.fetch()
    assert (
        repo.remotes.origin.url == "https://github.com/wube/factorio-data"
    ), "Targeted repo is not `wube/factorio-data`"

    tag_list = sorted([version_string_to_tuple(tag.name) for tag in repo.tags])
    # Only select versions >= 1.0
    tag_list = tag_list[tag_list.index((1, 0, 0, 0)) :]

    versions = [(1, 0, 0), (1, 1, 0), (1, 1, 110), (2, 0, 8), tag_list[-1]]

    failed_versions = []
    for version in versions:
        version_string = version_tuple_to_string(version[:3])

        # Checkout version
        repo.git.checkout(version_string)

        # Update local data
        try:
            update_draftsman_data()
            print(version_string)
        except lua52.LuaError as e:
            print(e)
            print("{} failed".format(version_string))
            failed_versions.append(version_string)
            continue

        # Now run tests
        subprocess.run(["coverage", "run", "-p"], check=True)

    print("Failed Versions: ", failed_versions)


if __name__ == "__main__":
    main()
