# lab.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ModulesMixin, ItemRequestMixin, EnergySourceMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import get_first, reissue_warnings
from draftsman.warning import ItemLimitationWarning

from draftsman.data.entities import labs
from draftsman.data import entities, modules

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union
import warnings


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
    # item_requests = attrs.fields(ItemRequestMixin).item_requests.to_field()

    # @item_requests.validator()
    # def ensure_name_recognized(self, attr, value, mode=None):
    #     ...

    # =========================================================================

    # @reissue_warnings
    # def set_item_request(self, item: str, count: Optional[uint32]):  # TODO: ItemID
    #     super().set_item_request(item, count)

    #     # TODO: check the lab's limitations to see if the module is allowed
    #     # ('allowed_effects')
    #     # This is all for regular labs, but not necessarily modded ones.
    #     if item not in modules.raw and item not in self.inputs:
    #         warnings.warn(
    #             "Item '{}' cannot be placed in Lab '{}'".format(item, self.name),
    #             ItemLimitationWarning,
    #             stacklevel=2,
    #         )

    #     # TODO: check the amount of the science pack passed in; if its greater
    #     # than 1 stack issue an ItemCapacityWarning
    #     # Note that this asserts that each lab can only contain 1 stack of each
    #     # science pack it consumes, which might change in a future Factorio
    #     # version.

    # =========================================================================

    __hash__ = Entity.__hash__
