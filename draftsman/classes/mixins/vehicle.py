# vehicle.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import FilteredInventory, uint32
from draftsman.validators import instance_of

import attrs
from typing import Optional


@attrs.define(slots=False)
class VehicleMixin(Exportable):
    """
    A number of common properties that all vehicles have.
    """

    trunk_inventory: Optional[FilteredInventory] = attrs.field(
        default=None,
        converter=FilteredInventory.converter,
        validator=instance_of(Optional[FilteredInventory]),
    )
    """
    Inventory object which encodes slot filters for the main inventory of the
    vehicle.
    """

    # =========================================================================

    ammo_inventory: Optional[FilteredInventory] = attrs.field(
        default=None,
        converter=FilteredInventory.converter,
        validator=instance_of(Optional[FilteredInventory]),
    )
    """
    Inventory object which encodes slot filters for the ammunition slots of the
    vehicle.
    """

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
