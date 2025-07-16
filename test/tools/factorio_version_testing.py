# factorio_version_testing.py

"""
Script that iterates over all the tagged versions of Factorio data and runs the
test suite to test exactly how far back Draftsman is compatable. Shows the
errors that occured when the commands were run.

This tells us that Draftsman works well with any version of Factorio greater
than 1.0.0; prior to this there are some structural changes that probably
require a separate version. Since the likelyhood the people will be using
versions of Factorio prior to 1.0.0 is quite slim, I feel comfortable kicking
this can down the road.
"""

from draftsman.data import mods
from draftsman.env import update
from draftsman.utils import version_string_to_tuple, version_tuple_to_string

from git import Repo
import pytest

import logging
import sys


def main():
    # Make sure we have no mods active, as this will mess everything up
    assert len(mods.mod_list) == 1 and mods.mod_list["base"]

    # Get the current repo
    directory = "D:\\SourceCode\\repos\\Python\\factorio-draftsman\\"  # FIXME: better
    repo = Repo(directory)

    # Get a list of all the tags corresponding to each Factorio version, and sort by
    # version instead of lexographically
    factorio_data = repo.submodules["factorio-data"].module()

    tag_list = []
    for tag in factorio_data.tags:
        tag_list.append(version_string_to_tuple(tag.name))
    tag_list.sort(reverse=True)
    for i, tag in enumerate(tag_list):
        tag_list[i] = version_tuple_to_string(tag)

    # Iterate over every tag in the list up to 1.0.0 (which is our limit)
    start_version = 0
    end_version = tag_list.index("1.0.0")
    output = ""  # because pytest captures stdout, we append our results to a
    # buffer and print it afterwards
    failed = False
    for tag in tag_list[start_version:end_version]:
        output += tag + ":\t"

        # Try to:
        try:
            # Run draftsman-update
            update(no_mods=True, factorio_version=tag)

            returncode = pytest.main(["test", "-Werror", "-qq"])

            if returncode == 0:
                output += "PASS\n"
            else:
                output += "FAIL\n"
                failed = True
        except Exception as e:
            logging.error(exc_info=True)
            output += "ERROR: {}".format(e)
            failed = True

        if failed:
            break

    print("Returning to version {}...".format(tag_list[0]))

    # After testing, reset the submodule's head back to latest
    update(no_mods=True, factorio_version=tag_list[0])

    print("\n", "=" * 100, "\n")

    print("Result:")
    print(output)


if __name__ == "__main__":
    main()
