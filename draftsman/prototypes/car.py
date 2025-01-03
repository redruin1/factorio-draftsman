# car.py

from draftsman.classes.entity import Entity
from draftsman.classes.exportable import attempt_and_reissue
from draftsman.classes.mixins import (
    VehicleMixin,
    RequestItemsMixin,
    EquipmentGridMixin,
    OrientationMixin,
)
from draftsman.classes.vector import Vector, PrimitiveVector, PrimitiveIntVector
from draftsman.constants import Orientation, ValidationMode
from draftsman.signatures import uint32
from draftsman.utils import get_first

from draftsman.data.entities import cars

from pydantic import ConfigDict, Field
from typing import Any, Literal, Optional, Union


class Car(
    VehicleMixin, EquipmentGridMixin, RequestItemsMixin, OrientationMixin, Entity
):
    """
    A drivable entity which uses wheels or tracks for locomotion.
    """

    class Format(
        VehicleMixin.Format,
        EquipmentGridMixin.Format,
        RequestItemsMixin.Format,
        OrientationMixin.Format,
        Entity.Format,
    ):
        model_config = ConfigDict(title="Car")

    def __init__(
        self,
        name: Optional[str] = get_first(cars),
        position: Union[Vector, PrimitiveVector] = None,
        tile_position: Union[Vector, PrimitiveVector] = (0, 0),
        orientation: Optional[Orientation] = Orientation.NORTH,
        enable_logistics_while_moving: Optional[bool] = True,
        grid: list[Format.EquipmentComponent] = [],
        trunk_inventory=None,
        ammo_inventory=None,
        driver_is_main_gunner: Optional[bool] = True,
        selected_gun_index: Optional[uint32] = 1,  # TODO: size
        items: dict[str, uint32] = {},  # TODO: ItemID
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
            cars,
            position=position,
            tile_position=tile_position,
            orientation=orientation,
            enable_logistics_while_moving=enable_logistics_while_moving,
            grid=grid,
            trunk_inventory=trunk_inventory,
            ammo_inventory=ammo_inventory,
            driver_is_main_gunner=driver_is_main_gunner,
            selected_gun_index=selected_gun_index,
            items=items,
            tags=tags,
            **kwargs
        )

        self.validate_assignment = validate_assignment

    # =========================================================================

    __hash__ = Entity.__hash__
