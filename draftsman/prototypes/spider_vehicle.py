# spider_vehicle.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    VehicleMixin,
    EquipmentGridMixin,
    RequestFiltersMixin,
    ColorMixin,
    EnergySourceMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Color
from draftsman.utils import attrs_reuse
from draftsman.validators import instance_of

from draftsman.data.entities import spider_vehicles

import attrs


@attrs.define
class SpiderVehicle(
    VehicleMixin,
    EquipmentGridMixin,
    RequestFiltersMixin,
    ColorMixin,
    EnergySourceMixin,
    # OrientationMixin, # Don't think there actually is an orientation here
    Entity,
):
    """
    .. versionadded:: 3.0.0 (Factorio 2.0)

    A drivable entity which can move in any direction at once.
    """

    @property
    def similar_entities(self) -> list[str]:
        return spider_vehicles

    # =========================================================================

    color = attrs_reuse(
        attrs.fields(ColorMixin).color,
        factory=lambda: Color(r=255 / 255, g=127 / 255, b=0.0, a=127 / 255),
    )

    # =========================================================================

    auto_target_without_gunner: bool = attrs.field(
        default=True, validator=instance_of(bool)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this spidertron should automatically target enemies when
    there is no passenger in the vehicle.
    """

    # =========================================================================

    auto_target_with_gunner: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.

    Whether or not this spidertron should automatically target enemies when
    there is a passenger in the vehicle.
    """

    # =========================================================================

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    SpiderVehicle,
    lambda fields: {
        (
            "automatic_targeting_parameters",
            "auto_target_without_gunner",
        ): fields.auto_target_without_gunner.name,
        (
            "automatic_targeting_parameters",
            "auto_target_with_gunner",
        ): fields.auto_target_with_gunner.name,
    },
)
