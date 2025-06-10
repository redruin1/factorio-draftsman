# modules.py

from draftsman.data import entities, modules
from .item_requests import ItemRequestMixin
from draftsman.signatures import (
    BlueprintInsertPlan,
    ItemID,
    ItemInventoryPositions,
    InventoryPosition,
    ModuleID,
    QualityID,
    uint32,
)
from draftsman.warning import ModuleCapacityWarning, ModuleNotAllowedWarning

from typing import Iterable, Optional


class ModulesMixin(ItemRequestMixin):
    """
    (Implicitly inherits :py:class:`~.ItemRequestMixin`)

    Allows the entity to have modules, and keep track of the amount of modules
    currently inside the entity.
    """

    @property
    def total_module_slots(self) -> int:
        """
        The total number of module slots in the Entity. Returns ``None`` if this
        entity's name is not recognized by Draftsman. Not exported; read only.
        """
        return entities.raw.get(self.name, {"module_slots": None}).get(
            "module_slots", 0
        )

    # =========================================================================

    @property
    def module_slots_occupied(self) -> int:
        """
        The total number of module slots that are currently taken by inserted
        modules. Not exported; read only.
        """
        return sum(
            [v for k, v in self.item_requests if k in modules.raw]
        )  # TODO: FIXME

    # =========================================================================

    @property
    def allowed_effects(self) -> Optional[set[str]]:
        """
        A set of all effect modifiers that this entity supports via modules and
        beacons. Returns ``None`` if this entity's name is not recognized by
        Draftsman. Not exported; read only.
        """
        return entities.get_allowed_effects(self.name, default=entities.NO_EFFECTS)

    # =========================================================================

    @property
    def allowed_modules(self) -> Optional[set[str]]:
        """
        A list of all valid modules that can be inserted into this entity.
        Determined by the 'allowed_effects' key in the data.raw entry for this
        entity. Returns ``None`` if this entity's name is not recognized by
        Draftsman. Not exported; read only.
        """
        return modules.get_modules_from_effects(self.allowed_effects, None)

    # =========================================================================

    def request_modules(
        self,
        inventory_id: uint32,
        module_name: ModuleID,
        slots: int | Iterable[int],
        quality: QualityID = "normal",
    ):
        """
        Loads module ``module_name`` into the slot specified by ``slots``, or
        multiple slots if ``slots`` is instead an iterable of integers.

        :param module_name: The name of the module to request to this entity.
        :param slots: The slots to request this module to.
        :param quality: The quality of the module to request.
        """
        if isinstance(slots, int):
            slots = (slots,)

        # Iterate over existing item requests
        existing_request = None
        for item_request in self.item_requests:
            item_request: BlueprintInsertPlan
            # If we already request this module elsewhere, reuse this item
            # request object
            if (
                item_request.id.name == module_name
                and item_request.id.quality == quality
            ):
                existing_request = item_request

            # Delete any slots that we want to write to that are occupied by
            # other modules
            item_request.items.in_inventory = [
                location
                for location in item_request.items.in_inventory
                if location.stack not in slots
            ]

        # Trim item requests which now point to zero slots
        self.item_requests = [
            item_request
            for item_request in self.item_requests
            if len(item_request.items.in_inventory) != 0
        ]

        if existing_request:
            # TODO: does this trigger validation?
            existing_request.items.in_inventory += [
                InventoryPosition(inventory=inventory_id, count=1, stack=slot)
                for slot in slots
            ]
        else:
            # TODO: does this trigger validation?
            self.item_requests.append(
                BlueprintInsertPlan(
                    id=ItemID(name=module_name, quality=quality),
                    items=ItemInventoryPositions(
                        in_inventory=[
                            InventoryPosition(
                                inventory=inventory_id, count=1, stack=slot
                            )
                            for slot in slots
                        ]
                    ),
                )
            )
