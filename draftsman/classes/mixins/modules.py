# modules.py

from draftsman.constants import ValidationMode
from draftsman.data import entities, modules
from draftsman.signatures import (
    AttrsItemRequest,
    AttrsItemSpecification,
    AttrsInventoryLocation,
    ModuleName,
    QualityName,
    uint32,
)
from draftsman.warning import ModuleCapacityWarning, ModuleNotAllowedWarning

from pydantic import BaseModel, ValidationInfo, field_validator
from typing import Iterable, Optional


class ModulesMixin:  # (RequestItemsMixin)
    """
    (Implicitly inherits :py:class:`~.RequestItemsMixin`)

    Allows the entity to have modules, and keep track of the amount of modules
    currently inside the entity.
    """

    # class Format(BaseModel):
    #     # @field_validator("items", check_fields=False) # TODO: reimplement
    #     # @classmethod
    #     # def ensure_not_too_many_modules(
    #     #     cls, value: Optional[dict[str, uint32]], info: ValidationInfo
    #     # ):
    #     #     if not info.context or value is None:
    #     #         return value
    #     #     if info.context["mode"] <= ValidationMode.MINIMUM:
    #     #         return value

    #     #     entity: "ModulesMixin" = info.context["object"]
    #     #     warning_list: list = info.context["warning_list"]

    #     #     if entity.total_module_slots is None:  # entity not recognized
    #     #         return value
    #     #     # if entity.total_module_slots == 0:  # Better warning issued elsewhere (where?)
    #     #     #     return value

    #     #     if entity.module_slots_occupied > entity.total_module_slots:
    #     #         warning_list.append(
    #     #             ModuleCapacityWarning(
    #     #                 "Current number of module slots used ({}) greater than max module capacity ({}) for entity '{}'".format(
    #     #                     entity.module_slots_occupied,
    #     #                     entity.total_module_slots,
    #     #                     entity.name,
    #     #                 )
    #     #             )
    #     #         )

    #     #     return value

    #     # @field_validator("items", check_fields=False) # TODO: reimplement
    #     # @classmethod
    #     # def ensure_module_type_matches_entity(
    #     #     cls, value: Optional[dict[str, uint32]], info: ValidationInfo
    #     # ):
    #     #     if not info.context or value is None:
    #     #         return value
    #     #     if info.context["mode"] <= ValidationMode.MINIMUM:
    #     #         return value

    #     #     entity: "ModulesMixin" = info.context["object"]
    #     #     warning_list: list = info.context["warning_list"]

    #     #     if entity.allowed_modules is None:  # entity not recognized
    #     #         return value

    #     #     for item in entity.module_items:
    #     #         if item not in entity.allowed_modules:
    #     #             if (
    #     #                 entity.allowed_modules is not None
    #     #                 and len(entity.allowed_modules) > 0
    #     #             ):
    #     #                 reason_string = "allowed modules are {}".format(
    #     #                     entity.allowed_modules
    #     #                 )
    #     #             else:
    #     #                 reason_string = "this machine does not accept modules"

    #     #             warning_list.append(
    #     #                 ModuleNotAllowedWarning(
    #     #                     "Cannot add module '{}' to '{}'; {}".format(
    #     #                         item, entity.name, reason_string
    #     #                     )
    #     #                 )
    #     #             )

    #     #     return value
    #     pass

    # def __init__(self, name: str, similar_entities: list[str], **kwargs):
    #     # Keep track of the current module slots currently used
    #     # self._module_slots_occupied = 0
    #     # self.module_items = {}

    #     super(ModulesMixin, self).__init__(name, similar_entities, **kwargs)

    # =========================================================================

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
        A list of all effect modifiers that this entity supports via modules.
        Returns ``None`` if this entity's name is not recognized by Draftsman.
        Not exported; read only.
        """
        # If name not known, return None
        entity = entities.raw.get(self.name, None)
        if entity is None:
            return None
        # If name known, but no key, then return default list
        result = entity.get(
            "allowed_effects",
            ["speed", "productivity", "consumption", "pollution", "quality"],
        )
        # Normalize single string effect to a 1-length set
        return {result} if isinstance(result, str) else set(result)

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
        module_name: ModuleName,
        slots: int | Iterable[int],
        quality: QualityName = "normal",
    ):
        """
        Loads ``count`` modules sequentially into the entity starting at slot
        ``position``.
        """
        if isinstance(slots, int):
            slots = (slots,)

        # Iterate over existing item requests
        existing_request = None
        for item_request in self.item_requests:
            item_request: AttrsItemRequest
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
                AttrsInventoryLocation(inventory=inventory_id, count=1, stack=slot)
                for slot in slots
            ]
        else:
            # TODO: does this trigger validation?
            self.item_requests.append(
                AttrsItemRequest(
                    id={"name": module_name, "quality": quality},
                    items=AttrsItemSpecification(
                        in_inventory=[
                            AttrsInventoryLocation(
                                inventory=inventory_id, count=1, stack=slot
                            )
                            for slot in slots
                        ]
                    ),
                )
            )
