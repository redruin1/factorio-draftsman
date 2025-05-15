# locomotive.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EquipmentGridMixin,
    ItemRequestMixin,
    ColorMixin,
    EnergySourceMixin,
    OrientationMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsColor
from draftsman.validators import instance_of

from draftsman.data.entities import locomotives

import attrs
from typing import Optional


@attrs.define
class Locomotive(
    EquipmentGridMixin,
    ItemRequestMixin,
    ColorMixin,
    EnergySourceMixin,
    OrientationMixin,
    Entity,
):
    """
    A train car that moves other wagons around using a fuel.
    """

    @property
    def similar_entities(self) -> list[str]:
        return locomotives

    # =========================================================================

    # TODO: should be evolved
    color: Optional[AttrsColor] = attrs.field(
        default=AttrsColor(r=234 / 255, g=17 / 255, b=0, a=127 / 255),
        converter=AttrsColor.converter,
        validator=instance_of(Optional[AttrsColor]),
    )

    # =========================================================================

    __hash__ = Entity.__hash__


Locomotive.add_schema({"$id": "urn:factorio:entity:locomotive"})
