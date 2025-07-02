# locomotive.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EquipmentGridMixin,
    ColorMixin,
    EnergySourceMixin,
    OrientationMixin,
)
from draftsman.signatures import Color
from draftsman.utils import fix_incorrect_pre_init
from draftsman.validators import instance_of

from draftsman.data.entities import locomotives

import attrs
from typing import Optional


@fix_incorrect_pre_init
@attrs.define
class Locomotive(
    EquipmentGridMixin,
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

    # TODO: should be evolve
    color: Optional[Color] = attrs.field(
        default=Color(r=234 / 255, g=17 / 255, b=0, a=127 / 255),
        converter=Color.converter,
        validator=instance_of(Optional[Color]),
    )

    # =========================================================================

    __hash__ = Entity.__hash__
