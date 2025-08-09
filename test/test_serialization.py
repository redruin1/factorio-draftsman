# test_serialization.py

from draftsman.entity import Container

import pytest

import re


def test_get_version_DNE():
    """
    Make sure we get a proper error message if the user tries to structure/
    unstructure something with an unsupported version
    """
    with pytest.raises(
        ValueError, match=re.escape("No converter exists for version (0, 0)")
    ):
        Container.from_dict({}, version=(0, 0))

    with pytest.raises(
        ValueError, match=re.escape("No converter exists for version (0, 0)")
    ):
        Container().to_dict(version=(0, 0))
