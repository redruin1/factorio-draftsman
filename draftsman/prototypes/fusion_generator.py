# fusion_generator.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import fusion_generators

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class FusionGenerator(DirectionalMixin, Entity):
    """
    An entity which converts plasma into energy.
    """

    class Format(DirectionalMixin.Format, Entity.Format):
        model_config = ConfigDict(title="FusionGenerator")

    def __init__(
        self,
        name: Optional[str] = get_first(fusion_generators),
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
            fusion_generators,
            position=position,
            tile_position=tile_position,
            direction=direction,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
