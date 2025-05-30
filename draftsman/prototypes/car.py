# car.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    VehicleMixin,
    ItemRequestMixin,
    EquipmentGridMixin,
    EnergySourceMixin,
    OrientationMixin,
)

from draftsman.data.entities import cars

import attrs


@attrs.define
class Car(
    VehicleMixin,
    EquipmentGridMixin,
    ItemRequestMixin,
    EnergySourceMixin,
    OrientationMixin,
    Entity,
):
    """
    A drivable entity which moves in one direction and can steer left or right.
    """

    @property
    def similar_entities(self) -> list[str]:
        return cars

    # =========================================================================

    __hash__ = Entity.__hash__
