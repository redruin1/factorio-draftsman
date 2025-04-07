# pipe.py

from draftsman.classes.entity import Entity
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import pipes

import attrs
from typing import Any, Literal, Optional, Union
from pydantic import ConfigDict


@attrs.define
class Pipe(Entity):
    """
    A structure that transports a fluid across a surface.
    """

    class Format(Entity.Format):
        model_config = ConfigDict(title="Pipe")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(pipes),
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
    #         pipes,
    #         position=position,
    #         tile_position=tile_position,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return pipes

    # =========================================================================

    __hash__ = Entity.__hash__
