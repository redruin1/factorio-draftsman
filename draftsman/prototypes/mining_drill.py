# mining_drill.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    CircuitReadResourceMixin,
    CircuitConditionMixin,
    CircuitEnableMixin,
    LogisticConditionMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.constants import InventoryType
from draftsman.signatures import QualityID

from draftsman.data import entities, modules
from draftsman.data.entities import mining_drills

import attrs
from typing import Iterable, Optional


@attrs.define
class MiningDrill(
    ModulesMixin,
    CircuitReadResourceMixin,
    CircuitConditionMixin,
    LogisticConditionMixin,
    CircuitEnableMixin,
    ControlBehaviorMixin,
    CircuitConnectableMixin,
    EnergySourceMixin,
    DirectionalMixin,
    Entity,
):
    """
    An entity that extracts resources (item or fluid) from the environment.
    """

    @property
    def similar_entities(self) -> list[str]:
        return mining_drills

    # =========================================================================

    @property
    def allowed_effects(self) -> Optional[set[str]]:
        return entities.get_allowed_effects(self.name, default=entities.ALL_EFFECTS)

    # =========================================================================

    @property
    def module_slots_occupied(self) -> int:
        return len(
            {
                inv_pos.stack
                for req in self.item_requests
                if req.id.name in modules.raw
                for inv_pos in req.items.in_inventory
                if inv_pos.inventory == InventoryType.MINING_DRILL_MODULES
            }
        )

    # =========================================================================

    def request_modules(
        self,
        module_name: str,  # TODO: should be ModuleID
        slots: int | Iterable[int],
        quality: QualityID = "normal",
    ):
        return super().request_modules(
            InventoryType.MINING_DRILL_MODULES, module_name, slots, quality
        )

    # =========================================================================

    __hash__ = Entity.__hash__
