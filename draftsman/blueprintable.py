# blueprintable.py

"""
Alias module. Imports :py:class:`.Blueprint`, :py:class:`.BlueprintBook`,
:py:class:`.DeconstructionPlanner`, :py:class:`.UpgradePlanner`, and
:py:class:`.Group` under the namespace ``draftsman``.
"""

from draftsman import utils
from draftsman.error import IncorrectBlueprintTypeError


from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.deconstruction_planner import DeconstructionPlanner
from draftsman.classes.upgrade_planner import UpgradePlanner
from draftsman.classes.blueprint_book import BlueprintBook


@utils.reissue_warnings
def get_blueprintable_from_string(blueprintable_string: str) -> Blueprintable:
    """
    Gets a Blueprintable object based off of the ``blueprint_string``. A
    "Blueprintable object" in this context means either a :py:class:`.Blueprint`,
    :py:class:`.DeconstructionPlanner`, :py:class:`.UpgradePlanner`, or a
    :py:class:`.BlueprintBook`, depending on the particular string you passed in.
    This function allows you generically accept export strings of any of the
    above types and return the appropriate class instance.

    :param blueprintable_string: The blueprint string to interpret.

    :returns: A :py:class:`.Blueprint`, :py:class:`.BlueprintBook`,
        :py:class:`.DeconstructionPlanner`, or :py:class:`.UpgradePlanner`
        object.

    :exception MalformedBlueprintStringError: If the ``blueprint_string`` cannot
        be resolved due to an error with the zlib or JSON decompression.
    :exception IncorrectBlueprintTypeError: If the root level of the
        decompressed JSON object is neither ``"blueprint"``,
        ``"deconstruction_planner"``, ``"upgrade_planner"``, nor
        ``"blueprint_book"``, and thus it's type cannot be deduced.
    """
    blueprintable = utils.string_to_JSON(blueprintable_string)
    if "blueprint" in blueprintable:
        return Blueprint(blueprintable)
    elif "deconstruction_planner" in blueprintable:
        return DeconstructionPlanner(blueprintable)
    elif "upgrade_planner" in blueprintable:
        return UpgradePlanner(blueprintable)
    elif "blueprint_book" in blueprintable:
        return BlueprintBook(blueprintable)
    else:
        raise IncorrectBlueprintTypeError(
            "Unknown blueprintable '{}'".format(list(blueprintable.keys())[0])
        )


@utils.reissue_warnings
def get_blueprintable_from_JSON(blueprintable_JSON: dict) -> Blueprintable:
    """
    Gets a Blueprintable object based off of the ``blueprint_JSON``. A
    "Blueprintable object" in this context means either a :py:class:`.Blueprint`,
    :py:class:`.DeconstructionPlanner`, :py:class:`.UpgradePlanner`, or a
    :py:class:`.BlueprintBook`, depending on the particular dict you passed in.
    This function allows you generically accept any valid JSON structure of the
    the above types and return the appropriate class instance.

    :param blueprintable_JSON: The blueprint JSON dict to interpret.

    :returns: A :py:class:`.Blueprint`, :py:class:`.BlueprintBook`,
        :py:class:`.DeconstructionPlanner`, or :py:class:`.UpgradePlanner`
        object.

    :exception IncorrectBlueprintTypeError: If the root level of the
        decompressed JSON object is neither ``"blueprint"``,
        ``"deconstruction_planner"``, ``"upgrade_planner"``, nor
        ``"blueprint_book"``, and thus it's type cannot be deduced.
    """
    if "blueprint" in blueprintable_JSON:
        return Blueprint(blueprintable_JSON)
    elif "deconstruction_planner" in blueprintable_JSON:
        return DeconstructionPlanner(blueprintable_JSON)
    elif "upgrade_planner" in blueprintable_JSON:
        return UpgradePlanner(blueprintable_JSON)
    elif "blueprint_book" in blueprintable_JSON:
        return BlueprintBook(blueprintable_JSON)
    else:
        raise IncorrectBlueprintTypeError(
            "Unknown blueprintable '{}'".format(list(blueprintable_JSON.keys())[0])
        )
