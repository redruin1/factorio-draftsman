# inventory.py

from draftsman.classes.exportable import Exportable
from draftsman.data import entities, mods
from draftsman.constants import Inventory, ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    ensure_bar_less_than_inventory_size,
    uint16,
)
from draftsman.utils import calculate_occupied_slots
from draftsman.validators import and_, conditional, instance_of
from draftsman.warning import BarWarning

import attrs

import math
import warnings

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


@attrs.define(slots=False)
class InventoryMixin(Exportable):
    """
    Enables the entity to have inventory control. Keeps track of the currently
    requested items for this entity and issues warnings if the requested items
    amount exceeds the inventory size of the entity.
    """

    @property
    def inventory_bar_enabled(self) -> Optional[bool]:
        """
        Whether or not this Entity has its inventory limiting bar enabled.
        Returns ``None`` if this entity is not recognized by Draftsman. Not
        exported; read only.
        """
        if mods.versions["base"] < (2, 0):  # pragma: no coverage
            # "enable_inventory_bar"
            return entities.raw.get(self.name, {"enable_inventory_bar": None}).get(
                "enable_inventory_bar", True
            )
        else:
            # "inventory_type"
            inventory_type = entities.raw.get(self.name, {"inventory_type": None}).get(
                "inventory_type", "with_bar"
            )
            if inventory_type is None:
                return None
            return inventory_type in ("with_bar", "with_filters_and_bar")

    # =========================================================================

    @property
    def quality_affects_inventory_size(self) -> Optional[bool]:
        """
        Whether or not the quality of this entity modifies its inventory size.
        Not exported; read only.
        """
        return entities.raw.get(
            self.name, {"quality_affects_inventory_size": None}
        ).get("quality_affects_inventory_size", True)

    # =========================================================================

    @property
    def inventory_size(self) -> uint16:
        """
        The number of inventory slots that this Entity has. Equivalent to the
        ``"inventory_size"`` key in Factorio's ``data.raw``. Returns ``None`` if
        this entity's name is not recognized by Draftsman. Not exported; read
        only.
        """
        inventory_size = entities.raw.get(self.name, {}).get("inventory_size", None)
        if inventory_size is None or not self.quality_affects_inventory_size:
            return inventory_size
        else:
            mutlipliers = {  # TODO: grab this dynamically
                "normal": 1.0,
                "uncommon": 1.3,
                "rare": 1.6,
                "epic": 1.9,
                "legendary": 2.5,
            }
            return math.floor(inventory_size * mutlipliers[self.quality])

    # =========================================================================

    @property
    def inventory_slots_occupied(self) -> int:
        """
        The number of inventory slots filled by the item requests for this
        entity. Useful for quickly investigating the capacity of the chest after
        the item requests have been delivered. Not exported; read only.
        """
        return calculate_occupied_slots(self.item_requests, Inventory.chest)

    # =========================================================================

    bar: Optional[uint16] = attrs.field(
        default=None,
        validator=and_(
            instance_of(Optional[uint16]),
            ensure_bar_less_than_inventory_size,
        ),
        metadata={"never_null": True},
    )
    """
    The limiting bar of the inventory. Used to prevent the final-most
    slots in the inventory from accepting new items.

    Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
    exceeds the Entity's ``inventory_size`` attribute.

    :exception DataFormatError: If set to anything other than an ``int`` or
        ``None``.
    :exception DataFormatError: If the set value lies outside of the range
        ``[0, 65536)``.
    """

    @bar.validator
    @conditional(ValidationMode.STRICT)
    def _bar_validator(self, _: attrs.Attribute, value: uint16):
        """
        Ensure this entity has a bar that can be controlled.
        """
        if self.inventory_bar_enabled is False:
            msg = "This entity does not have bar control"
            warnings.warn(BarWarning(msg))

    # =========================================================================

    def merge(self, other: "Entity"):
        super().merge(other)

        self.bar = other.bar


InventoryMixin.add_schema(
    {"properties": {"bar": {"oneOf": [{"$ref": "urn:uint16"}, {"type": "null"}]}}}
)

draftsman_converters.add_hook_fns(
    InventoryMixin,
    lambda fields: {"bar": fields.bar.name},
)
