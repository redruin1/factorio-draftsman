# fluid_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import EquipmentGridMixin, OrientationMixin
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.utils import get_first
from draftsman.warning import DraftsmanWarning

from draftsman.data.entities import fluid_wagons

from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


class FluidWagon(OrientationMixin, Entity):
    """
    A train wagon that holds a fluid as cargo.
    """

    class Format(EquipmentGridMixin.Format, OrientationMixin.Format, Entity.Format):
        model_config = ConfigDict(title="FluidWagon")

    def __init__(
        self,
        name: Optional[str] = get_first(fluid_wagons),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        orientation: Orientation = Orientation.NORTH,
        enable_logistics_while_moving: Optional[bool] = True,
        grid: list[Format.EquipmentComponent] = [],
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
            fluid_wagons,
            position=position,
            tile_position=tile_position,
            orientation=orientation,
            enable_logistics_while_moving=enable_logistics_while_moving,
            grid=grid,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
