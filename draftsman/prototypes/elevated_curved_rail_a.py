# elevated_curved_rail_a.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, EightWayDirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import elevated_curved_rails_a

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class ElevatedCurvedRailA(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    First set of elevated curved rail entities with 2.0 rails. (TODO)
    """

    # class Format(
    #     DoubleGridAlignedMixin.Format, EightWayDirectionalMixin.Format, Entity.Format
    # ):
    #     model_config = ConfigDict(title="ElevatedCurvedRailA")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(elevated_curved_rails_a),
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
    #         elevated_curved_rails_a,
    #         position=position,
    #         tile_position=tile_position,
    #         direction=direction,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return elevated_curved_rails_a

    # =========================================================================

    __hash__ = Entity.__hash__
