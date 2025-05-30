# lab.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ModulesMixin, ItemRequestMixin, EnergySourceMixin
from draftsman.constants import Inventory
from draftsman.signatures import ModuleName, QualityName

from draftsman.data.entities import labs
from draftsman.data import entities

import attrs
from typing import Iterable, Optional


@attrs.define
class Lab(ModulesMixin, ItemRequestMixin, EnergySourceMixin, Entity):
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
        Not exported; read only.
        """
        return entities.raw.get(self.name, {"inputs": None})["inputs"]

    # =========================================================================

    # TODO: in a perfect world
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
        return entities.get_allowed_effects(self.name, default=entities.ALL_EFFECTS_EXCEPT_QUALITY)

    # =========================================================================

    def request_modules(
        self,
        module_name: ModuleName,
        slots: int | Iterable[int],
        quality: QualityName = "normal",
    ):
        return super().request_modules(
            Inventory.lab_modules, module_name, slots, quality
        )

    # =========================================================================

    __hash__ = Entity.__hash__

