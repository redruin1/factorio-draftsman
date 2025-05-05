# assembling_machine.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    ModulesMixin,
    RequestItemsMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import fix_incorrect_pre_init
from draftsman.warning import ModuleLimitationWarning

from draftsman.data.entities import assembling_machines
from draftsman.data import entities, modules

import attrs
from pydantic import ConfigDict, ValidationInfo, field_validator
from typing import Any, Literal, Optional, Union


@fix_incorrect_pre_init
@attrs.define
class AssemblingMachine(
    InputIngredientsMixin,
    ModulesMixin,
    RequestItemsMixin,
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

    __hash__ = Entity.__hash__
