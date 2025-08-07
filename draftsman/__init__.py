# __init__.py
"""
Allows the user to import, create, manipulate, and export Factorio blueprint
strings.
"""

from draftsman._version import (
    __version__ as __version__,
    __version_info__ as __version_info__,
)

import attrs

__all__ = ["__version__", "__version_info__", "DEFAULT_FACTORIO_VERSION"]

DEFAULT_FACTORIO_VERSION = (2, 0, 0)
"""
The Factorio version that Draftsman should assume it is operating under if it
cannot determine the version from it's current environment, due to its absence
or corruption. Should rarely (if ever) need to be used, intended to be a 
last-ditch fallback.
"""

# def field(*, default=attrs.NOTHING, omittable=True):
#     """
#     TODO
#     """
#     pass


def define(cls):
    """
    Custom `attrs.define` wrapper. Handles Draftsman-specific boilerplate to
    reduce repetition.
    """

    # Grab all specified class validators
    model_validators = [
        v for _, v in cls.__dict__.items() if hasattr(v, "__attrs_class_validator__")
    ]
    cls = attrs.define(cls)  # field_transformer=field_transformer

    # Attach class validators to the instance
    cls.__attrs_class_validators__ = model_validators

    # TODO: we could patch __attrs_post_init__ to run the model validators and
    # conjoin that with any existing class implementation
    return cls
