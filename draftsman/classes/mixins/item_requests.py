# item_requests.py

from draftsman.classes.exportable import Exportable
from draftsman.serialization import draftsman_converters
from draftsman.signatures import (
    AttrsItemRequest,
    AttrsItemID,
    AttrsItemSpecification,
    AttrsInventoryLocation,
    uint32,
)
from draftsman.utils import reissue_warnings
from draftsman.validators import instance_of

import attrs
from copy import deepcopy

from typing import Literal, Optional


@attrs.define(slots=False)
class ItemRequestMixin(Exportable):
    """
    Enables an entity to request items during its construction.

    Note that this is *not* for Logistics requests such as requester and buffer
    chests (that's what
    :py:class:`~.mixins.request_filters.RequestFiltersMixin` is for).
    Instead this is for specifying additional construction components, things
    like speed modules for beacons or productivity modules for assembling
    machines.
    """

    @property  # TODO abstractproperty
    def allowed_items(self) -> Optional[set[str]]:
        pass  # return set()

    # =========================================================================

    def _items_converter(value):
        if value is None:
            return []
        elif isinstance(value, list):
            res = [None] * len(value)
            for i, elem in enumerate(value):
                res[i] = AttrsItemRequest.converter(elem)
            return res
        else:
            return value

    item_requests: list[AttrsItemRequest] = attrs.field(
        factory=list,
        converter=_items_converter,
        validator=instance_of(list[AttrsItemRequest]),
    )
    """
    A list of items to deliver to the entity. Not to be confused with logistics
    requests (which are persistent), item requests are only fulfilled once when
    the entity is first constructed. Most notably, modules are requested to
    entities with this field.

    For user-friendly ways to modify this array, see TODO and TODO.
    """

    # =========================================================================

    @reissue_warnings
    def set_item_request(
        self,
        item: str,
        count: Optional[uint32] = None,
        quality: Literal[
            "normal", "uncommon", "rare", "epic", "legendary", "any"
        ] = "normal",
        inventory: uint32 = 0,
        slot: Optional[uint32] = None,
    ):
        """
        Requests an amount of an item. Removes the item request if ``count`` is
        set to ``0`` or ``None``. Manages ``module_slots_occupied``.

        Raises a number of warnings if the requested item is mismatched for the
        type of entity you're requesting items for. For example,
        :py:class:`.ModuleLimitationWarning` will be raised when requesting an
        item that is not a module to a Beacon entity.

        :param item: The string name of the requested item.
        :param quality: The quality of the requested item.
        :param count: The desired amount of that item. If omitted a count of
            ``0`` will be assumed.
        :param inventory: The particular inventory to request this item to. If
            omitted it will default to the first (typically only) inventory.
        :param slot: The particular slot in the inventory to place the item. The
            next open slot will be chosen automatically if omitted.

        :exception TypeError: If ``item`` is anything other than a ``str``, or
            if ``count`` is anything other than an ``int`` or ``None``.
        :exception InvalidItemError: If ``item`` is not a valid item name.
        :exception ValueError: If ``count`` is less than zero.
        """
        if count is None:
            count = 0

        if count == 0:
            # TODO: better removal across multiple categories
            # (Might be better to abstract this into `remove_item_request` or similar)
            self.item_requests = [
                i_item for i_item in self.item_requests if i_item.id.name != item
            ]
        else:
            # Try to find an existing entry for `item` with the same quality
            existing_spec = next(
                filter(
                    lambda x: x.id.name == item and x.id.quality == quality,
                    self.item_requests,
                ),
                None,
            )
            if existing_spec is None:
                # If not, add a new item entry
                if slot is None:
                    slot = len(self.item_requests)
                self.item_requests += [
                    AttrsItemRequest(
                        id=AttrsItemID(name=item, quality=quality),
                        items=AttrsItemSpecification(
                            in_inventory=[
                                AttrsInventoryLocation(
                                    inventory=inventory,
                                    stack=slot,
                                    count=count,
                                )
                            ]
                        ),
                    )
                ]
            else:
                # Try to find an existing entry at the same slot in the same inventory
                # TODO: what if there's an entry, but slot is None? Do we just pick
                # the first valid entry?
                if slot is None:
                    slot = 0
                existing_slot = next(
                    filter(
                        lambda x: x.inventory == inventory and x.stack == slot,
                        existing_spec.items.in_inventory,
                    ),
                    None,
                )
                if existing_slot is None:
                    # If not, make a new one
                    existing_spec.items.in_inventory.append(
                        AttrsInventoryLocation(
                            inventory=inventory, stack=slot, count=count
                        )
                    )
                else:
                    # If so, simply modify the count
                    existing_slot.count = count

    # =========================================================================

    def merge(self, other: "ItemRequestMixin"):
        super().merge(other)

        self.item_requests = deepcopy(other.item_requests)


# TODO: versioning

ItemRequestMixin.add_schema(
    {
        "properties": {
            "items": {"type": "array", "items": {"$ref": "urn:factorio:item-request"}}
        }
    }
)

draftsman_converters.add_hook_fns(
    ItemRequestMixin,
    lambda fields: {"items": fields.item_requests.name},
)
