# half_diagonal_rail.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, EightWayDirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import half_diagonal_rails

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class HalfDiagonalRail:
    """
    Rail entities which lie halfway inbetween the classic 45 degree diagonals.
    """

    class Format(
        DoubleGridAlignedMixin.Format, EightWayDirectionalMixin.Format, Entity.Format
    ):
        model_config = ConfigDict(title="HalfDiagonalRail")

    def __init__(
        self,
        name: Optional[str] = get_first(half_diagonal_rails),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        TODO
        """

        super().__init__(
            name,
            half_diagonal_rails,
            position=position,
            tile_position=tile_position,
            direction=direction,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return half_diagonal_rails

    # =========================================================================

    __hash__ = Entity.__hash__
