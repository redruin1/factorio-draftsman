# locomotive.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EquipmentGridMixin,
    RequestItemsMixin,
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
    RequestItemsMixin,
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


draftsman_converters.get_version((1, 0)).add_schema(
    {"$id": "factorio:locomotive_v1.0"},
    Locomotive,
    lambda fields: {
        None: fields.equipment.name,
        None: fields.enable_logistics_while_moving.name,
    },
)
