# heat_pipe.py

from draftsman.classes.entity import Entity
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import heat_pipes

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class HeatPipe(Entity):
    """
    An entity used to transfer thermal energy.
    """

    # class Format(Entity.Format):
    #     model_config = ConfigDict(title="HeatPipe")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(heat_pipes),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
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
    #         heat_pipes,
    #         position=position,
    #         tile_position=tile_position,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return heat_pipes

    # =========================================================================

    __hash__ = Entity.__hash__
