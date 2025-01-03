# modules.py

from draftsman.constants import ValidationMode
from draftsman.data import entities, modules
from draftsman.signatures import uint32
from draftsman.warning import ModuleCapacityWarning, ModuleNotAllowedWarning

from pydantic import BaseModel, ValidationInfo, field_validator
from typing import Optional


class ModulesMixin:  # (RequestItemsMixin)
    """
    (Implicitly inherits :py:class:`~.RequestItemsMixin`)

    Allows the entity to have modules, and keep track of the amount of modules
    currently inside the entity.
    """

    class Format(BaseModel):
        # @field_validator("items", check_fields=False) # TODO: reimplement
        # @classmethod
        # def ensure_not_too_many_modules(
        #     cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        # ):
        #     if not info.context or value is None:
        #         return value
        #     if info.context["mode"] <= ValidationMode.MINIMUM:
        #         return value

        #     entity: "ModulesMixin" = info.context["object"]
        #     warning_list: list = info.context["warning_list"]

        #     if entity.total_module_slots is None:  # entity not recognized
        #         return value
        #     # if entity.total_module_slots == 0:  # Better warning issued elsewhere (where?)
        #     #     return value

        #     if entity.module_slots_occupied > entity.total_module_slots:
        #         warning_list.append(
        #             ModuleCapacityWarning(
        #                 "Current number of module slots used ({}) greater than max module capacity ({}) for entity '{}'".format(
        #                     entity.module_slots_occupied,
        #                     entity.total_module_slots,
        #                     entity.name,
        #                 )
        #             )
        #         )

        #     return value

        # @field_validator("items", check_fields=False) # TODO: reimplement
        # @classmethod
        # def ensure_module_type_matches_entity(
        #     cls, value: Optional[dict[str, uint32]], info: ValidationInfo
        # ):
        #     if not info.context or value is None:
        #         return value
        #     if info.context["mode"] <= ValidationMode.MINIMUM:
        #         return value

        #     entity: "ModulesMixin" = info.context["object"]
        #     warning_list: list = info.context["warning_list"]

        #     if entity.allowed_modules is None:  # entity not recognized
        #         return value

        #     for item in entity.module_items:
        #         if item not in entity.allowed_modules:
        #             if (
        #                 entity.allowed_modules is not None
        #                 and len(entity.allowed_modules) > 0
        #             ):
        #                 reason_string = "allowed modules are {}".format(
        #                     entity.allowed_modules
        #                 )
        #             else:
        #                 reason_string = "this machine does not accept modules"

        #             warning_list.append(
        #                 ModuleNotAllowedWarning(
        #                     "Cannot add module '{}' to '{}'; {}".format(
        #                         item, entity.name, reason_string
        #                     )
        #                 )
        #             )

        #     return value
        pass

    def __init__(self, name: str, similar_entities: list[str], **kwargs):
        # Keep track of the current module slots currently used
        # self._module_slots_occupied = 0
        # self.module_items = {}

        super(ModulesMixin, self).__init__(name, similar_entities, **kwargs)

    # =========================================================================

    @property
    def total_module_slots(self) -> int:
        """
        The total number of module slots in the Entity. Returns ``None`` if this
        entity's name is not recognized by Draftsman. Not exported; read only.
        """
        # If not recognized, return None
        # If recognized, but no module specification, then return 0
        # return entities.raw.get(
        #     self.name, {"module_specification": {"module_slots": None}}
        # ).get("module_specification", {"module_slots": 0})["module_slots"]
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
        return sum([v for k, v in self.items if k in modules.raw])  # TODO: FIXME

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
        # return entities.raw.get(self.name, {"allowed_module_categories": []})["allowed_module_categories"]

    # =========================================================================

    @property
    def module_items(self) -> dict[str, uint32]:  # TODO: ItemID
        """
        The subset of :py:attr:`.items` where each key is a known module
        currently requested to this entity. Returns an empty dict if none of
        the keys of ``items`` are known as valid module names. Not exported;
        read only.
        """
        return {k: v for k, v in self.items.items() if k in modules.raw}
