# car.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    VehicleMixin,
    ItemRequestMixin,
    EquipmentGridMixin,
    EnergySourceMixin,
    OrientationMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector, PrimitiveIntVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import get_first

from draftsman.data.entities import cars

import attrs
from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


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
