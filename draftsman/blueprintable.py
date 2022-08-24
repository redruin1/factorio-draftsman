# blueprint.py
# -*- encoding: utf-8 -*-

"""
Alias module. Imports :py:class:`.Blueprint` and :py:class:`.BlueprintBook` 
under the namespace ``draftsman``.
"""

from draftsman import utils
from draftsman.error import IncorrectBlueprintTypeError
from typing import Union


from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.deconstruction_planner import DeconstructionPlanner
from draftsman.classes.upgrade_planner import UpgradePlanner
from draftsman.classes.blueprintbook import BlueprintBook


@utils.reissue_warnings
def get_blueprintable_from_string(blueprintable_string):
    # type: (str) -> Blueprintable
    """
    Returns a :py:class:`.Blueprint` or a :py:class:`.BlueprintBook` depending
    on the string passed in.

    Gets a Blueprintable object based off of the ``blueprint_string``. A
    "Blueprintable object" in this context means either a :py:class:`.Blueprint`,
    :py:class:`.DeconstructionPlanner`, :py:class:`.UpgradePlanner`, or a
    :py:class:`.BlueprintBook`, depending on the particular string you passed in.
    This function allows you generically accept either export strings of any of
    the above types and return the appropriate class instance.

    :param blueprintable_string: The blueprint string to interpret.

    :returns: A ``Blueprint``, ``DeconstructionPlanner``, ``UpgradePlanner``,
        or ``BlueprintBook`` object.

    :exception MalformedBlueprintStringError: If the ``blueprint_string`` cannot
        be resolved due to an error with the zlib or JSON decompression.
    :exception IncorrectBlueprintTypeError: If the root level of the
        decompressed JSON object is neither ``"blueprint"``,
        ``"deconstruction_planner"``, ``"upgrade_planner"``, nor
        ``"blueprint_book"``.
    """
    blueprintable = utils.string_to_JSON(blueprintable_string)
    if "blueprint" in blueprintable:
        return Blueprint(blueprintable_string)
    elif "deconstruction_planner" in blueprintable:
        return DeconstructionPlanner(blueprintable_string)
    elif "upgrade_planner" in blueprintable:
        return UpgradePlanner(blueprintable_string)
    elif "blueprint_book" in blueprintable:
        return BlueprintBook(blueprintable_string)
    else:
        raise IncorrectBlueprintTypeError(
            "Unknown blueprintable '{}'".format(list(blueprintable.keys())[0])
        )
