# gate.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import gates

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class Gate(DirectionalMixin, Entity):
    """
    A wall that opens near the player.
    """

    class Format(DirectionalMixin.Format, Entity.Format):
        model_config = ConfigDict(title="Gate")

    def __init__(
        self,
        name: Optional[str] = get_first(gates),
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
            gates,
            position=position,
            tile_position=tile_position,
            direction=direction,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
