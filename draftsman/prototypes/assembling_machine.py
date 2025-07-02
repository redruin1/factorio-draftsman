# assembling_machine.py

from draftsman.constants import InventoryType
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    ModulesMixin,
    CraftingMachineMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    RecipeMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.signatures import ModuleID, QualityID
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import assembling_machines
from draftsman.data import modules

import attrs
from typing import Iterable, Optional


@fix_incorrect_pre_init
@attrs.define
class AssemblingMachine(
    InputIngredientsMixin,
    ModulesMixin,
    CraftingMachineMixin,
    LogisticConditionMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
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

    # TODO: validate item requests match whichever recipe is currently selected
    # @property  # TODO abstractproperty
    # def allowed_items(self) -> Optional[set[str]]:
    #     if self.allowed_input_ingredients is None:
    #         return None
    #     else:
    #         return self.allowed_modules + self.allowed_input_ingredients

    @property
    def allowed_modules(self) -> Optional[set[str]]:
        if self.recipe is None:
            return super().allowed_modules
        else:
            return modules.get_modules_from_effects(self.allowed_effects, self.recipe)

    # =========================================================================

    @property
    def module_slots_occupied(self) -> int:
        return len(
            {
                inv_pos.stack
                for req in self.item_requests
                if req.id.name in modules.raw
                for inv_pos in req.items.in_inventory
                if inv_pos.inventory == InventoryType.assembling_machine_modules
            }
        )

    # =========================================================================

    def request_modules(
        self,
        module_name: ModuleID,
        slots: int | Iterable[int],
        quality: QualityID = "normal",
    ):
        return super().request_modules(
            InventoryType.assembling_machine_modules, module_name, slots, quality
        )

    # =========================================================================

    __hash__ = Entity.__hash__
