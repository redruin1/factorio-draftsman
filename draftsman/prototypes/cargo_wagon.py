# cargo_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EquipmentGridMixin,
    ItemRequestMixin,
    FilteredInventoryMixin,
    OrientationMixin,
)

from draftsman.data.entities import cargo_wagons

import attrs


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


CargoWagon.add_schema(
    {
        "$id": "urn:factorio:entity:cargo-wagon",
    },
    version=(1, 0),
    mro=(ItemRequestMixin, FilteredInventoryMixin, OrientationMixin, Entity),
)

CargoWagon.add_schema({"$id": "urn:factorio:entity:cargo-wagon"}, version=(2, 0))
