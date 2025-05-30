# beacon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    ModulesMixin,
    ItemRequestMixin,
    EnergySourceMixin,
)
from draftsman.constants import Inventory
from draftsman.signatures import ModuleName, QualityName

from draftsman.data.entities import beacons

import attrs
from typing import Iterable


@attrs.define
class Beacon(ModulesMixin, ItemRequestMixin, EnergySourceMixin, Entity):
    """
    An entity designed to apply module effects to other machines in its radius.
    """

    @property
    def similar_entities(self) -> list[str]:
        return beacons

    # =========================================================================

    def request_modules(
        self,
        module_name: ModuleName,
        slots: int | Iterable[int],
        quality: QualityName = "normal",
    ):
        return super().request_modules(
            Inventory.beacon_modules, module_name, slots, quality
        )

    # =========================================================================

    __hash__ = Entity.__hash__

