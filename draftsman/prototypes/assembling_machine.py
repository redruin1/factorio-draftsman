# assembling_machine.py

from draftsman.constants import Inventory
from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    InputIngredientsMixin,
    ModulesMixin,
    ItemRequestMixin,
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
from draftsman.serialization import draftsman_converters
from draftsman.signatures import ModuleName, QualityName
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import assembling_machines
from draftsman.data import entities, modules

import attrs
from typing import Iterable, Optional


@fix_incorrect_pre_init
@attrs.define
class AssemblingMachine(
    InputIngredientsMixin,
    ModulesMixin,
    ItemRequestMixin,
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

    def request_modules(
        self,
        module_name: ModuleName,
        slots: int | Iterable[int],
        quality: QualityName = "normal",
    ):
        return super().request_modules(
            Inventory.assembling_machine_modules, module_name, slots, quality
        )

    # =========================================================================

    __hash__ = Entity.__hash__


AssemblingMachine.add_schema(
    {"$id": "urn:factorio:entity:assembling-machine"},
    version=(1, 0),
    mro=(ItemRequestMixin, RecipeMixin, DirectionalMixin, Entity),
)

AssemblingMachine.add_schema(
    {
        "$id": "urn:factorio:entity:assembling-machine",
    },
    version=(2, 0),
)
