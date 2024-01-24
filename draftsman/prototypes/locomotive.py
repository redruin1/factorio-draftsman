# locomotive.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import RequestItemsMixin, ColorMixin, OrientationMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import get_first

from draftsman.data.entities import locomotives

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class Locomotive(RequestItemsMixin, ColorMixin, OrientationMixin, Entity):
    """
    A train car that moves other wagons around using a fuel.
    """

    class Format(
        RequestItemsMixin.Format,
        ColorMixin.Format,
        OrientationMixin.Format,
        Entity.Format,
    ):
        model_config = ConfigDict(title="Locomotive")

    def __init__(
        self,
        name: Optional[str] = get_first(locomotives),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        orientation: Orientation = Orientation.NORTH,
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
        super().__init__(
            name,
            locomotives,
            position=position,
            tile_position=tile_position,
            orientation=orientation,
            items=items,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # TODO: check if item requests are valid fuel sources or not

    # =========================================================================

    __hash__ = Entity.__hash__
