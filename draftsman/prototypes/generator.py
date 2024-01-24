# generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import get_first
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import generators

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class Generator(DirectionalMixin, Entity):
    """
    An entity that converts a fluid (usually steam) to electricity.
    """

    class Format(DirectionalMixin.Format, Entity.Format):
        model_config = ConfigDict(title="Generator")

    def __init__(
        self,
        name: Optional[str] = get_first(generators),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        validate_assignment: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
        **kwargs
    ):
        super().__init__(
            name,
            generators,
            position=position,
            tile_position=tile_position,
            direction=direction,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    __hash__ = Entity.__hash__
