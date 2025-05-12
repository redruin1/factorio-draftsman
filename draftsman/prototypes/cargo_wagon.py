# cargo_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EquipmentGridMixin,
    ItemRequestMixin,
    FilteredInventoryMixin,
    OrientationMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import cargo_wagons

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class CargoWagon(
    EquipmentGridMixin,
    ItemRequestMixin,
    FilteredInventoryMixin,
    OrientationMixin,
    Entity,
):
    """
    A train wagon that holds items as cargo.
    """

    # TODO: check for item requests exceeding cargo capacity

    @property
    def similar_entities(self) -> list[str]:
        return cargo_wagons

    # =========================================================================

    __hash__ = Entity.__hash__
