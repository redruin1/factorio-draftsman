# fluid_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EquipmentGridMixin,
    ItemRequestMixin,
    OrientationMixin,
)

from draftsman.data.entities import fluid_wagons

import attrs


@attrs.define
class FluidWagon(EquipmentGridMixin, ItemRequestMixin, OrientationMixin, Entity):
    """
    A train wagon that holds a fluid as cargo.
    """

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return fluid_wagons

    # =========================================================================

    __hash__ = Entity.__hash__
