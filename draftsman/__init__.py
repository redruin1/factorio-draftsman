# __init__.py
"""
Allows the user to import, create, manipulate, and export Factorio blueprint 
strings.

`draftsman` attempts to provide a convinient, 'one-stop-shop' solution to the
problem of programmatically creating blueprint strings, used for automation of 
designing structures that would be too tedius to build otherwise.

In addition to providing the bare functionality of importing and exporting, 
`draftsman` is designed with the developer in mind, and has a wide array of 
methods and classes designed to write clean, self-documenting scripts. 
`draftsman` is also well-documented, well-tested, and easy to install.
"""

from draftsman._version import __version__, __version_info__
from draftsman._factorio_version import __factorio_version__, __factorio_version_info__

import attrs


def define(cls):
    """
    Custom `attrs.define` wrapper. Handles Draftsman-specific boilerplate to
    reduce repetition.
    """
    # Grab all specified validators
    model_validators = [
        v for _, v in cls.__dict__.items() if hasattr(v, "__attrs_class_validator__")
    ]
    cls = attrs.define(cls)
    cls.__attrs_class_validators__ = model_validators
    # TODO: we could patch __attrs_post_init__ to run the model validators and
    # conjoin that with any existing class implementation
    return cls


# def field(*, default=attrs.NOTHING, omittable=True):
#     """
#     TODO
#     """
#     pass
