# boiler.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import RequestItemsMixin, DirectionalMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Direction, ValidationMode
from draftsman.signatures import uint32
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import boilers

from pydantic import ConfigDict
from typing import Any, Literal, Union


class Boiler(RequestItemsMixin, DirectionalMixin, Entity):
    """
    An entity that uses a fuel to convert a fluid (usually water) to another
    fluid (usually steam).
    """

    class Format(RequestItemsMixin.Format, DirectionalMixin.Format, Entity.Format):
        model_config = ConfigDict(title="Boiler")

    def __init__(
        self,
        name: str = boilers[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        direction: Direction = Direction.NORTH,
        items: dict[str, uint32] = {},  # TODO: ItemID
        tags: dict[str, Any] = {},
        validate: Union[
            ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
        ] = ValidationMode.STRICT,
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
            boilers,
            position=position,
            tile_position=tile_position,
            direction=direction,
            items=items,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # TODO: ensure fuel requests to this entity match it's allowed fuel categories

    # =========================================================================

    __hash__ = Entity.__hash__
