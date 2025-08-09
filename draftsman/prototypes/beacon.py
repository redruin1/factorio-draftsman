# beacon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    EnergySourceMixin,
)
from draftsman.constants import InventoryType
from draftsman.signatures import ModuleID, QualityID

from draftsman.data.entities import beacons
from draftsman.data import modules

import attrs
from typing import Iterable


@attrs.define
class Beacon(ModulesMixin, EnergySourceMixin, Entity):
    """
    An entity designed to apply module effects to other machines in its radius.
    """

    @property
    def similar_entities(self) -> list[str]:
        return beacons

    # =========================================================================

    @property
    def module_slots_occupied(self) -> int:
        return len(
            {
                inv_pos.stack
                for req in self.item_requests
                if req.id.name in modules.raw
                for inv_pos in req.items.in_inventory
                if inv_pos.inventory == InventoryType.BEACON_MODULES
            }
        )

    # =========================================================================

    def request_modules(
        self,
        module_name: str, # TODO: should be ModuleID
        slots: int | Iterable[int],
        quality: QualityID = "normal",
    ):
        return super().request_modules(
            InventoryType.BEACON_MODULES, module_name, slots, quality
        )

    # =========================================================================

    __hash__ = Entity.__hash__
