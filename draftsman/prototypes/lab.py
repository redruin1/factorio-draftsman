# lab.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ModulesMixin, EnergySourceMixin
from draftsman.constants import InventoryType
from draftsman.signatures import QualityID

from draftsman.data.entities import labs
from draftsman.data import entities, modules

import attrs
from typing import Iterable, Optional


@attrs.define
class Lab(ModulesMixin, EnergySourceMixin, Entity):
    """
    An entity that consumes items and produces research.
    """

    @property
    def similar_entities(self) -> list[str]:
        return labs

    # =========================================================================

    @property
    def inputs(self) -> Optional[list[str]]:
        """
        The inputs that this Lab uses to research, listed in their Factorio
        order. Returns ``None`` if this entity is not recognized by Draftsman.
        """
        return entities.raw.get(self.name, {"inputs": None})["inputs"]

    # =========================================================================

    @property
    def module_slots_occupied(self) -> int:
        return len(
            {
                inv_pos.stack
                for req in self.item_requests
                if req.id.name in modules.raw
                for inv_pos in req.items.in_inventory
                if inv_pos.inventory == InventoryType.LAB_MODULES
            }
        )

    # =========================================================================

    # TODO: should be evolve
    # item_requests = attrs.fields(ItemRequestMixin).item_requests.reuse()

    # @item_requests.validator()
    # @conditional(ValidationMode.STRICT)
    # def ensure_name_recognized(self, attr, value):
    #     # TODO: check the lab's limitations to see if the module is allowed
    #     # ('allowed_effects')
    #     # This is all for regular labs, but not necessarily modded ones.
    #     if item not in modules.raw and item not in self.inputs:
    #         warnings.warn(
    #             "Item '{}' cannot be placed in Lab '{}'".format(item, self.name),
    #             ItemLimitationWarning,
    #             stacklevel=2,
    #         )

    # =========================================================================

    @property
    def allowed_effects(self) -> Optional[set[str]]:
        return entities.get_allowed_effects(
            self.name, default=entities.ALL_EFFECTS_EXCEPT_QUALITY
        )

    # =========================================================================

    def request_modules(
        self,
        module_name: str,  # TODO: should be ModuleID
        slots: int | Iterable[int],
        quality: QualityID = "normal",
    ):
        return super().request_modules(
            InventoryType.LAB_MODULES, module_name, slots, quality
        )

    # =========================================================================

    __hash__ = Entity.__hash__
