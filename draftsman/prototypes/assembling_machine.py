# assembling_machine.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    ModulesMixin,
    ItemRequestMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.signatures import AttrsSignalID
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import assembling_machines
from draftsman.data import entities, modules

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class AssemblingMachine(
    InputIngredientsMixin,
    ModulesMixin,
    ItemRequestMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    A machine that takes input items and produces output items. Includes
    assembling machines, chemical plants, oil refineries, and centrifuges, but
    does not include :py:class:`.RocketSilo`.
    """

    @property
    def similar_entities(self) -> list[str]:
        return assembling_machines

    # =========================================================================

    @property
    def allowed_effects(self) -> Optional[set[str]]:
        # If name not known, return None
        entity = entities.raw.get(self.name, None)
        if entity is None:
            return None
        # If name known, but no key, then return empty list
        result = entity.get("allowed_effects", [])
        # Normalize single string effect to a 1-length list
        return {result} if isinstance(result, str) else set(result)

    # =========================================================================

    # TODO: reimplement, but do so more specifically; i.e. allowed_inputs
    # @property  # TODO abstractproperty
    # def allowed_items(self) -> Optional[set[str]]:
    #     if self.allowed_input_ingredients is None:
    #         return None
    #     else:
    #         return self.allowed_modules + self.allowed_input_ingredients

    @property
    def allowed_modules(self) -> Optional[set[str]]:  # TODO: maybe set?
        if self.recipe is None:
            return super().allowed_modules
        else:
            return modules.get_modules_from_effects(self.allowed_effects, self.recipe)

    # =========================================================================

    circuit_set_recipe: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the circuit network should set the current recipe of the 
    machine.
    """

    # =========================================================================

    read_contents: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the items currently inside of the assembling machine should
    be broadcasted to the circuit network.
    """

    # =========================================================================

    include_in_crafting: bool = attrs.field(
        default=True, validator=instance_of(bool)
    )
    """
    Whether or not to output the contents of the items that are currently being
    used as ingredients during machine operation in addition to the other items
    currently sitting in this assembling machine. Only has an effect if 
    :py:attr:`.read_contents` is set to ``True``.
    """

    # =========================================================================

    read_recipe_finished: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the assembling machine should pulse a signal for 1-tick the
    instant a recipe finishes it's crafting cycle. The signal that is output is
    determined by :py:attr:`.recipe_finished_signal`.
    """

    # =========================================================================

    recipe_finished_signal: Optional[AttrsSignalID] = attrs.field(
        default=None,
        converter=AttrsSignalID.converter,
        validator=instance_of(Optional[AttrsSignalID])
    )
    """
    What signal to pulse when the crafting cycle completes. Only pulsed if 
    :py:attr:`.read_recipe_finished` is set to ``True``.
    """

    # =========================================================================

    read_working: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not a control signal should be broadcast to the circuit network
    
    """

    # =========================================================================

    __hash__ = Entity.__hash__


AssemblingMachine.add_schema(
    {
        "$id": "urn:factorio:entity:assembling-machine"
    },
    version=(1, 0),
    mro=(ItemRequestMixin, RecipeMixin, DirectionalMixin, Entity)
)

AssemblingMachine.add_schema(
    {
        "$id": "urn:factorio:entity:assembling-machine"
    },
    version=(2, 0)
)

# TODO: add hook functions