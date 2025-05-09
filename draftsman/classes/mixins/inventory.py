# inventory.py

from draftsman.data import entities, mods
from draftsman.constants import Inventory, ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    ensure_bar_less_than_inventory_size,
    uint16,
    uint32,
)
from draftsman.utils import calculate_occupied_slots
from draftsman.validators import and_, instance_of
from draftsman.warning import BarWarning, IndexWarning, ItemCapacityWarning

import attrs

import math
import warnings

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no coverage
    from draftsman.classes.entity import Entity


@attrs.define(slots=False)
class InventoryMixin:
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

    def _check_bar_enabled(
        self, attr, value, mode=None, warning_list: Optional[list] = None
    ):
        mode = mode if mode is not None else self.validate_assignment
        if mode >= ValidationMode.STRICT:
            # Make sure to check that it's `False`; this attribute can return
            # `None` if it doesn't recognize the entity, and in that case we
            # don't want to issue a warning at all
            if self.inventory_bar_enabled is False:
                msg = "This entity does not have bar control"
                if warning_list is None:
                    warnings.warn(BarWarning(msg))
                else:
                    warning_list.append(BarWarning(msg))

    bar: Optional[uint16] = attrs.field(
        default=None,
        validator=and_(
            instance_of(Optional[uint16]),
            ensure_bar_less_than_inventory_size,
            _check_bar_enabled,
        ),
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

    # @property
    # def bar(self) -> uint16:
    #     """
    #     The limiting bar of the inventory. Used to prevent the final-most
    #     slots in the inventory from accepting new items.

    #     Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
    #     exceeds the Entity's ``inventory_size`` attribute.

    #     :getter: Gets the bar location of the inventory.
    #     :setter: Sets the bar location of the inventory.

    #     :exception DraftsmanError: If attempting to set the bar of an Entity
    #         that has the ``inventory_bar_enabled`` attribute set to ``False``.
    #     :exception DataFormatError: If set to anything other than an ``int`` or
    #         ``None``.
    #     :exception DataFormatError: If the set value lies outside of the range
    #         ``[0, 65536)``.
    #     """
    #     return self._root.bar

    # @bar.setter
    # def bar(self, value: uint16):
    #     if self.validate_assignment:
    #         result = attempt_and_reissue(
    #             self, type(self).Format, self._root, "bar", value
    #         )
    #         self._root.bar = result
    #     else:
    #         self._root.bar = value

    # =========================================================================

    # def set_item_request(self, item: str, count: uint32):  # TODO: ItemID
    #     """
    #     Issues warnings if the set item exceeds the inventory size of the entity.
    #     """
    #     # if item in items.raw:
    #     #     stack_size = items.raw[item]["stack_size"]
    #     #     num_slots_add = int(math.ceil(count / float(stack_size)))
    #     #     num_slots_old = int(math.ceil(self.items.get(item, 0) / float(stack_size)))

    #     #     self._inventory_slots_occupied -= num_slots_old
    #     #     self._inventory_slots_occupied += num_slots_add

    #     super().set_item_request(item, count)

    #     # TODO: move this into validator function for "items"
    #     if self.inventory_slots_occupied > self.inventory_size:
    #         warnings.warn(
    #             "Current item requests exceeds the inventory size of this entity",
    #             ItemCapacityWarning,
    #             stacklevel=2,
    #         )

    # =========================================================================

    def merge(self, other: "Entity"):
        super().merge(other)

        self.bar = other.bar


draftsman_converters.add_hook_fns(
    # {"$id": "factorio:inventory_mixin"},
    InventoryMixin,
    lambda fields: {"bar": fields.bar.name},
)
