# fluid_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import OrientationMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import fluid_wagons
from draftsman.data import entities

from pydantic import ConfigDict
from typing import Any, Literal, Union


class FluidWagon(OrientationMixin, Entity):
    """
    A train wagon that holds a fluid as cargo.
    """

    class Format(OrientationMixin.Format, Entity.Format):
        model_config = ConfigDict(title="FluidWagon")

    def __init__(
        self,
        name: str = fluid_wagons[0],
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        orientation: Orientation = Orientation.NORTH,
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
            fluid_wagons,
            position=position,
            tile_position=tile_position,
            orientation=orientation,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

        self.validate(mode=validate).reissue_all(stacklevel=3)

    # =========================================================================

    __hash__ = Entity.__hash__
