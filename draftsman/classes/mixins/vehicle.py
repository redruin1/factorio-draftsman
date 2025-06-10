# vehicle.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import FilteredInventory, uint16, uint32
from draftsman.validators import and_, instance_of

from draftsman.data import entities, qualities

import attrs
import math
from typing import Optional
import weakref


def _trunk_inventory_size(entity) -> Optional[uint16]:
    """
    Number of trunk inventory slots that this vehicle has. Returns ``None``
    if this entity is not recognized by Draftsman.
    """
    inventory_size = entities.raw.get(entity.name, {"inventory_size": None})[
        "inventory_size"
    ]
    if inventory_size is None:
        return None
    modifier = 0.3 * qualities.raw.get(entity.quality, {"level": 0})["level"]
    return math.floor(inventory_size + inventory_size * modifier)


def _ammo_inventory_size(entity) -> Optional[uint16]:
    """
    Number of ammo slots that this vehicle has. Returns ``None`` if this
    entity is not recognized by Draftsman.
    """
    guns = entities.raw.get(entity.name, {"guns": None})["guns"]
    return len(guns) if guns is not None else guns


@attrs.define(slots=False)
class VehicleMixin(Exportable):
    """
    A number of common properties that all vehicles have.
    """

    trunk_inventory: Optional[FilteredInventory] = attrs.field(
        # factory=FilteredInventory,
        converter=FilteredInventory.converter,
        validator=and_(
            instance_of(Optional[FilteredInventory]),
            lambda self, _, value: value._set_parent(
                self, self.ammo_inventory, _trunk_inventory_size
            ),
        ),
    )
    """
    Inventory object which encodes slot filters for the main inventory of the
    vehicle.
    """

    @trunk_inventory.default
    def _(self):
        return FilteredInventory()._set_parent(self, None, _trunk_inventory_size)

    # =========================================================================

    ammo_inventory: Optional[FilteredInventory] = attrs.field(
        # factory=FilteredInventory,
        converter=FilteredInventory.converter,
        validator=and_(
            instance_of(Optional[FilteredInventory]),
            lambda self, _, value: value._set_parent(
                self, self.ammo_inventory, _ammo_inventory_size
            ),
        ),
    )
    """
    Inventory object which encodes slot filters for the ammunition slots of the
    vehicle. Setting the :py:attr:`~.FilteredInventory.bar` of this inventory 
    has no effect.
    """

    @ammo_inventory.default
    def _(self):
        return FilteredInventory()._set_parent(self, None, _ammo_inventory_size)

    # =========================================================================

    driver_is_main_gunner: bool = attrs.field(
        default=False, validator=instance_of(bool)
    )
    """
    Whether or not the driver or the passenger has control of the vehicle's 
    weapons.
    """

    # =========================================================================

    selected_gun_index: uint32 = attrs.field(default=1, validator=instance_of(uint32))
    """
    Which gun is currently selected by the gunner. Defaults to ``1`` for 
    vehicles with only one gun.
    """


draftsman_converters.add_hook_fns(
    VehicleMixin,
    lambda fields: {
        "trunk_inventory": fields.trunk_inventory.name,
        "ammo_inventory": fields.ammo_inventory.name,
        "driver_is_main_gunner": fields.driver_is_main_gunner.name,
        "selected_gun_index": fields.selected_gun_index.name,
    },
)
