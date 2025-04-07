# cargo_wagon.py

from draftsman.classes.entity import Entity
from draftsman.classes.mixins import (
    EquipmentGridMixin,
    RequestItemsMixin,
    InventoryFilterMixin,
    OrientationMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.signatures import ItemRequest
from draftsman.utils import get_first

from draftsman.data.entities import cargo_wagons

import attrs
from pydantic import ConfigDict
from typing import Any, Literal, Optional, Union


@attrs.define
class CargoWagon(
    EquipmentGridMixin,
    RequestItemsMixin,
    InventoryFilterMixin,
    OrientationMixin,
    Entity,
):
    """
    A train wagon that holds items as cargo.
    """

    # class Format(
    #     EquipmentGridMixin.Format,
    #     RequestItemsMixin.Format,
    #     InventoryFilterMixin.Format,
    #     OrientationMixin.Format,
    #     Entity.Format,
    # ):
    #     model_config = ConfigDict(title="CargoWagon")

    # def __init__(
    #     self,
    #     name: Optional[str] = get_first(cargo_wagons),
    #     position: Union[Vector, PrimitiveVector] = None,
    #     tile_position: Union[Vector, PrimitiveVector] = (0, 0),
    #     orientation: Orientation = Orientation.NORTH,
    #     enable_logistics_while_moving: Optional[bool] = True,
    #     grid: list[Format.EquipmentComponent] = [],
    #     items: Optional[list[ItemRequest]] = [],  # TODO: ItemID
    #     inventory: Format.InventoryFilters = {},
    #     tags: dict[str, Any] = {},
    #     validate_assignment: Union[
    #         ValidationMode, Literal["none", "minimum", "strict", "pedantic"]
    #     ] = ValidationMode.STRICT,
    #     **kwargs
    # ):
    #     super().__init__(
    #         name,
    #         cargo_wagons,
    #         position=position,
    #         tile_position=tile_position,
    #         orientation=orientation,
    #         enable_logistics_while_moving=enable_logistics_while_moving,
    #         grid=grid,
    #         items=items,
    #         inventory=inventory,
    #         tags=tags,
    #         **kwargs
    #     )

    #     self.validate_assignment = validate_assignment

    # TODO: check for item requests exceeding cargo capacity

    # =========================================================================

    @property
    def similar_entities(self) -> list[str]:
        return cargo_wagons

    # =========================================================================

    __hash__ = Entity.__hash__
