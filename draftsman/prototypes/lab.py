# lab.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import ModulesMixin, RequestItemsMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.signatures import ItemRequest, uint32
from draftsman.utils import get_first, reissue_warnings
from draftsman.warning import ItemLimitationWarning

from draftsman.data.entities import labs
from draftsman.data import entities, modules

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union
import warnings


@attrs.define
class Lab(ModulesMixin, RequestItemsMixin, Entity):
    """
    An entity that consumes items and produces research.
    """

    # class Format(
    #     ModulesMixin.Format,
    #     RequestItemsMixin.Format,
    #     Entity.Format,
    # ):
    #     model_config = ConfigDict(title="Lab")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(labs),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     items: Optional[list[ItemRequest]] = [],  # TODO: ItemID
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     """
    #     TODO
    #     """

    #     super().__init__(
    #         name,
    #         labs,
    #         position=position,
    #         tile_position=tile_position,
    #         items=items,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return labs

    # =========================================================================

    @property
    def inputs(self) -> Optional[list[str]]:
        """
        The inputs that this Lab uses to research, ordered by their Factorio
        order. Returns ``None`` if this entity is not recognized by Draftsman.
        Not exported; read only.
        """
        return entities.raw.get(self.name, {"inputs": None})["inputs"]

    # =========================================================================

    # @property # TODO
    # def allowed_items(self) -> Optional[set[str]]:
    #     return {module_name for module_name in modules.raw}

    # =========================================================================

    @reissue_warnings
    def set_item_request(self, item: str, count: Optional[uint32]):  # TODO: ItemID
        super().set_item_request(item, count)

        # TODO: check the lab's limitations to see if the module is allowed
        # ('allowed_effects')
        # This is all for regular labs, but not necessarily modded ones.
        if item not in modules.raw and item not in self.inputs:
            warnings.warn(
                "Item '{}' cannot be placed in Lab '{}'".format(item, self.name),
                ItemLimitationWarning,
                stacklevel=2,
            )

        # TODO: check the amount of the science pack passed in; if its greater
        # than 1 stack issue an ItemCapacityWarning
        # Note that this asserts that each lab can only contain 1 stack of each
        # science pack it consumes, which might change in a future Factorio
        # version.

    # =========================================================================

    __hash__ = Entity.__hash__
