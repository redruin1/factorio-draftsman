# rail_ramp.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DoubleGridAlignedMixin, EightWayDirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import rail_ramps

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class RailRamp(DoubleGridAlignedMixin, EightWayDirectionalMixin, Entity):
    """
    A ramp which transitions between ground and elevated rails.
    """

    class Format(
        DoubleGridAlignedMixin.Format, EightWayDirectionalMixin.Format, Entity.Format
    ):
        model_config = ConfigDict(title="RailRamp")

    def __init__(
        self,
        name: Optional[str] = get_first(rail_ramps),
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
            rail_ramps,
            position=position,
            tile_position=tile_position,
            direction=direction,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
