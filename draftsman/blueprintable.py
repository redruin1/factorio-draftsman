# blueprint.py

"""
Alias module. Imports :py:class:`.Blueprint` and :py:class:`.BlueprintBook` 
under the namespace ``draftsman``.
"""

from draftsman import utils
from draftsman.error import IncorrectBlueprintTypeError
from typing import Union


from draftsman.classes.blueprint import Blueprint
from draftsman.classes.blueprintbook import BlueprintBook


def get_blueprintable_from_string(blueprint_string):
    # type: (str) -> Union[Blueprint, BlueprintBook]
    """
    Returns a :py:class:`.Blueprint` or a :py:class:`.BlueprintBook` depending
    on the string passed in.

    Gets a Blueprintable object based off of the ``blueprint_string``. A
    "Blueprintable object" in this context means either a Blueprint or a
    BlueprintBook, depending on the particular string you passed in. This
    function allows you generically accept either Blueprint or BlueprintBook
    strings and return the appropriate class instance.

    :param blueprint_string: The blueprint string to interpret.

    :returns: Either a ``Blueprint`` or ``BlueprintBook`` object.

    :exception MalformedBlueprintStringError: If the ``blueprint_string`` cannot
        be resolved due to an error with the zlib or JSON decompression.
    :exception IncorrectBlueprintTypeError: If the root level of the
        decompressed JSON object is neither ``"blueprint"``, ``"blueprint_book"``.
    """
    blueprintable = utils.string_to_JSON(blueprint_string)
    if "blueprint" in blueprintable:
        return Blueprint(blueprint_string)
    elif "blueprint_book" in blueprintable:
        return BlueprintBook(blueprint_string)
    else:
        raise IncorrectBlueprintTypeError
