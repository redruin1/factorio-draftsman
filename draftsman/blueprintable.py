# blueprintable.py

"""
Alias module. Imports :py:class:`.Blueprint`, :py:class:`.BlueprintBook`,
:py:class:`.DeconstructionPlanner`, :py:class:`.UpgradePlanner`, and
:py:class:`.Group` under the namespace ``draftsman``.
"""

from draftsman import __factorio_version_info__
from draftsman.error import IncorrectBlueprintTypeError
from draftsman.utils import reissue_warnings, string_to_JSON, decode_version

from draftsman.classes.blueprintable import Blueprintable
from draftsman.classes.blueprint import Blueprint
from draftsman.classes.deconstruction_planner import DeconstructionPlanner
from draftsman.classes.upgrade_planner import UpgradePlanner
from draftsman.classes.blueprint_book import BlueprintBook


@reissue_warnings
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
    blueprintable_JSON = string_to_JSON(blueprintable_string)
    return get_blueprintable_from_JSON(blueprintable_JSON)


@reissue_warnings
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
        blueprintable_type = Blueprint
    elif "deconstruction_planner" in blueprintable_JSON:
        blueprintable_type = DeconstructionPlanner
    elif "upgrade_planner" in blueprintable_JSON:
        blueprintable_type = UpgradePlanner
    elif "blueprint_book" in blueprintable_JSON:
        blueprintable_type = BlueprintBook
    else:
        raise IncorrectBlueprintTypeError(
            "Unknown blueprintable '{}'".format(next(blueprintable_JSON))
        )
    # Try and get the version from the dictionary, falling back to current
    # environment configuration if not found
    root_item = blueprintable_type.root_item.fget(blueprintable_type)
    if "version" in blueprintable_JSON[root_item]:
        version = decode_version(blueprintable_JSON[root_item]["version"])
    else:
        version = __factorio_version_info__

    return blueprintable_type.from_dict(blueprintable_JSON, version=version)
