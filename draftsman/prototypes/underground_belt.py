# underground_belt.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import IOTypeMixin, DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import underground_belts

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class UndergroundBelt(IOTypeMixin, DirectionalMixin, Entity):
    """
    A transport belt that transfers items underneath other entities.
    """

    class Format(IOTypeMixin.Format, DirectionalMixin.Format, Entity.Format):

        model_config = ConfigDict(title="UndergroundBelt")

    def __init__(
        self,
        name: Optional[str] = get_first(underground_belts),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        io_type: Literal["input", "output"] = "input",
        tags: dict[str, Any] = {},
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        """
        Construct a new underground belt.

        TODO
        """
        # Convert "type" (used by Factorio) into "io_type" (used by Draftsman)
        if "type" in kwargs and io_type == "input":
            io_type = kwargs["type"]

        super().__init__(
            name,
            underground_belts,
            position=position,
            tile_position=tile_position,
            direction=direction,
            io_type=io_type,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
