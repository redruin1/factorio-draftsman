# cargo_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EquipmentGridMixin,
    OrientationMixin,
)
from draftsman.serialization import draftsman_converters
from draftsman.signatures import Inventory, uint16
from draftsman.validators import and_, instance_of

from draftsman.data.entities import cargo_wagons
from draftsman.data import entities, qualities

import attrs
import math
from typing import Optional


def _cargo_wagon_inventory_size(entity: "CargoWagon") -> Optional[uint16]:
    """
    Gets the inventory size of this cargo wagon.
    """
    inventory_size = entities.raw.get(entity.name, {"inventory_size": None})[
        "inventory_size"
    ]
    if inventory_size is None:
        return None
    if not entities.raw[entity.name].get("quality_affects_inventory_size", False):
        return inventory_size
    modifier = 0.3 * qualities.raw.get(entity.quality, {"level": 0})["level"]
    return math.floor(inventory_size + inventory_size * modifier)


@attrs.define
class CargoWagon(
    EquipmentGridMixin,
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

    inventory: Optional[Inventory] = attrs.field(
        validator=and_(
            instance_of(Optional[Inventory]),
            lambda self, _, value, **kwargs: value._set_parent(
                self, self.inventory, _cargo_wagon_inventory_size
            ),
        ),
    )
    """
    Inventory object of this cargo wagon. Holds metadata associated with this
    wagons inventory, such as it's size, limiting bar position, and item filters
    (if any).
    """

    @inventory.default
    def _(self) -> Inventory:
        return Inventory()._set_parent(self, None, _cargo_wagon_inventory_size)

    # =========================================================================

    def merge(self, other: "CargoWagon"):
        super().merge(other)

        self.inventory = other.inventory

    __hash__ = Entity.__hash__


draftsman_converters.add_hook_fns(
    CargoWagon,
    lambda fields: {
        "inventory": fields.inventory.name,
    },
)
