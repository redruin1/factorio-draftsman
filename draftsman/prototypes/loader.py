# loader.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    FiltersMixin,
    IOTypeMixin,
    EnergySourceMixin,
    DirectionalMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import FilterEntry
from draftsman.utils import fix_incorrect_pre_init

from draftsman.data.entities import loaders

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@fix_incorrect_pre_init
@attrs.define
class Loader(FiltersMixin, IOTypeMixin, EnergySourceMixin, DirectionalMixin, Entity):
    """
    An entity that inserts items directly from a belt to an inventory or
    vise-versa.
    """

    # class Format(
    #     FiltersMixin.Format,
    #     IOTypeMixin.Format,
    #     DirectionalMixin.Format,
    #     Entity.Format,
    # ):
    #     model_config = ConfigDict(title="Loader")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(loaders),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
    #     io_type: Literal["input", "output"] = "input",
    #     filters: list[FilterEntry] = [],
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     super().__init__(
    #         name,
    #         loaders,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         io_type=io_type,
    #         filters=filters,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return loaders

    # =========================================================================

    __hash__ = Entity.__hash__
