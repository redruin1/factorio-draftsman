# lightning_attractor.py

from draftsman.classes.entity import Entity
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import ValidationMode
from draftsman.utils import get_first

from draftsman.data.entities import lightning_attractors

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class LightningAttractor(Entity):
    """
    An entity that protects an area from lightning strike damage and converts
    their energy for a power grid.
    """

    class Format(Entity.Format):
        model_config = ConfigDict(title="HalfDiagonalRail")

    def __init__(
        self,
        name: Optional[str] = get_first(lightning_attractors),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
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
            lightning_attractors,
            position=position,
            tile_position=tile_position,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    @property
    def similar_entities(self) -> list[str]:
        return lightning_attractors

    # =========================================================================

    __hash__ = Entity.__hash__
