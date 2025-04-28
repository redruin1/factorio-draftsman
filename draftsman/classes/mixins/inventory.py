# inventory.py

from draftsman.data import entities, items
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.constants import ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    DraftsmanBaseModel,
    ensure_bar_less_than_inventory_size,
    uint16,
    uint32,
)
from draftsman.validators import and_, instance_of
from draftsman.warning import BarWarning, IndexWarning, ItemCapacityWarning

import attrs
import math
from pydantic import Field, ValidationInfo, field_validator
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

    class Format(DraftsmanBaseModel):
        bar: Optional[uint16] = Field(
            None,
            description="""
            Limiting bar on this entity's inventory.
            """,
        )

        @field_validator("bar")
        @classmethod
        def ensure_inventory_bar_enabled(
            cls, bar: Optional[uint16], info: ValidationInfo
        ):
            if not info.context or bar is None:
                return bar
            if info.context["mode"] <= ValidationMode.MINIMUM:
                return bar

            warning_list: list = info.context["warning_list"]
            entity: InventoryMixin = info.context["object"]

            # Make sure to check that it's `False`; this attribute can return
            # `None` if it doesn't recognize the entity, and in that case we
            # don't want to issue a warning at all
            if entity.inventory_bar_enabled is False:
                warning_list.append(BarWarning("This entity does not have bar control"))

            return bar

        @field_validator("bar")
        @classmethod
        def ensure_less_than_inventory_size(
            cls, bar: Optional[uint16], info: ValidationInfo
        ):
            return ensure_bar_less_than_inventory_size(cls, bar, info)

    # def __init__(self, name, similar_entities, **kwargs):
    #     self._root: __class__.Format

    #     # self._inventory_slots_occupied = 0

    #     super().__init__(name, similar_entities, **kwargs)

    #     self._root.bar = kwargs.get("bar", None)

    # =========================================================================

    @property
    def inventory_bar_enabled(self) -> Optional[bool]:
        """
        Whether or not this Entity has its inventory limiting bar enabled.
        Equivalent to the ``"enable_inventory_bar"`` key in Factorio's
        ``data.raw``, or ``True`` if not present. Returns ``None`` if this
        entity is not recognized by Draftsman. Not exported; read only.
        """
        return entities.raw.get(self.name, {"enable_inventory_bar": None}).get(
            "enable_inventory_bar", True
        )

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
        entity. Used to keep track of requested items and issue warnings if the
        amount inside the container exceeds the inventory size of the entity.
        Requested items that are not recognized by Draftsman are not added to
        this total, since it cannot deduce their stack size. Not exported; read
        only.
        """
        # TODO: this grabs every item, which in some cases like furnaces is
        # undesireable, since the fuel we can request to those entities goes to
        # a different inventory that should not affect this one
        # I believe the best course of action would be to store a private
        # `container_items` object alonside `items` which would only contain
        # these specific items; subclasses could then implement `fuel_items`,
        # `module_items`, etc. and keep them up to date alongside `items`
        return sum(
            int(math.ceil(count / float(items.raw[item]["stack_size"])))
            for item, count in self.items.items()
            if item in items.raw
        )

    # =========================================================================

    def _check_bar_enabled(self, attr, value, mode=None):
        mode = mode if mode is not None else self.validate_assignment
        if mode >= ValidationMode.STRICT:
            # Make sure to check that it's `False`; this attribute can return
            # `None` if it doesn't recognize the entity, and in that case we
            # don't want to issue a warning at all
            if self.inventory_bar_enabled is False:
                msg = "This entity does not have bar control"
                warnings.warn(BarWarning(msg))

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

    def set_item_request(self, item: str, count: uint32):  # TODO: ItemID
        """
        Issues warnings if the set item exceeds the inventory size of the entity.
        """
        # if item in items.raw:
        #     stack_size = items.raw[item]["stack_size"]
        #     num_slots_add = int(math.ceil(count / float(stack_size)))
        #     num_slots_old = int(math.ceil(self.items.get(item, 0) / float(stack_size)))

        #     self._inventory_slots_occupied -= num_slots_old
        #     self._inventory_slots_occupied += num_slots_add

        super().set_item_request(item, count)

        # TODO: move this into validator function for "items"
        if self.inventory_slots_occupied > self.inventory_size:
            warnings.warn(
                "Current item requests exceeds the inventory size of this entity",
                ItemCapacityWarning,
                stacklevel=2,
            )

    # =========================================================================

    def merge(self, other: "Entity"):
        super().merge(other)

        self.bar = other.bar

    # =========================================================================

    def __eq__(self, other) -> bool:
        return super().__eq__(other) and self.bar == other.bar


draftsman_converters.add_schema(
    {"$id": "factorio:inventory_mixin"},
    InventoryMixin,
    lambda fields: {"bar": fields.bar.name},
)
