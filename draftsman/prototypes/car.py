# car.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    VehicleMixin,
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
    EnergySourceMixin,
    OrientationMixin,
    Entity,
):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    A drivable entity which moves in along one axis and can steer left or right.
    Includes vanilla tanks as well as regular cars.
    """

    @property
    def similar_entities(self) -> list[str]:
        return cars

    # =========================================================================

    __hash__ = Entity.__hash__
