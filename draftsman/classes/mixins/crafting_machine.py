# crafting_machine.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsSignalID
from draftsman.validators import instance_of

import attrs
from typing import Optional


@attrs.define(slots=False)
class CraftingMachineMixin(Exportable):
    """
    Gives the crafting machine circuit controls over it's behavior.
    """

    circuit_set_recipe: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not the circuit network should set the current recipe of the 
    machine.
    """

    # =========================================================================

    read_contents: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not the items currently inside of the assembling machine should
    be broadcasted to the circuit network.
    """

    # =========================================================================

    include_in_crafting: bool = attrs.field(default=True, validator=instance_of(bool))
    """
    Whether or not to output the contents of the items that are currently being
    used as ingredients during machine operation in addition to the other items
    currently sitting in this assembling machine. Only has an effect if 
    :py:attr:`.read_contents` is set to ``True``.
    """

    # =========================================================================

    read_recipe_finished: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not the assembling machine should pulse a signal for 1-tick the
    instant a recipe finishes it's crafting cycle. What signal is output is
    determined by :py:attr:`.recipe_finished_signal`.
    """

    # =========================================================================

    recipe_finished_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    What signal to pulse when the crafting cycle completes. Only operates if 
    :py:attr:`.read_recipe_finished` is ``True``.
    """

    # =========================================================================

    read_working: bool = attrs.field(default=False, validator=instance_of(bool))
    """
    Whether or not a control signal should be broadcast to the circuit network
    when the machine is actively crafting an item or items. What signal is 
    output is determined by :py:attr:`.working_signal`.
    """

    # =========================================================================

    working_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID]),
    )
    """
    What signal to continuously output when the machine is crafting. Only 
    operates if :py:attr:`.read_working` is ``True``.
    """


CraftingMachineMixin.add_schema(None, version=(1, 0))

draftsman_converters.get_version((1, 0)).add_hook_fns(
    CraftingMachineMixin, lambda fields: {}
)

CraftingMachineMixin.add_schema(
    {
        "properties": {
            "control_behavior": {
                "type": "object",
                "properties": {
                    "set_recipe": {"type": "boolean", "default": "false"},
                    "read_contents": {"type": "boolean", "default": "false"},
                    "include_in_crafting": {"type": "boolean", "default": "true"},
                    "read_recipe_finished": {"type": "boolean", "default": "false"},
                    "recipe_finished_signal": {
                        "anyOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
                    },
                    "read_working": {"type": "boolean", "default": "false"},
                    "working_signal": {
                        "anyOf": [{"$ref": "urn:factorio:signal-id"}, {"type": "null"}]
                    },
                },
            }
        },
    },
    version=(2, 0),
)

draftsman_converters.get_version((2, 0)).add_hook_fns(
    CraftingMachineMixin,
    lambda fields: {
        ("control_behavior", "set_recipe"): fields.circuit_set_recipe.name,
        ("control_behavior", "read_contents"): fields.read_contents.name,
        ("control_behavior", "include_in_crafting"): fields.include_in_crafting.name,
        ("control_behavior", "read_recipe_finished"): fields.read_recipe_finished.name,
        (
            "control_behavior",
            "recipe_finished_signal",
        ): fields.recipe_finished_signal.name,
        ("control_behavior", "read_working"): fields.read_working.name,
        ("control_behavior", "working_signal"): fields.working_signal.name,
    },
)
