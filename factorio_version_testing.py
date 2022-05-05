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

import logging
import os.path
import subprocess
from git import Repo

from draftsman.data import mods
from draftsman.env import update
from draftsman.utils import version_string_to_tuple, version_tuple_to_string


def main():
    # Make sure we have no mods active, as this will mess everything up
    assert len(mods.mod_list) == 1 and mods.mod_list["base"]

    # Get the current repo
    directory = os.path.dirname(__file__)
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
    version_final = tag_list.index("1.0.0")
    for tag in tag_list[:version_final]:

        print(tag + ": ")

        # Set the head of the repo to match the current tag
        factorio_data.git.checkout(tag)

        # Update the submodule so that the data inside is correct
        factorio_data.submodule_update()

        # Try to:
        try:
            # Run draftsman-update
            update()
            # Run python -m unittest discover
            subprocess.run(["python", "-m", "unittest", "discover"])
            print("\tPASS")
        except Exception as e:
            logging.error(exc_info=True)
            print("\tFAIL")

    print("\n", "=" * 100, "\n")


    # After testing, reset the submodule's head back to the version right before 
    # latest
    # TODO: might be better to just record what version the submodule was at 
    # before and set it to that afterward
    factorio_data.git.checkout(tag_list[1])

    # Update the submodule so that the data inside is correct
    factorio_data.submodule_update()

    # Update the module back to the original version
    update()


if __name__ == "__main__":
    main()