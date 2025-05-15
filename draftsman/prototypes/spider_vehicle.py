# spider_vehicle.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    VehicleMixin,
    EquipmentGridMixin,
    RequestFiltersMixin,
    ItemRequestMixin,
    ColorMixin,
    EnergySourceMixin,
    OrientationMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import AttrsColor
from draftsman.validators import instance_of

from draftsman.data.entities import spider_vehicles

import attrs
from typing import Optional


@attrs.define
class SpiderVehicle(
    VehicleMixin,
    EquipmentGridMixin,
    RequestFiltersMixin,
    ItemRequestMixin,
    ColorMixin,
    EnergySourceMixin,
    # OrientationMixin, # Don't think there actually is an orientation here
    Entity,
):
    """
    A drivable entity which can move in any direction at once.
    """

    @property
    def similar_entities(self) -> list[str]:
        return spider_vehicles

    # =========================================================================

    # TODO: just want to evolve the default
    color: Optional[AttrsColor] = attrs.field(
        factory=lambda: AttrsColor(r=255 / 255, g=127 / 255, b=0.0, a=127 / 255),
        converter=AttrsColor.converter,
        validator=instance_of(Optional[AttrsColor]),
    )

    # =========================================================================

    auto_target_without_gunner: bool = attrs.field(
        default=True, validator=instance_of(bool)
    )
    """
    Whether or not this spidertron should automatically target enemies when
    there is no passenger in the vehicle.
    """

    # =========================================================================

    auto_target_with_gunner: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not this spidertron should automatically target enemies when
    there is a passenger in the vehicle.
    """

    # =========================================================================

    __hash__ = Entity.__hash__


SpiderVehicle.add_schema(None, version=(1, 0))

SpiderVehicle.add_schema(
    {
        "$id": "urn:factorio:entity:spider-vehicle",
        "properties": {
            "automatic_targeting_parameters": {
                "type": "object",
                "parameters": {
                    "auto_target_without_gunner": {
                        "type": "boolean",
                        "default": "true",
                    },
                    "auto_target_with_gunner": {"type": "boolean", "default": "false"},
                },
            }
        },
    }
)


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
