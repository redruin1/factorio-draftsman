# fusion_reactor.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EnergySourceMixin, DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import fusion_reactors

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class FusionReactor(EnergySourceMixin, Entity):
    """
    A reactor which produces hot plasma.
    """

    # class Format(DirectionalMixin.Format, Entity.Format):
    #     model_config = ConfigDict(title="FusionReactor")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(fusion_reactors),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     direction: Direction = Direction.NORTH,
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
    #         fusion_reactors,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return fusion_reactors

    # =========================================================================

    __hash__ = Entity.__hash__
