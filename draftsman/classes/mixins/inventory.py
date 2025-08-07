# inventory.py

from draftsman import DEFAULT_FACTORIO_VERSION
from draftsman.classes.exportable import Exportable
from draftsman.data import entities, mods, qualities
from draftsman.constants import InventoryType, ValidationMode
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    ensure_bar_less_than_inventory_size,
    uint16,
)
from draftsman.utils import calculate_occupied_slots
from draftsman.validators import and_, conditional, instance_of, try_convert
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
        Returns ``None`` if this entity is not recognized by Draftsman.
        """
        if mods.versions.get("base", DEFAULT_FACTORIO_VERSION) < (2, 0):
            # "enable_inventory_bar"
            return entities.raw.get(self.name, {}).get("enable_inventory_bar", True)
        else:
            # "inventory_type"
            inventory_type = entities.raw.get(self.name, {}).get(
                "inventory_type", "with_bar"
            )
            return inventory_type in ("with_bar", "with_filters_and_bar")

    # =========================================================================

    @property
    def quality_affects_inventory_size(self) -> Optional[bool]:
        """
        Whether or not the :py:attr:`.quality` of this entity modifies its
        inventory size.
        """
        return entities.raw.get(
            self.name, {"quality_affects_inventory_size": None}
        ).get("quality_affects_inventory_size", True)

    # =========================================================================

    @property
    def size(self) -> Optional[uint16]:
        """
        The number of inventory slots that this entity has.
        If :py:attr:`quality_affects_inventory_size` is ``True`` for this entity,
        then the returned value is scaled by the :py:attr:`quality` of the
        entity. If the current quality of this entity is unrecognized by the
        current environment, then the base, un-scaled inventory size is
        returned.

        If this entity is unrecognized by the current environment, this
        attribute returns ``None``.
        """
        inventory_size = entities.raw.get(self.name, {}).get("inventory_size", None)
        if inventory_size is None or not self.quality_affects_inventory_size:
            return inventory_size
        multiplier = 0.3 * qualities.raw.get(self.quality, {"level": 0})["level"]
        return math.floor(inventory_size + inventory_size * multiplier)

    # =========================================================================

    @property
    def slots_occupied(self) -> int:
        """
        The number of inventory slots filled by the item requests for this
        entity. Useful for quickly determining the capacity of the chest after
        the item requests have been delivered.
        """
        return calculate_occupied_slots(self.item_requests, InventoryType.chest)

    # =========================================================================

    bar: Optional[uint16] = attrs.field(
        default=None,
        converter=try_convert(int),
        validator=and_(
            instance_of(Optional[uint16]),
            ensure_bar_less_than_inventory_size,
        ),
        metadata={"never_null": True},
    )
    """
    .. serialized::

        This attribute is imported/exported from blueprint strings.
    
    The limiting bar of the inventory. Used to prevent the final-most
    slots in the inventory from accepting new items.

    Raises :py:class:`~draftsman.warning.IndexWarning` if the set value
    exceeds the Entity's ``inventory_size`` attribute.
    """

    @bar.validator
    @conditional(ValidationMode.STRICT)
    def _bar_validator(self, _: attrs.Attribute, value: Optional[uint16]):
        """
        Ensure this entity has a bar that can be controlled.
        """
        if self.inventory_bar_enabled is False and value is not None:
            msg = "This entity does not have bar control"
            warnings.warn(BarWarning(msg))

    # =========================================================================

    def merge(self, other: "Entity"):
        super().merge(other)

        self.bar = other.bar


draftsman_converters.add_hook_fns(
    InventoryMixin,
    lambda fields: {"bar": fields.bar.name},
)
