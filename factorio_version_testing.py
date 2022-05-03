# factorio_version_testing.py

"""
Script that iterates over all the tagged versions of Factorio data and runs the
test suite to test exactly how far back Draftsman is compatable. Also shows 
which versions passed and what the errors were for the ones that failed.
"""

# git tag --list --sort=version:refname

import os.path
from git import Repo
from draftsman.utils import version_string_to_tuple, version_tuple_to_string

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

print(tag_list)
print(factorio_data.head)

# Iterate over every tag in the list
for tag in tag_list:

    # Set the head of the repo to match the current tag

    # Update the submodule so that the data inside is correct

    # Try to:
    # Run draftsman-update
    # Run python -m unittest discover

    # If it passed, show a pass
    # If it failed, show a fail and the error
    pass