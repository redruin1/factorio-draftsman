# blueprint.py

from draftsman import utils
from draftsman.error import MalformedBlueprintStringError
from typing import Union


from draftsman.classes.blueprint import Blueprint
from draftsman.classes.blueprintbook import BlueprintBook


def get_blueprintable_from_string(blueprint_string):
    # type: (str) -> Union[Blueprint, BlueprintBook]
    """Returns a `Blueprint` or a `Blueprint` depending on the string passed in.

    Gets a Blueprintable object based off of the `blueprint_string`. A
    'Blueprintable object' in this context either a Blueprint or a
    BlueprintBook, depending on the particular string you passed in. This
    function allows you generically accept either Blueprint strings or
    BlueprintBook strings.

    Returns:
        Either a Blueprint or a BlueprintBook, depending on the input string.

    Raises:
        MalformedBlueprintStringError: if the blueprint_string cannot be
            resolved to be a valid Blueprint or BlueprintBook.
    """
    blueprintable = utils.string_to_JSON(blueprint_string)
    if "blueprint" in blueprintable:
        return Blueprint(blueprint_string)
    elif "blueprint_book" in blueprintable:
        return BlueprintBook(blueprint_string)
    else:
        raise MalformedBlueprintStringError
